
from kvenjoy.io import *

class Point:
    """A 2D point with x, y coordinates"""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def bounding_box(self):
        """Calculate bounding box that could just hold this point
        """
        return (self.x, self.y, self.x, self.y)

class BezierPoint:
    """A Bezier point with two extra control points"""

    def __init__(self, cx1, cy1, cx2, cy2, x, y):
        self.cx1 = float(cx1)
        self.cy1 = float(cy1)
        self.cx2 = float(cx2)
        self.cy2 = float(cy2)
        self.x = float(x)
        self.y = float(y)

    def bounding_box(self):
        """Calculate bounding box that could just hold this Bezier point
        """
        return (min(self.cx1, self.cx2, self.x),
                min(self.cy1, self.cy2, self.y),
                max(self.cx1, self.cx2, self.x),
                max(self.cy1, self.cy2, self.y))


class Stroke:
    """Represents a continuous mark (path).

    A stroke contains a list of several Point or BezierPoint instances, from
    start point to end point of the path.
    """

    def __init__(self, points):
        self.points = points

    @classmethod
    def load_list(cls, stm):
        """Construct list of Stroke from given input stream.

        For detailed layout of strokes, please see README.md.

        Arguments:
        stm    -- The input stream.
        return -- List of Stroke objects constructed from the stream.
        """
        # Read coordinates buffer
        (num_floats,) = read_int(stm)
        floats = list(read_float(stm, num_floats))

        # Read command buffer
        (num_cmds,) = read_int(stm)
        cmds = list(read_byte(stm, num_cmds))

        # Construct strokes from command and coordinates buffer
        strokes = []
        points = []
        pi = 0
        for cmd in cmds:
            if cmd == 0:
                # Start a new stroke
                if points:
                    strokes.append(cls(points))
                    points = []
                points.append(Point(floats[pi], floats[pi + 1]))
                pi += 2
            elif cmd == 1:
                # Append a point to current stroke
                points.append(Point(floats[pi], floats[pi + 1]))
                pi += 2
            elif cmd == 2:
                # Append a Bezier point to current stroke
                points.append(BezierPoint(floats[pi], floats[pi + 1], floats[pi + 2], floats[pi + 3], floats[pi + 4], floats[pi + 5]))
                pi += 6
            else:
                raise Exception('Unknown glyph command "0x{:02x}"'.format(cmd))
        # Append last stroke (if there's any)
        if points:
            strokes.append(cls(points))

        return strokes

    @staticmethod
    def save_list(stm, strokes):
        """Write list of Stroke to given output stream.

        For detailed layout of strokes, please see README.md.

        Arguments:
        stm    -- The output stream.
        return -- List of Stroke objects to be written to the stream.
        """
        # Rebuild coordinate and command buffer
        floats = []
        cmds = []
        for stroke in strokes:
            cmds.append(0)
            floats.append(stroke.points[0].x)
            floats.append(stroke.points[0].y)
            for p in stroke.points[1:]:
                if isinstance(p, Point):
                    cmds.append(1)
                    floats.append(p.x)
                    floats.append(p.y)
                elif isinstance(p, BezierPoint):
                    cmds.append(2)
                    floats.append(p.cx1)
                    floats.append(p.cy1)
                    floats.append(p.cx2)
                    floats.append(p.cy2)
                    floats.append(p.x)
                    floats.append(p.y)
                else:
                    raise Exception('Unknown point type "{}"'.format(type(p).__name__))

        # Write coordinates buffer
        write_int(stm, len(floats))
        for f in floats:
            write_float(stm, f)
        write_int(stm, len(cmds))
        for c in cmds:
            write_byte(stm, c)
