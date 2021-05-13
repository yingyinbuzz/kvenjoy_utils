
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

    @staticmethod
    def load(stm):
        """Construct a variable from given input stream.

        Arguments:
        stm    -- The input stream.
        return -- The constructed Variable object.
        """
        (x, y) = read_float(stm, 2)
        (name,) = read_utf_string(stm)
        return Variable(x, y, name)

    @staticmethod
    def save(stm, variable):
        """Write a variable to given output stream.

        Arguments:
        stm      -- The output stream.
        variable -- The Variable object to be written.
        """
        write_float(stm, variable.x, variable.y)
        write_utf_string(stm, variable.name)

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

    @staticmethod
    def load(stm):
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

        return Gap(version, uuid, name, author, description, variables, stroke_groups)

    def save(stm, gap):
        """Write a GAP object to given output stream.

        Arguments:
        stm    -- The output stream.
        return -- GAP object to be written input stream.
        """
        zstm = io.BytesIO()
        write_int(zstm, gap.version)
        write_utf_string(zstm, gap.uuid, gap.name, gap.author, gap.description)
        write_int(zstm, len(gap.variables))
        for v in gap.variables:
            Variable.save(zstm, v)
        write_int(zstm, len(gap.stroke_groups))
        for g in gap.stroke_groups:
            kvenjoy.graph.Stroke.save_list(zstm, g)
        stm.write(gzip.compress(zstm.getvalue()))
