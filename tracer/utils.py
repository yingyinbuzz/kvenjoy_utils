
class IntervalTracker:
    """Tracks intervals.

    Track intervals, result will be put in 'intervals' member which is a map of
    individual intervals and corresponding counts.
    """
    def __init__(self):
        self.intervals = {}
        self._last = None

    def track_at(self, position, track):
        """Track interval.

        Arguments:
        position    -- Current position(numeric type)
        track       -- Tracking or stop tracking(boolean type)
        """
        if track:
            if self._last is None:
                self._last = position
        else:
            if self._last is not None:
                x = position - self._last
                if x < 0:
                    raise Exception('{} {}'.format(self._last, position))
                if x in self.intervals:
                    self.intervals[x] += 1
                else:
                    self.intervals[x] = 1
                self._last = None
