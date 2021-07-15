#!/usr/bin/env python3

from PIL import Image
from potrace.potrace import *

def make_dict(key_tuple, value_tuple):
    if len(key_tuple) != len(value_tuple):
        raise Exception('Tuple sizes not match: "{}" vs "{}"'.format(key_tuple, value_tuple))
    o = {}
    for i in range(len(key_tuple)):
        o[key_tuple[i]] = value_tuple[i]
    return o

def extract_dict(key_tuple, d):
    if len(key_tuple) != len(d):
        raise Exception('Tuple sizes not match: "{}" vs "{}"'.format(key_tuple, d))
    return tuple(d[x] for x in key_tuple)

if __name__ == '__main__':
    import sys
    import json
    print('Load image')
    img = Image.open(sys.argv[1])
    print('Build matrix')
    cm = build_coord_matrix(img, lambda p : p[0] < 192 and p[1] < 192 and p[2] < 192)

    # print('Decompose paths')
    # ps = decompose_paths(cm)
    # print('Total {} paths'.format(len(ps)))
    # jo = [[make_dict(('x', 'y', 'dx', 'dy'), p) for p in path] for path in ps]
    # print(json.dumps(jo, indent=4))

    with open(sys.argv[2]) as f:
        paths = json.load(f)
    areas = []
    for p in paths:
        a = path_area(cm, [extract_dict(('x', 'y', 'dx', 'dy'), point) for point in p])
        areas.append((a, p))
    print(json.dumps(areas, indent=4))
