#!/usr/bin/env python3

import re
import json
from kvenjoy.gfont import *
from kvenjoy.gap import *
from kvenjoy.converter import *

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

def export_gap_to_svg(gap, ofn):
    svg = gap_to_svg(gap)
    with open(ofn, 'w') as f:
        f.writelines(svg)

def export_gap_to_json(gap, ofn):
    jo = gap_to_json(gap)
    with open(ofn, 'w') as f:
        f.write(json.dumps(jo, indent=4))

def export_gap(fn, fmt, ofn):
    with open(fn, 'rb') as f:
        gap = Gap.load(f)
    if fmt == 'svg':
        export_gap_to_svg(gap, ofn)
    elif fmt == 'json':
        export_gap_to_json(gap, ofn)

def export_gfont_to_svg(font, ofn):
    svg = gfont_to_svg(font)
    with open(ofn, 'w') as f:
        f.writelines(svg)

def export_gfont_to_json(font, ofn):
    jo = gfont_to_json(font)
    with open(ofn, 'w') as f:
        f.write(json.dumps(jo, indent=4))

def export_gfont(fn, fmt, ofn):
    with open(fn, 'rb') as f:
        font = Font.load(f)
    if fmt == 'svg':
        export_gfont_to_svg(font, ofn)
    elif fmt == 'json':
        export_gfont_to_json(font, ofn)

def import_gap_from_svg(ifn):
    raise Exception('Import GAP from SVG not supported yet')

def import_gap_from_json(ifn):
    with open(ifn) as f:
        jo = json.load(f)
    return gap_from_json(jo)

def import_gap(fn, fmt, ifn):
    if fmt == 'svg':
        gap = import_gap_from_svg(ifn)
    elif fmt == 'json':
        gap = import_gap_from_json(ifn)
    with open(fn, 'wb') as f:
        Gap.save(f, gap)

def import_gfont_from_svg(ifn):
    raise Exception('Import GFONT from SVG not supported yet')

def import_gfont_from_json(ifn):
    with open(ifn) as f:
        jo = json.load(f)
    return gfont_from_json(jo)

def import_gfont(fn, fmt, ifn):
    if fmt == 'svg':
        font = import_gfont_from_svg(ifn)
    elif fmt == 'json':
        font = import_gfont_from_json(ifn)
    with open(fn, 'wb') as f:
        Font.save(f, font)

def file_type(fn):
    # Check extension name first
    if re.search(r'\.gap$', fn):
        return 'gap'
    if re.search(r'\.gfont$', fn):
        return 'gfont'

    # Check file content
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
    p.add_argument('-v', '--verbose', action='store_true',
                    help='Show verbose information')
    sp = p.add_subparsers(dest='command')

    p_dump = sp.add_parser('dump', description='Dump GFONT/GAP files(s)')
    p_dump.add_argument('gfiles', metavar='GFILE', type=str, nargs='+',
                        help='A GFONT/GAP file')

    p_export = sp.add_parser('export', description='Export a GFONT/GAP file')
    p_export.add_argument('-f', '--format', choices=['svg', 'json'],
                          help='Ouput format')
    p_export.add_argument('-o', '--output', metavar='OUTPUT', required=True,
                          help='Ouput file')
    p_export.add_argument('gfile', metavar='GFILE', type=str,
                          help='A GFONT/GAP file')

    p_import = sp.add_parser('import', description='Import a GFONT/GAP file')
    p_import.add_argument('-f', '--format', choices=['svg', 'json'],
                          help='Input format')
    p_import.add_argument('-i', '--input', metavar='INPUT', required=True,
                          help='Input file')
    p_import.add_argument('gfile', metavar='GFILE', type=str,
                          help='A GFONT/GAP file')

    args = p.parse_args()

    if args.command == 'dump':
        for fn in args.gfiles:
            if file_type(fn) == 'gap':
                dump_gap(fn, args.verbose)
            else:
                dump_gfont(fn, args.verbose)
            print()
    elif args.command == 'export':
        if file_type(args.gfile) == 'gap':
            export_gap(args.gfile, args.format, args.output)
        else:
            export_gfont(args.gfile, args.format, args.output)
    elif args.command == 'import':
        if file_type(args.gfile) == 'gap':
            import_gap(args.gfile, args.format, args.input)
        else:
            import_gfont(args.gfile, args.format, args.input)
