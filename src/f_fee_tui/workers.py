from __future__ import annotations

import logging
import pickle
import queue
import threading
import time
import traceback
from queue import Queue
from typing import TYPE_CHECKING

import zmq
from egse.confman import ConfigurationManagerProxy
from egse.dpu.fdpu import FastCameraDPUProxy
from egse.fee.ffee import HousekeepingData
from egse.fee.ffee import aeb_state
from egse.fee.ffee import f_fee_mode
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.setup import load_setup
from egse.zmq import MessageIdentifier
from textual.app import App

from .messages import AebStateChanged
from .messages import CommandThreadCrashed
from .messages import DebModeChanged
from .messages import DtcInModChanged
from .messages import ExceptionCaught
from .messages import LogRetrieved
from .messages import OutbuffChanged
from .messages import ShutdownReached
from .messages import TimeoutReached

if TYPE_CHECKING:
    from .app import FastFEEApp

_LOGGER = logging.getLogger("egse.f-fee-tui")

dpu = Settings.load("DPU Processor")


class Command(threading.Thread):
    def __init__(self, app: App, command_q: Queue) -> None:
        super().__init__()
        self._app = app
        self._command_q = command_q
        self._f_dpu: FastCameraDPUProxy | None = None
        self._cm_cs: ConfigurationManagerProxy | None = None
        self._cancelled = threading.Event()

    def run(self) -> None:

        screen = self._app.get_screen("master")

        # This first loop is needed to make sure the Command thread is not ended when either the FastCameraDPUProxy
        # or the ConfigurationManagerProxy can not connect to their control server. When no connection, we wait for
        # 10 seconds before trying again, unless the app is terminated.

        while True:
            try:
                with FastCameraDPUProxy() as self._f_dpu, ConfigurationManagerProxy() as self._cm_cs:
                    while True:
                        if self._cancelled.is_set():
                            break
                        try:
                            target, command, args, kwargs = self._command_q.get_nowait()
                            self._command_q.task_done()
                            screen.post_message(LogRetrieved(f"Executing command '{command}'"))
                            rc = self.execute_command(target, command, args, kwargs)
                            screen.post_message(LogRetrieved(f"Command '{command}' executed: {rc = }"))
                        except queue.Empty:
                            time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
                            continue
                        except Exception as exc:
                            _LOGGER.error(f"Caught and exception: {exc}")
                            tb = traceback.format_exc()
                            screen.post_message(ExceptionCaught(exc, tb))
            except ConnectionError as exc:
                screen.post_message(CommandThreadCrashed(exc))
            if self.sleep_or_break(10.0):
                break

    def sleep_or_break(self, timeout: float) -> bool:
        """
        Returns True if the App is terminated and the cancelled flag is set, returns False after sleeping
        for the given timeout in seconds. The idea for this function is that when we have a sleep in the
        event loop, we still can terminate the app without having to wait the whole sleep time.
        """
        for _ in range(int(timeout * 10)):
            if self._cancelled.is_set():
                is_cancelled = True
                break
            time.sleep(0.1)
        else:
            is_cancelled = False

        return True if is_cancelled else False

    def cancel(self) -> None:
        self._cancelled.set()

    def execute_command(self, target: str, command: str, args: list, kwargs: dict):

        screen = self._app.get_screen("master")

        if target == "DPU":
            try:
                screen.log.info(f"Running DPU command: {command}({args}, {kwargs})")
                response = getattr(self._f_dpu, command)(*args, **kwargs)
                screen.log.info(f"Response: {response}")
                return response
            except AttributeError as exc:
                screen.log.warning(f"No such command for DPU: {command}", exc_info=True)

        elif target == "CM_CS":
            try:
                screen.log.info(f"Running CM_CS command: {command}({args}, {kwargs})")
                response = getattr(self._cm_cs, command)(*args, **kwargs)
                screen.log.info(f"Response: {response}")
                return response
            except AttributeError as exc:
                screen.log.warning(f"No such command for CM_CS: {command}", exc_info=True)


