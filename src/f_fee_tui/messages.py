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


class ProblemDetected(Message):
    """A notification message for a problem that needs reporting."""
    def __init__(self, msg: str,):
        super().__init__()
        self.message = msg
