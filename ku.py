#!/usr/bin/env python3

from kvenjoy.gfont import *
from kvenjoy.gap import *

def format_point(p):
    if isinstance(p, Point):
        return 'P({}, {})'.format(p.x, p.y)
    elif isinstance(p, BezierPoint):
        return 'B({}, {}, {}, {}, {}, {})'.format(p.cx1, p.cy1, p.cx2, p.cy2, p.x, p.y)
    else:
        raise Exception('Unknown point type "{}"'.format(type(p).__name__))

def dump_gfont(fn, verbose):
    with open(fn, 'rb') as f:
        font = Font.load(f)
        print('File\t\t{}'.format(fn))
        print('Version\t\t{}'.format(font.version))
        print('Vendor\t\t{}'.format(font.vendor))
        print('Name\t\t{}'.format(font.name))
        print('Author\t\t{}'.format(font.author))
        print('Description\t{}'.format(font.description))
        print('Boundary\t{}'.format(font.boundary))
        print('Password\t{}'.format(font.password))
        print('UUID\t\t{}'.format(font.uuid))
        print('# Glyphs\t{}'.format(len(font.glyphs)))
        if verbose:
            for g in font.glyphs:
                print('\tCode=0x{:04x}'.format(g.code))
                for s in g.strokes:
                    print('\t\t{}'.format(', '.join([format_point(p) for p in s.points])))

def dump_gap(fn, verbose):
    with open(fn, 'rb') as f:
        gap = Gap.load(f)
        print('File\t\t{}'.format(fn))
        print('Version\t\t{}'.format(gap.version))
        print('UUID\t\t{}'.format(gap.uuid))
        print('Name\t\t{}'.format(gap.name))
        print('Author\t\t{}'.format(gap.author))
        print('Description\t{}'.format(gap.description))
        print('# Variables\t{}'.format(len(gap.variables)))
        print('# Strokes\t{}'.format(sum([len(sg) for sg in gap.stroke_groups])))
        if verbose:
            for v in gap.variables:
                print('\t{}({}, {})'.format(v.name, v.x, v.y))
            for sg in gap.stroke_groups:
                print('\t--')
                for s in sg:
                    print('\t\t{}'.format(', '.join([format_point(p) for p in s.points])))

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Utility to manipulate Kvenjoy GFONT/GAP file(s)')
    p.add_argument('action', choices=['dump'],
                    help='Action on GFONT/GAP file(s)')
    p.add_argument('gfiles', metavar='GFILE', type=str, nargs='+',
                    help='A GFONT/GAP file')
    p.add_argument('-v', '--verbose', action='store_true',
                    help='Show verbose information')
    args = p.parse_args()
    if args.action == 'dump':
        for fn in args.gfiles:
            with open(fn, 'rb') as f:
                bs = f.read(4)
                (magic,) = struct.unpack_from('>H', bs, 0)
            # GAP file is gzipped so check against GZIP magic would work
            if magic == 0x1f8b:
                dump_gap(fn, args.verbose)
            else:
                dump_gfont(fn, args.verbose)
            print()
