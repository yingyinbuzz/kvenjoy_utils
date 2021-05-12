
import io
import zipfile
import kvenjoy.cipher
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

class Glyph:
    """Visual representation of a character.

    A glyph has a associated character code (UNICODE) and several Stroke that
    forms the glyph.
    """

    def __init__(self, code, strokes):
        self.code = code
        self.strokes = strokes

    @staticmethod
    def load(stm):
        """Construct a Glyph from given input stream

        For detailed layout of a glyph, please see README.md.

        Arguments:
        stm    -- The input stream.
        return -- New Glyph object constructed from the stream.
        """

        # Read glyph character code
        (code,) = read_short(stm)

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

        return Glyph(code, strokes)

    @staticmethod
    def save(stm, glyph):
        """ Write a glyph to given stream.

        For detailed layout of a glyph, please see README.md.

        Arguments:
        stm   -- The output stream.
        glyph -- The glyph to be written.
        """

        # Rebuild coordinate and command buffer
        floats = []
        cmds = []
        for stroke in glyph.strokes:
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

        # Write glyph character code
        write_short(stm, glyph.code)

        # Write coordinates buffer
        write_int(stm, len(floats))
        for f in floats:
            write_float(stm, f)
        write_int(stm, len(cmds))
        for c in cmds:
            write_byte(stm, c)

class Font:
    """Represents a font.

    A font is a collection of Glyph instances.
    """
    def __init__(self, version, vendor, type, name, author, description, boundary, password, unknown, uuid, glyphs):
        self.version = version
        self.vendor = vendor
        self.type = type
        self.name = name
        self.author = author
        self.description = description
        self.boundary = boundary
        self.password = password
        self.unknown = unknown
        self.uuid = uuid
        self.glyphs = glyphs

    # Font file encryption/decryption key
    key = bytes([1, 9, 8, 9, 0, 8, 2, 6, 1, 9, 9, 2, 0, 8, 2, 8])

    @staticmethod
    def load(stm):
        """Construct a font from given input stream.

        For detailed layout of a font, please see README.md.

        Arguments:
        stm    -- The input stream.
        return -- A new Font object.
        """
        # Load font header fields
        (version,) = read_int(stm)
        (header_size,) = read_int(stm)
        header_block = stm.read(header_size)
        if version >= 5:
            header_block = kvenjoy.cipher.decrypt(header_block, Font.key)
        header_stm = io.BytesIO(header_block)
        (vendor,) = read_utf_string(header_stm)
        (type,) = read_int(header_stm)
        (name,) = read_utf_string(header_stm)
        (author,) = read_utf_string(header_stm)
        (description,) = read_utf_string(header_stm)
        (boundary,) = read_int(header_stm)
        (num_glyphs,) = read_int(header_stm)
        password = None
        unknown = None
        uuid = None
        if version >= 2:
            (password,) = read_utf_string(header_stm)
        if version >= 4:
            (unknown,) = read_raw_string(header_stm)
        if version >= 7:
            (uuid,) = read_utf_string(header_stm)

        # Read and ignore non-zipped glyphs (at most 30)
        # TODO: Find out what exactly these non-zipped glyphs are for.
        (num_non_zipped_glyphs,) = read_int(stm)
        for i in range(num_non_zipped_glyphs):
            g = Glyph.load(stm)

        # Load zipped glyphs
        z = zipfile.ZipFile(stm)
        glyphs = []
        for zfn in z.namelist():
            zstm = io.BytesIO(z.read(zfn))
            g = Glyph.load(zstm)
            glyphs.append(g)

        # Construct font
        return Font(version, vendor, type, name, author, description, boundary, password, unknown, uuid, glyphs)

    @staticmethod
    def save(stm, font):
        """Write a font to given input stream.

        For detailed layout of a font, please see README.md.

        Arguments:
        stm  -- The output stream.
        font -- The font to be written.
        """

        # Write header
        write_int(stm, font.version)
        head_stm = io.BytesIO()
        write_utf_string(head_stm, font.vendor)
        write_int(head_stm, font.type)
        write_utf_string(head_stm, font.name)
        write_utf_string(head_stm, font.author)
        write_utf_string(head_stm, font.description)
        write_int(head_stm, font.boundary)
        write_int(head_stm, len(font.glyphs))
        if font.version >= 2:
            write_utf_string(head_stm, font.password)
        if font.version >= 4:
            write_raw_string(head_stm, font.unknown)
        if font.version >= 7:
            write_utf_string(head_stm, font.uuid)
        head_block = head_stm.getvalue()
        if font.version >= 5:
            head_block = kvenjoy.cipher.encrypt(head_block, Font.key)
        write_int(stm, len(head_block))
        stm.write(head_block)

        # Write some non-zipped glyphs
        # TODO: Find out what exactly these non-zipped glyphs are for.
        num_glyph = min(30, len(font.glyphs))
        write_int(stm, num_glyph)
        for i in range(num_glyph):
            Glyph.save(stm, font.glyphs[i])

        # Write zipped glyphs
        zstm = io.BytesIO()
        z = zipfile.ZipFile(zstm, mode='w', compression=zipfile.ZIP_DEFLATED)
        for g in font.glyphs:
            gstm = io.BytesIO()
            Glyph.save(gstm, g)
            z.writestr('{:d}'.format(g.code), gstm.getvalue())
        z.close()
        stm.write(zstm.getvalue())
