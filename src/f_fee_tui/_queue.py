from queue import Queue
from queue import Empty

class ClearableQueue(Queue):
    """Add the possibility to clear the queue."""
    def clear(self):
        try:
            msg = []
            while True:
                msg.append(str(self.get_nowait()))
                self.task_done()
        except Empty:
            pass
        if msg:
            print("Queue not empty at exit:")
            print("\n".join(msg))
