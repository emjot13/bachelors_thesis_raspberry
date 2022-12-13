from threading import Timer
from datetime import datetime

class RepeatedTimer(object):
    def __init__(self, interval, function, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.kwargs = kwargs
        # self.data       = data
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        date = datetime.now().replace(microsecond=0)
        self.kwargs["data"]["time"] = date
        self.function(**self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False