#!/usr/bin/env python3

import sys
from PIL import Image
from math import sqrt

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
    image = Image.open(fn)
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

    if w > h:
        for x in range(w + h):
            sx = min(x, w - 1)
            for y in range(max(0, x - w), min(h, x)):
                it.track_at(round(y * sqrt(2)), is_stroke(image.getpixel((sx, y))))
                sx -= 1
            it.track_at(round(min(h, x) * sqrt(2)), False)
    else:
        for y in range(h + w):
            sy = min(y, h - 1)
            for x in range(max(0, y - h), min(w, y)):
                it.track_at(round(x * sqrt(2)), is_stroke(image.getpixel((x, sy))))
                sy -= 1
            it.track_at(round(min(w, y) * sqrt(2)), False)

    if w > h:
        for x in range(-h, w):
            sx = max(0, x)
            for y in range(max(0, -x), min(h, w - x)):
                it.track_at(round(y * sqrt(2)), is_stroke(image.getpixel((sx, y))))
                sx += 1
            it.track_at(round(min(h, w - x) * sqrt(2)), False)
    else:
        for y in range(-w, h):
            sy = max(0, y)
            for x in range(max(0, -y), min(w, h - y)):
                it.track_at(round(x * sqrt(2)), is_stroke(image.getpixel((x, sy))))
                sy += 1
            it.track_at(round(min(w, h - y) * sqrt(2)), False)

    for interval, count in sorted(((k, it.intervals[k]) for k in it.intervals), reverse=True, key=lambda p : p[1]):
        print(' {}:{}'.format(interval, count), end='')
    print()
