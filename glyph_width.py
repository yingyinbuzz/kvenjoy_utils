#!/usr/bin/env python3

import sys
from PIL import Image
from tracer.stroke_size import *

def is_stroke(p):
    return p < 128

for fn in sys.argv[1:]:
    print(fn)
    image = Image.open(fn)
    print('Stroke size = {}'.format(scan_stroke_size(image, is_stroke)))

