
import kvenjoy.gap
import kvenjoy.gfont
from kvenjoy.graph import *

def variable_to_json(var):
    """Converts a Variable object to dict/json struct"""
    o = {}
    o['x'] = var.x
    o['y'] = var.y
    o['name'] = var.name
    return o

def variable_from_json(jo):
    """Converts a dict/json struct to a Variable object"""
    return kvenjoy.gap.Variable(jo['x'], jo['y'], jo['name'])

def variable_to_svg(var):
    """Converts a Variable object to SVG element"""
    return ['<text x="{}" y="{}" font-size="16px" font-family="serif" text-anchor="middle" fill="#ff0000">{}</text>'.format(var.x, var.y, var.name)]

def point_to_json(point):
    """Converts a Point/BezierPoint object to dict/json struct"""
    if isinstance(point, Point):
        return [point.x, point.y]
    elif isinstance(point, BezierPoint):
        return [point.cx1, point.cy1, point.cx2, point.cy2, point.x, point.y]
    else:
        raise Exception('Unknown point type "{}"'.format(type(point).__name__))

def point_from_json(jo):
    """Converts a dict/json struct to Point/BezierPoint object"""
    if len(jo) == 2:
        return Point(jo[0], jo[1])
    elif len(jo) == 6:
        return BezierPoint(jo[0], jo[1], jo[2], jo[3], jo[4], jo[5])
    else:
        raise Exception('Wrong point coordinates length "{}"'.format(len(jo)))

def stroke_to_json(stroke):
    """Converts a Stroke object to dict/json struct"""
    o = {}
    o['points'] = [point_to_json(p) for p in stroke.points]
    return o

def stroke_from_json(jo):
    """Converts a dict/json struct to Stroke object"""
    return Stroke([point_from_json(x) for x in jo['points']])

def stroke_to_svg(stroke):
    """Converts a Stroke object to SVG element"""
    o = '<path d="'
    o += ' M {} {}'.format(stroke.points[0].x, stroke.points[0].y)
    for p in stroke.points[1:]:
        if isinstance(p, Point):
            o += ' L {} {}'.format(p.x, p.y)
        elif isinstance(p, BezierPoint):
            o += ' C {} {}, {} {}, {} {}'.format(p.cx1, p.cy1, p.cx2, p.cy2, p.x, p.y)
        else:
            raise Exception('Unknown point type "{}"'.format(type(p).__name__))
    o += '" stroke="black" fill="transparent" vector-effect="non-scaling-stroke"/>'
    return [o]

def gap_to_json(gap):
    """Converts a Gap object to dict/json struct"""
    o = {}
    o['version'] = gap.version
    o['name'] = gap.name
    o['uuid'] = gap.uuid
    o['author'] = gap.author
    o['description'] = gap.description
    o['variables'] = [variable_to_json(v) for v in gap.variables]
    o['stroke_groups'] = [[stroke_to_json(s) for s in sg] for sg in gap.stroke_groups]
    return o

def gap_from_json(jo):
    """Converts a dict/json struct to Gap object"""
    return kvenjoy.gap.Gap(jo['version'], jo['uuid'], jo['name'], jo['author'], jo['description'],
                           [variable_from_json(x) for x in jo['variables']],
                           [[stroke_from_json(s) for s in sg] for sg in jo['stroke_groups']])

def gap_to_svg(gap, standalone=True):
    """Converts a Gap object to SVG elements"""
    o = []
    if standalone:
        (x0, y0, x1, y1) = gap.bounding_box()
        px = (x1 - x0) / 10
        py = (y1 - y0) / 20
        vw = (x1 - x0) + 2 * px
        vh = (y1 - y0) + 2 * py
        vx = x0 - px
        vy = y0 - py
        o.append('<svg version="1.1" viewBox="{} {} {} {}" baseProfile="full" xmlns="http://www.w3.org/2000/svg">'.format(vx, vy, vw, vh))
    for v in gap.variables:
        o.extend(variable_to_svg(v))
    for sg in gap.stroke_groups:
        for s in sg:
            o.extend(stroke_to_svg(s))
    if standalone:
        o.append('</svg>')
    return o

def glyph_to_json(g):
    """Converts a Glyph object to dict/json struct"""
    o = {}
    o['code'] = g.code
    o['strokes'] = [stroke_to_json(s) for s in g.strokes]
    return o

def glyph_from_json(jo):
    """Converts a dict/json struct to Glyph object"""
    return kvenjoy.gfont.Glyph(jo['code'], [stroke_from_json(s) for s in jo['strokes']])

def glyph_to_svg(g, transform=None):
    """Converts a Glyph object to SVG elements"""
    o = []
    if transform is None:
        o.append('<g>')
    else:
        o.append('<g transform="{}">'.format(transform))
    o.append('<title>{:04x}</title>'.format(g.code))
    for s in g.strokes:
        o.extend(stroke_to_svg(s))
    o.append('</g>')
    return o

def gfont_to_json(font):
    """Converts a Font object to dict/json struct"""
    o = {}
    o['version'] = font.version
    o['vendor'] = font.vendor
    o['type'] = font.type
    o['name'] = font.name
    o['author'] = font.author
    o['description'] = font.description
    o['boundary'] = font.boundary
    o['password'] = font.password
    o['unknown'] = [b for b in font.unknown]
    o['uuid'] = font.uuid
    o['glyphs'] = [glyph_to_json(g) for g in font.glyphs]
    return o

def gfont_from_json(jo):
    """Converts a dict/json struct to a Font object"""
    return kvenjoy.gfont.Font(jo['version'], jo['vendor'], jo['type'],
                              jo['name'], jo['author'], jo['description'],
                              jo['boundary'], jo['password'], bytes(jo['unknown']), jo['uuid'],
                              [glyph_from_json(g) for g in jo['glyphs']])

def gfont_to_svg(font, standalone=True):
    """Converts a Font object to SVG elements"""
    o = []
    n_cols = 16
    n_rows = len(font.glyphs) // n_cols + (1 if len(font.glyphs) % n_cols else 0)
    cell_w = 64
    cell_h = 64
    cell_base_x = cell_w / 2
    cell_base_y = cell_h * 3 / 4
    scale_x = cell_w / font.boundary
    scale_y = cell_h / font.boundary
    if standalone:
        (x0, y0, x1, y1) = (0, 0, cell_w * n_cols, cell_h * n_rows)
        px = max((x1 - x0) / 10, 20)
        py = max((y1 - y0) / 20, 20)
        vw = (x1 - x0) + 2 * px
        vh = (y1 - y0) + 2 * py
        vx = x0 - px
        vy = y0 - py
        # o.append('<svg version="1.1" viewBox="{} {} {} {}" baseProfile="full" xmlns="http://www.w3.org/2000/svg">'.format(vx, vy, vw, vh))
        o.append('<svg version="1.1" width="{}" height="{}" baseProfile="full" xmlns="http://www.w3.org/2000/svg">'.format(vw, vh))
    i = 0
    for g in font.glyphs:
        row = i // n_cols
        col = i % n_cols
        transform = 'translate({}, {}) scale({} {})'.format(col * cell_w + cell_base_x, row * cell_h + cell_base_y, scale_x, scale_y)
        o.extend(glyph_to_svg(g, transform=transform))
        i += 1
    if standalone:
        o.append('</svg>')
    return o