class Monitor(threading.Thread):
    def __init__(self, app: App) -> None:
        self._app = app
        self._cancelled = threading.Event()
        self._reset_frame_errors = threading.Event()

        self.hostname = dpu.HOSTNAME
        self.port = dpu.DATA_DISTRIBUTION_PORT

        self.previous_deb_mode = f_fee_mode.ON_MODE
        self.previous_aeb_state = {}
        self.accumulated_outbuff = [0, 0, 0, 0, 0, 0, 0, 0]
        """The total number of OUTBUFF errors since it was last reset."""
        self.outbuff_mapping = [0, 2, 1, 3, 4, 6, 5, 7]
        """Mapping of the OUTBUFF_x and the DTC_IN_MOD, see Setup AEB_TO_T_IN_MOD"""

        super().__init__()

    def run(self) -> None:

        start_time = time.monotonic()
        """Starting time for detecting a timeout or a shutdown of the data distribution channel."""
        timeout_reported = False
        """Flag to track if a timeout has been reported or not."""
        shutdown_reported = False
        """Flag to track if a shutdown has been reported or not."""

        context = zmq.Context.instance()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, MessageIdentifier.F_FEE_REGISTER_MAP.to_bytes(1, byteorder='big'))
        receiver.setsockopt(zmq.SUBSCRIBE, MessageIdentifier.SYNC_HK_DATA.to_bytes(1, byteorder='big'))
        receiver.connect(f"tcp://{self.hostname}:{self.port}")

        setup = load_setup()

        screen = self._app.get_screen("master")

        while True:
            if self._cancelled.is_set():
                break
            if self._reset_frame_errors.is_set():
                self._reset_frame_errors.clear()
                self.accumulated_outbuff = [0, 0, 0, 0, 0, 0, 0, 0]
                screen.post_message(OutbuffChanged(self.accumulated_outbuff))

            socket_list, _, _ = zmq.select([receiver], [], [], timeout=0.1)

            if receiver in socket_list:
                start_time = time.monotonic()
                timeout_reported = False
                shutdown_reported = False
                try:
                    sync_id, pickle_string = receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.handle_messages(sync_id, data, setup)
                except Exception as exc:
                    tb = traceback.format_exc()
                    screen.post_message(ExceptionCaught(exc, tb))

            if time.monotonic() - start_time > 6.0 and not timeout_reported:
                screen.post_message(TimeoutReached("Timeout reached after 6s on data distribution channel."))
                timeout_reported = True
            if time.monotonic() - start_time > 10.0 and not shutdown_reported:
                screen.post_message(ShutdownReached("Resetting the monitoring panels after 10s of inactivity."))
                shutdown_reported = True

        receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        receiver.close()

        screen.post_message(LogRetrieved("Monitor Thread finished ..."))
        screen.log.info("Monitor Thread finished ...")

    def cancel(self) -> None:
        self._cancelled.set()

    def reset_frame_errors(self):
        self._reset_frame_errors.set()

    def handle_messages(self, sync_id, data, setup):

        screen = self._app.get_screen("master")

        if sync_id == MessageIdentifier.F_FEE_REGISTER_MAP:

            # How can we be sure the Register Map is properly synchronised with the F-FEE?

            register_map, _ = data
            register_map = RegisterMap("F-FEE", memory_map=register_map, setup=setup)

            t0 = register_map["DEB_DTC_IN_MOD_2", "T0_IN_MOD"]
            t1 = register_map["DEB_DTC_IN_MOD_2", "T1_IN_MOD"]
            t2 = register_map["DEB_DTC_IN_MOD_2", "T2_IN_MOD"]
            t3 = register_map["DEB_DTC_IN_MOD_2", "T3_IN_MOD"]
            t4 = register_map["DEB_DTC_IN_MOD_1", "T4_IN_MOD"]
            t5 = register_map["DEB_DTC_IN_MOD_1", "T5_IN_MOD"]
            t6 = register_map["DEB_DTC_IN_MOD_1", "T6_IN_MOD"]
            t7 = register_map["DEB_DTC_IN_MOD_1", "T7_IN_MOD"]

            screen.log(f"{t0=}, {t1=}, {t2=}, {t3=}, {t4=}, {t5=}, {t6=}, {t7=}")

            screen.post_message(DtcInModChanged(t0, t1, t2, t3, t4, t5, t6, t7))

        elif sync_id == MessageIdentifier.SYNC_HK_DATA:

            cmd, aeb_id, data, timestamp = data

            if cmd == 'command_deb_read_hk':
                hk_data = HousekeepingData("DEB", data, setup)
                deb_mode = f_fee_mode(hk_data["STATUS", "OPER_MOD"])
                screen.log(f"DEB_MODE = {deb_mode.name}")
                screen.post_message(DebModeChanged(deb_mode))
                outbuff = [hk_data["OVF", f"OUTBUFF_{x}"] for x in range(1, 9)]
                # outbuff = random.choices([0, 1], k=8)
                screen.log(f"{outbuff = }")
                if any(outbuff):
                    # re-order outbuff to match with DTC_IN_MOD
                    outbuff = [outbuff[idx] for idx in self.outbuff_mapping]
                    # update the accumulated values for OUTBUFF
                    self.accumulated_outbuff = [x + y for x, y in zip(self.accumulated_outbuff, outbuff)]
                    screen.post_message(OutbuffChanged(self.accumulated_outbuff))
            elif cmd == 'command_aeb_read_hk':
                aeb_id = aeb_id[0]  # this comes from the args, so it's a list
                hk_data = HousekeepingData(aeb_id, data, setup)
                aeb_status = hk_data["STATUS", "AEB_STATUS"]
                screen.log(f"AEB_STATE = {aeb_state(aeb_status).name}")

                # Power is/was handled by the DEB_DTC_AEB_ONOFF state from the DEB register map above.
                # Should I check the AEB_ONOFF from the Register Map? Is there a chance/reason why the AEB_STATE
                # would not match?

                if aeb_status == aeb_state.OFF:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_onoff", False))
                elif aeb_status == aeb_state.INIT:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_init", True))
                elif aeb_status == aeb_state.POWER_UP:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_power_up", True))
                elif aeb_status == aeb_state.POWER_DOWN:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_power_down", True))
                elif aeb_status == aeb_state.CONFIG:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_config", True))
                elif aeb_status == aeb_state.IMAGE:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_image", True))
                elif aeb_status == aeb_state.PATTERN:
                    screen.post_message(AebStateChanged(f"{aeb_id.lower()}_pattern", True))
