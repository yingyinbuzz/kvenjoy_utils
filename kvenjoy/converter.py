
import kvenjoy.graph

def variable_to_json(var):
    """Converts a Variable object to dict/json struct"""
    o = {}
    o['x'] = var.x
    o['y'] = var.y
    o['name'] = var.name
    return o

def point_to_json(point):
    """Converts a Point/BezierPoint object to dict/json struct"""
    if isinstance(point, kvenjoy.graph.Point):
        return [point.x, point.y]
    elif isinstance(point, kvenjoy.graph.BezierPoint):
        return [point.cx1, point.cy1, point.cx2, point.cy2, point.x, point.y]
    else:
        raise Exception('Unknown point type "{}"'.format(type(point).__name__))

def stroke_to_json(stroke):
    """Converts a Stroke object to dict/json struct"""
    o = {}
    o['points'] = [point_to_json(p) for p in stroke.points]
    return o

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

def glyph_to_json(g):
    o = {}
    o['code'] = g.code
    o['strokes'] = [stroke_to_json(s) for s in g.strokes]
    return o

def gfont_to_json(font):
    """Converts a Gfont object to dict/json struct"""
    o = {}
    o['version'] = font.version
    o['vendor'] = font.vendor
    o['type'] = font.type
    o['name'] = font.name
    o['author'] = font.author
    o['description'] = font.description
    o['boundary'] = font.boundary
    o['password'] = font.password
    o['unknown'] = font.unknown
    o['uuid'] = font.uuid
    o['glyphs'] = [glyph_to_json(g) for g in font.glyphs]
    return o
