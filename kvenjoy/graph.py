
from kvenjoy.io import *

class Point:
    """A 2D point with x, y coordinates"""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

class BezierPoint:
    """A Bezier point with two extra control points"""

    def __init__(self, cx1, cy1, cx2, cy2, x, y):
        self.cx1 = float(cx1)
        self.cy1 = float(cy1)
        self.cx2 = float(cx2)
        self.cy2 = float(cy2)
        self.x = float(x)
        self.y = float(y)

class Stroke:
    """Represents a continuous mark (path).

    A stroke contains a list of several Point or BezierPoint instances, from
    start point to end point of the path.
    """

    def __init__(self, points):
        self.points = points

    @staticmethod
    def load_list(stm):
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
                    strokes.append(Stroke(points))
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
            strokes.append(Stroke(points))

        return strokes
