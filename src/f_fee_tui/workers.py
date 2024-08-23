import random
import threading
import time

from textual.message import Message


class DebModeChanged(Message):
    def __init__(self, deb_mode: int):
        super().__init__()
        self.deb_mode = deb_mode


class Monitor(threading.Thread):
    def __init__(self, app: "FastFEEApp") -> None:
        self._app = app
        self._canceled = threading.Event()
        super().__init__()

    def run(self) -> None:

        while True:
            if self._canceled.is_set():
                return

            deb_mode = random.choice([0, 1, 2, 3, 6, 7])

            self._app.post_message(DebModeChanged(deb_mode))

            time.sleep(2.0)

    def cancel(self) -> None:
        self._canceled.set()
