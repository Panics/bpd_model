from datetime import datetime

class TimeKeeper:

    _startTime:datetime

    def ElapsedTimeInSeconds(self) -> float:
        return (datetime.now() - self._startTime).total_seconds()

    def __init__(self):
        self._startTime = datetime.now()
