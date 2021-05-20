
import io
import gzip
import kvenjoy.graph
from kvenjoy.io import *

class Variable:
    """Representa a variable.

    A variable has a X/Y coordinates and a name.
    """
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

    @classmethod
    def load(cls, stm):
        """Construct a variable from given input stream.

        Arguments:
        stm    -- The input stream.
        return -- The constructed Variable object.
        """
        (x, y) = read_float(stm, 2)
        (name,) = read_utf_string(stm)
        return cls(x, y, name)

    def save(self, stm):
        """Write a variable to given output stream.

        Arguments:
        stm      -- The output stream.
        """
        write_float(stm, self.x, self.y)
        write_utf_string(stm, self.name)

class Gap:
    """Represent a GAP file.

    A GAP file is a collection of stroke groups and variables.
    """
    def __init__(self, version, uuid, name, author, description, variables, stroke_groups):
        self.version = version
        self.uuid = uuid
        self.name = name
        self.author = author
        self.description = description
        self.variables = variables
        self.stroke_groups = stroke_groups

    def bounding_box(self):
        """Calculate bounding box that could just hold this gap

        Arguments:
        return -- (x0, y0, x1, y1) Left top and right bottom coordinates of the bounding box.
        """
        (x0, y0, x1, y1) = (None, None, None, None)
        for v in self.variables:
                if x0 is None or x0 > v.x:
                    x0 = v.x
                if y0 is None or y0 > v.y:
                    y0 = v.y
                if x1 is None or x1 < v.x:
                    x1 = v.x
                if y1 is None or y1 < v.y:
                    y1 = v.y
        for sg in self.stroke_groups:
            for s in sg:
                for p in s.points:
                    (px0, py0, px1, py1) = p.bounding_box()
                    if x0 is None or x0 > px0:
                        x0 = px0
                    if y0 is None or y0 > py0:
                        y0 = py0
                    if x1 is None or x1 < px1:
                        x1 = px1
                    if y1 is None or y1 < py1:
                        y1 = py1
        return (x0, y0, x1, y1)

    @classmethod
    def load(cls, stm):
        """Construct a GAP object from given input stream.

        Arguments:
        stm    -- The input stream.
        return -- GAP object constructed from input stream.
        """
        bs = gzip.decompress(stm.read())
        zstm = io.BytesIO(bs)
        (version,) = read_int(zstm)
        (uuid, name, author, description) = read_utf_string(zstm, 4)
        (num_vars,) = read_int(zstm)
        variables = [Variable.load(zstm) for i in range(num_vars)]
        (num_groups,) = read_int(zstm)
        stroke_groups = [kvenjoy.graph.Stroke.load_list(zstm) for i in range(num_groups)]

        return cls(version, uuid, name, author, description, variables, stroke_groups)

    def save(self, stm):
        """Write a GAP object to given output stream.

        Arguments:
        stm    -- The output stream.
        """
        zstm = io.BytesIO()
        write_int(zstm, self.version)
        write_utf_string(zstm, self.uuid, self.name, self.author, self.description)
        write_int(zstm, len(self.variables))
        for v in self.variables:
            v.save(zstm)
        write_int(zstm, len(self.stroke_groups))
        for g in self.stroke_groups:
            kvenjoy.graph.Stroke.save_list(zstm, g)
        stm.write(gzip.compress(zstm.getvalue()))
