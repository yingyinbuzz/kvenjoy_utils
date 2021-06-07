#!/usr/bin/env python3

import sys
from PIL import Image
from tracer.stroke_size import *

def is_stroke_grayscale(p):
    return p < 128

def is_stroke_rgb(p):
    r, g, b = p
    return r < 128 and g < 128 and b < 128

for fn in sys.argv[1:]:
    print(fn)
    image = Image.open(fn)
    print('Stroke size = {}'.format(scan_stroke_size(image, is_stroke_rgb if image.mode == 'RGB' else is_stroke_grayscale)))

