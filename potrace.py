#!/usr/bin/env python3

from PIL import Image
from potrace.potrace import *

if __name__ == '__main__':
    import sys
    import json
    print('Load image')
    img = Image.open(sys.argv[1])
    print('Build matrix')
    cm = build_coord_matrix(img, lambda p : p[0] < 192 and p[1] < 192 and p[2] < 192)
    print('Decompose paths')
    ps = decompose_paths(cm)
    print('Total {} paths'.format(len(ps)))
    jo = [[{'x':p[0], 'y':p[1]} for p in path] for path in ps]
    print(json.dumps(jo, indent=4))
