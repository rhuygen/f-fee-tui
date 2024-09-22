import pickle
import time
from typing import Tuple

import zmq
from egse.zmq import MessageIdentifier


def log_message(app, name, sync_id, message, timed_out: bool):
    # app.log(f"{name:10s} {'' if sync_id is None else MessageIdentifier(sync_id).name}, {'🔴' if timed_out else '🟢'}")
    ...


services = {
    'cm_cs': {
        'description': "The Configuration Control Server",
        'hostname': 'localhost',
        'port': 6001,
        'type': zmq.SUB,
        'multipart': False,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    'sm_cs': {
        'description': "The Storage Manager",
        'hostname': 'localhost',
        'port': 6101,
        'type': zmq.SUB,
        'multipart': False,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    'pm_cs': {
        'description': "The Process Manager",
        'hostname': 'localhost',
        'port': 6201,
        'type': zmq.SUB,
        'multipart': False,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    'syn_cs': {
        'description': "The Synoptics Control Server storing generic and device independent housekeeping.",
        'hostname': 'localhost',
        'port': 6205,
        'type': zmq.SUB,
        'multipart': False,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    # The data dumper sends out a STATUS sync_id every second (because the timeout of the Poller is set to 1000ms).
    "data_dump": {
        'description': "The Data Dumper for F-CAM SpaceWire data.",
        'hostname': 'localhost',
        'port': 30304,  # MONITORING_PORT
        'type': zmq.SUB,
        'subscribe': MessageIdentifier.STATUS.to_bytes(1, byteorder='big'),
        'multipart': True,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    "dpu_cs": {
        'description': "The DPU Processor",
        'hostname': 'localhost',
        'port': 6601,  # MONITORING_PORT
        'type': zmq.SUB,
        'multipart': False,
        'sock': None,
        'interval': 3,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
    # Monitor DATA_DISTRIBUTION port, this data is sent out by the Data Processor,
    # Subscribe to the SYNC_TIMECODE which is sent out every 2.5s for the F-CAM. Other sync identifiers are ignored.
    "data": {
        'description': "The Data Distribution by the Data Processor",
        'hostname': 'localhost',
        'port': 30103,  # DATA_DISTRIBUTION_PORT
        'type': zmq.SUB,
        'subscribe': MessageIdentifier.SYNC_TIMECODE.to_bytes(1, byteorder='big'),
        'multipart': True,
        'sock': None,
        'interval': 5,
        'last_received': time.monotonic(),
        'timed-out': False,
        'callback': log_message
    },
}


async def handle_multi_part(sock: zmq.Socket, message_id: bytes) -> Tuple[int, list]:
    message_parts = []
    message_id = int.from_bytes(message_id, byteorder='big')
    while True:
        part = await sock.recv()
        message_parts.append(pickle.loads(part))
        if not sock.getsockopt(zmq.RCVMORE):
            break

    return message_id, message_parts


async def handle_single_part(sock: zmq.Socket, message: bytes) -> Tuple[int, list]:
    message_id = MessageIdentifier.ALL
    response = pickle.loads(message)

    return message_id, [response]
