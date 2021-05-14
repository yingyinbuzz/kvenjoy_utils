
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

def glyph_to_json(g):
    """Converts a Glyph object to dict/json struct"""
    o = {}
    o['code'] = g.code
    o['strokes'] = [stroke_to_json(s) for s in g.strokes]
    return o

def glyph_from_json(jo):
    """Converts a dict/json struct to Glyph object"""
    return kvenjoy.gfont.Glyph(jo['code'], [stroke_from_json(s) for s in jo['strokes']])

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
