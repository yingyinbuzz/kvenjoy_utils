#!/usr/bin/env python3

import sys
import PIL.Image

class IntervalTracker:
    def __init__(self):
        self.intervals = {}
        self._last = None

    def track_at(self, position, track):
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

def is_stroke(p):
    return p < 128

for fn in sys.argv[1:]:
    print(fn)
    image = PIL.Image.open(fn)
    w, h = image.size
    print('Size {}x{}'.format(w, h))

    it = IntervalTracker()

    for y in range(h):
        for x in range(w):
            it.track_at(x, is_stroke(image.getpixel((x, y))))
        it.track_at(w, False)

    for x in range(w):
        for y in range(h):
            it.track_at(y, is_stroke(image.getpixel((x, y))))
        it.track_at(h, False)


    for interval, count in sorted(((k, it.intervals[k]) for k in it.intervals), reverse=True, key=lambda p : p[1]):
        print(' {}:{}'.format(interval, count), end='')
    print()
