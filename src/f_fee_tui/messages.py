from textual.message import Message


class DebModeChanged(Message):
    """This message is sent when the Monitor detects a change in the DEB mode."""
    def __init__(self, deb_mode: int):
        super().__init__()
        self.deb_mode = deb_mode


class AebStateChanged(Message):
    """This message reports on the State of the AEBs."""
    def __init__(self, aeb_state_type, aeb_state):
        super().__init__()
        self.aeb_state_type = aeb_state_type
        self.aeb_state = aeb_state


class DtcInModChanged(Message):
    """This message reports on the State of the AEBs."""
    def __init__(self, t0, t1, t2, t3, t4, t5, t6, t7):
        super().__init__()
        self.t0 = t0
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.t4 = t4
        self.t5 = t5
        self.t6 = t6
        self.t7 = t7


class OutbuffChanged(Message):
    def __init__(self, outbuff):
        super().__init__()
        self.outbuff = outbuff


class ExceptionCaught(Message):
    """This message is sent whenever a non-resolvable exception occurs in the Monitor or Commanding thread."""
    def __init__(self, exc: Exception, tb=None):
        super().__init__()
        self.exc = exc
        self.tb = tb


class TimeoutReached(Message):
    """This message is sent when the Monitor or Commanding thread reached a timeout."""
    def __init__(self, msg: str):
        super().__init__()
        self.message = msg


class ShutdownReached(Message):
    """This message is sent when the Monitoring reached a timeout for 5s."""
    def __init__(self, msg: str):
        super().__init__()
        self.message = msg


class ProblemDetected(Message):
    """A notification message for a problem that needs reporting."""
    def __init__(self, msg: str):
        super().__init__()
        self.message = msg


class CommandThreadCrashed(Message):
    """The Command Thread caught an Exception and finished."""
    def __init__(self, exc: Exception):
        super().__init__()
        self.exc = exc


class LogRetrieved(Message):
    """A notification with general information."""
    def __init__(self, msg: str):
        super().__init__()
        self.message = msg
