#!/usr/bin/env python3

from PIL import Image
from tracer.stroke_size import *
from tracer.stroke_repair import *

def is_stroke_grayscale(p):
    return p < 128

def make_stroke_pixel_grayscale():
    return 0

def is_stroke_rgb(p):
    r, g, b = p
    return r < 128 and g < 128 and b < 128

def make_stroke_pixel_rgb():
    return (0, 0, 0)

if __name__ == '__main__':
    import sys
    import os
    for fn in sys.argv[1:]:
        print(fn)
        image = Image.open(fn)
        is_stroke = is_stroke_rgb if image.mode == 'RGB' else is_stroke_grayscale
        make_stroke_pixel = make_stroke_pixel_rgb if image.mode == 'RGB' else make_stroke_pixel_grayscale
        stroke_size = scan_stroke_size(image, is_stroke)
        new_image = repair_strokes(image, stroke_size, is_stroke, make_stroke_pixel)
        new_image.save('{}_repaired.png'.format(os.path.splitext(fn)[0]))
