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

def export_gap(fn):
    with open(fn, 'rb') as f:
        gap = Gap.load(f)
    with open('{}.svg'.format(fn), 'w') as f:
        (x0, y0, x1, y1) = gap.bounding_box()
        px = (x1 - x0) / 10
        py = (y1 - y0) / 20
        vw = (x1 - x0) + 2 * px
        vh = (y1 - y0) + 2 * py
        vx = x0 - px
        vy = y0 - py
        print('<svg version="1.1" viewBox="{} {} {} {}" baseProfile="full" xmlns="http://www.w3.org/2000/svg">'.format(vx, vy, vw, vh), file=f)
        for v in gap.variables:
            print('<text x="{}" y="{}" dominant-baseline="auto" text-anchor="middle" fill="#ff0000">{}</text>'.format(v.x, v.y, v.name), file=f)
        for sg in gap.stroke_groups:
            for s in sg:
                print('<path d="', file=f, end='')
                print(' M {} {}'.format(s.points[0].x, s.points[0].y), file=f, end='')
                for p in s.points[1:]:
                    if isinstance(p, BezierPoint):
                        print(' C {} {}, {} {}, {} {}'.format(p.cx1, p.cy1, p.cx2, p.cy2, p.x, p.y), file=f, end='')
                    else:
                        print(' L {} {}'.format(p.x, p.y), file=f, end='')
                print('" stroke="black" fill="transparent"/>', file=f)
        print('</svg>', file=f)

def export_gfont(fn):
    raise Exception('GFONT export has not been supported yet.')

def file_type(fn):
    with open(fn, 'rb') as f:
        bs = f.read(4)
        (magic,) = struct.unpack_from('>H', bs, 0)
    # GAP file is gzipped so check against GZIP magic would work
    if magic == 0x1f8b:
        return 'gap'
    return 'gfont'

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Utility to manipulate Kvenjoy GFONT/GAP file(s)')
    p.add_argument('action', choices=['dump', 'export'],
                    help='Action on GFONT/GAP file(s)')
    p.add_argument('gfiles', metavar='GFILE', type=str, nargs='+',
                    help='A GFONT/GAP file')
    p.add_argument('-v', '--verbose', action='store_true',
                    help='Show verbose information')
    args = p.parse_args()
    if args.action == 'dump':
        for fn in args.gfiles:
            if file_type(fn) == 'gap':
                dump_gap(fn, args.verbose)
            else:
                dump_gfont(fn, args.verbose)
            print()
    elif args.action == 'export':
        for fn in args.gfiles:
            if file_type(fn) == 'gap':
                export_gap(fn)
            else:
                export_gfont(fn)
