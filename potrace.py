#!/usr/bin/env python3

from PIL import Image
from potrace.potrace import *

if __name__ == '__main__':
    import sys
    print('Load image')
    img = Image.open(sys.argv[1])
    print('Build matrix')
    cm = build_coord_matrix(img, lambda p : p[0] < 128 and p[1] < 128 and p[2] < 128)
    print('Decompose paths')
    ps = decompose_paths(cm)
