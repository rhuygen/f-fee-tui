import pickle
import random
import threading
import time
import traceback

import zmq
from egse.fee.ffee import f_fee_mode
from egse.reg import RegisterMap
from egse.settings import Settings
from egse.zmq import MessageIdentifier
from textual.message import Message

dpu = Settings.load("DPU Processor")


class DebModeChanged(Message):
    def __init__(self, deb_mode: int):
        super().__init__()
        self.deb_mode = deb_mode


class ExceptionCaught(Message):
    def __init__(self, exc: Exception, tb=None):
        super().__init__()
        self.exc = exc
        self.tb = tb


class TimeoutReached(Message):
    """This message is sent when the Monitor reached a timeout on the data distribution channel."""


class Monitor(threading.Thread):
    def __init__(self, app: "FastFEEApp") -> None:
        self._app = app
        self._canceled = threading.Event()
        self.hostname = dpu.HOSTNAME
        self.port = dpu.DATA_DISTRIBUTION_PORT
        super().__init__()

    def run(self) -> None:

        n_timeouts = 0
        """The timeout is 1s, we count the number of timeouts to detect if the DPU or N-FEE might be dead or stalled."""

        context = zmq.Context.instance()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        receiver.connect(f"tcp://{self.hostname}:{self.port}")

        while True:
            if self._canceled.is_set():
                break

            socket_list, _, _ = zmq.select([receiver], [], [], timeout=1.0)

            if receiver in socket_list:
                n_timeouts = 0
                try:
                    sync_id, pickle_string = receiver.recv_multipart()
                    sync_id = int.from_bytes(sync_id, byteorder='big')
                    data = pickle.loads(pickle_string)
                    self.handle_messages(sync_id, data)
                except Exception as exc:
                    tb = traceback.format_exc()
                    self._app.post_message(ExceptionCaught(exc, tb))

            if len(socket_list) == 0:
                n_timeouts += 1
                if n_timeouts > 3:  # at least a timecode should arrive every 2.5s
                    self._app.post_message(TimeoutReached())
                    n_timeouts = 0

        receiver.disconnect(f"tcp://{self.hostname}:{self.port}")
        receiver.close()

    # Change the name of this function to run() if you just want tp see a simulation
    # of changing LEDs
    def run_sim(self) -> None:
        prev_deb_mode = 0

        while True:
            if self._canceled.is_set():
                return

            if prev_deb_mode == (deb_mode := random.choice([0, 1, 2, 3, 6, 7])):
                continue
            else:
                prev_deb_mode = deb_mode

            self._app.post_message(DebModeChanged(deb_mode))

            time.sleep(0.1)

    def cancel(self) -> None:
        self._canceled.set()

    def handle_messages(self, sync_id, data):

        if sync_id == MessageIdentifier.F_FEE_REGISTER_MAP:
            register_map, _ = data
            register_map = RegisterMap("F-FEE", memory_map=register_map)

            deb_mode = f_fee_mode(register_map["DEB_DTC_FEE_MOD", "OPER_MOD"])

            self._app.post_message(DebModeChanged(deb_mode))
