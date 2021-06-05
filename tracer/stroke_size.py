
from math import sqrt
from tracer.utils import IntervalTracker

def scan_stroke_size(image, is_stroke):
    """Scan an grayscale image to detect glyph stroke size.
    Arguments:
    image   - The PIL image object to be scanned.
    is_stoke - A callable object to check whether a given pixel is stroke or not.
    return - Detected stroke size.
    """
    w, h = image.size
    it = IntervalTracker()

    # Scan vertically
    for y in range(h):
        for x in range(w):
            it.track_at(x, is_stroke(image.getpixel((x, y))))
        it.track_at(w, False)

    # Scan horizontally
    for x in range(w):
        for y in range(h):
            it.track_at(y, is_stroke(image.getpixel((x, y))))
        it.track_at(h, False)

    # Scan diaggonally
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

    # Scan diaggonally
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

    sizes = sorted(((k, it.intervals[k]) for k in it.intervals), reverse=True, key=lambda p : p[1])
    return sizes[0][0] if sizes else None
