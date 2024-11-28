from queue import Queue
from queue import Empty


class ClearableQueue(Queue):
    """Add the possibility to clear the queue."""
    def clear(self):
        msg = []
        try:
            while True:
                msg.append(str(self.get_nowait()))
                self.task_done()
        except Empty:
            pass
        finally:
            if msg:
                print("Queue not empty at exit:")
                print("\n".join(msg))
