"""
Stream input/output wrappers.

Byte order is big endian.
"""
import struct

def read_byte(stm, count = 1):
    """Read byte(s) from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of bytes to be read.
    """
    return _read(stm, '>{}B'.format(count))

def read_short(stm, count = 1):
    """Read half word(s) from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of half words to be read.
    """
    return _read(stm, '>{}H'.format(count))

def read_int(stm, count = 1):
    """Read integer(s) from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of integers to be read.
    """
    return _read(stm, '>{}I'.format(count))

def read_float(stm, count = 1):
    """Read float(s) from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of floats to be read.
    """
    return _read(stm, '>{}f'.format(count))

def read_c_string(stm, count = 1):
    """Read NULL terminated C strings from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of strings to be read.
    """
    ss = []
    for _ in range(count):
        bs = bytearray()
        (b,) = read_byte(stm)
        while b != 0:
            bs.append(b)
            (b,) = read_byte(stm)
        ss.append(bs.decode('utf-8'))
    return tuple(ss)

def read_utf_string(stm, count = 1):
    """Read UTF-8 encoded string(s) from stream.

    NOTE: Java modified UTF-8 encoding is not supported.

    Arguments:
    stm   -- Input stream.
    count -- Number of strings to be read.
    """
    ss = []
    for i in range(count):
        (size,) = read_short(stm)
        bs = stm.read(size)
        ss.append(bs.decode('utf-8'))
    return tuple(ss)

def read_raw_string(stm, count = 1):
    """Read raw string(s) from stream.

    Arguments:
    stm   -- Input stream.
    count -- Number of strings to be read.
    """
    ss = []
    for i in range(count):
        (size,) = read_short(stm)
        bs = stm.read(size)
        ss.append(bs)
    return tuple(ss)

def write_byte(stm, *args):
    """Write byte(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Bytes to be written.
    """
    _write(stm, '>{}B'.format(len(args)), *args)

def write_short(stm, *args):
    """Write half word(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Half words to be written.
    """
    _write(stm, '>{}H'.format(len(args)), *args)

def write_int(stm, *args):
    """Write integer(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Integers to be written.
    """
    _write(stm, '>{}I'.format(len(args)), *args)

def write_float(stm, *args):
    """Write float(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Floats to be written.
    """
    _write(stm, '>{}f'.format(len(args)), *args)

def write_c_string(stm, *args):
    """Write NULL terminated string(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Strings to be written.
    """
    bs_null = bytearray([0])
    for s in args:
        bs = s.encode('utf-8')
        stm.write(bs)
        stm.write(bs_null)

def write_utf_string(stm, *args):
    """Write UTF-8 encoded string(s) to stream.

    NOTE: Java modified UTF-8 encoding is not supported.

    Arguments:
    stm   -- Output stream.
    *args -- Strings to be written.
    """
    for s in args:
        bs = s.encode('utf-8')
        write_short(stm, len(bs))
        stm.write(bs)

def write_raw_string(stm, *args):
    """Write raw string(s) to stream.

    Arguments:
    stm   -- Output stream.
    *args -- Strings to be written.
    """
    for bs in args:
        write_short(stm, len(bs))
        stm.write(bs)

def _read(stm, fmt):
    bs = stm.read(struct.calcsize(fmt))
    return struct.unpack_from(fmt, bs, 0)

def _write(stm, fmt, *args):
    bs = bytearray(struct.calcsize(fmt))
    struct.pack_into(fmt, bs, 0, *args)
    stm.write(bs)
