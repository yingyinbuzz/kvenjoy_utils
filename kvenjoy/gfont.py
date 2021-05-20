
import io
import zipfile
import kvenjoy.cipher
from kvenjoy.graph import *
from kvenjoy.io import *

class Glyph:
    """Visual representation of a character.

    A glyph has a associated character code (UNICODE) and several Stroke that
    forms the glyph.
    """

    def __init__(self, code, strokes):
        self.code = code
        self.strokes = strokes

    @classmethod
    def load(cls, stm):
        """Construct a Glyph from given input stream.

        For detailed layout of a glyph, please see README.md.

        Arguments:
        stm    -- The input stream.
        return -- New Glyph object constructed from the stream.
        """
        # Read glyph character code
        (code,) = read_short(stm)
        strokes = Stroke.load_list(stm)

        return cls(code, strokes)

    def save(self, stm):
        """ Write a glyph to given stream.

        For detailed layout of a glyph, please see README.md.

        Arguments:
        stm   -- The output stream.
        """
        # Write glyph character code
        write_short(stm, self.code)

        # Write glyphs
        Stroke.save_list(stm, self.strokes)

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

    @classmethod
    def load(cls, stm):
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
        return cls(version, vendor, type, name, author, description, boundary, password, unknown, uuid, glyphs)

    def save(self, stm):
        """Write a font to given input stream.

        For detailed layout of a font, please see README.md.

        Arguments:
        stm  -- The output stream.
        """

        # Write header
        write_int(stm, self.version)
        head_stm = io.BytesIO()
        write_utf_string(head_stm, self.vendor)
        write_int(head_stm, self.type)
        write_utf_string(head_stm, self.name)
        write_utf_string(head_stm, self.author)
        write_utf_string(head_stm, self.description)
        write_int(head_stm, self.boundary)
        write_int(head_stm, len(self.glyphs))
        if self.version >= 2:
            write_utf_string(head_stm, self.password)
        if self.version >= 4:
            write_raw_string(head_stm, self.unknown)
        if self.version >= 7:
            write_utf_string(head_stm, self.uuid)
        head_block = head_stm.getvalue()
        if self.version >= 5:
            head_block = kvenjoy.cipher.encrypt(head_block, Font.key)
        write_int(stm, len(head_block))
        stm.write(head_block)

        # Write some non-zipped glyphs
        # TODO: Find out what exactly these non-zipped glyphs are for.
        write_int(stm, min(30, len(self.glyphs)))
        for g in self.glyphs:
            g.save(stm)

        # Write zipped glyphs
        zstm = io.BytesIO()
        z = zipfile.ZipFile(zstm, mode='w', compression=zipfile.ZIP_DEFLATED)
        for g in self.glyphs:
            gstm = io.BytesIO()
            g.save(gstm)
            z.writestr('{:d}'.format(g.code), gstm.getvalue())
        z.close()
        stm.write(zstm.getvalue())
