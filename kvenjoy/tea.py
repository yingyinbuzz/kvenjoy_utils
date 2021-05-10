"""
Implements a 16-round [TEA](https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm).
"""
import struct

def encrypt(plain, key):
    """Encrypt given plaintext block (64 bits).

    Both input and output are of type 'bytes' or 'bytearray'.

    Arguments:
    plain  -- Plaintext to be encrypted (64 bits).
    key    -- Encryption key (128 bits).
    return -- Ciphertext (64 bits).
    """
    (x0, x1) = struct.unpack_from('>2I', plain, 0)
    (k0, k1, k2, k3) = struct.unpack_from('>4I', key, 0)
    d = 0x9e3779b9
    s = 0
    for i in range(16):
        s = _m32(s + d)
        x0 = _m32(x0 + _m32((_lshift(x1, 4) + k0) ^ (x1 + s) ^ (_rshift(x1, 5) + k1)))
        x1 = _m32(x1 + _m32((_lshift(x0, 4) + k2) ^ (x0 + s) ^ (_rshift(x0, 5) + k3)))
    bs = bytearray(8)
    struct.pack_into('>2I', bs, 0, x0, x1)
    return bs

def decrypt(cipher, key):
    """Decrypt given ciphertext block (64 bits).

    Both input and output are of type 'bytes' or 'bytearray'.

    Arguments:
    cipher -- Ciphertext to be decrypt (64 bits).
    key    -- Decryption key (128 bits).
    return -- Plaintext (64 bits).
    """
    (x0, x1) = struct.unpack_from('>2I', cipher, 0)
    (k0, k1, k2, k3) = struct.unpack_from('>4I', key, 0)
    d = 0x9e3779b9
    s = _m32(d * 16)
    for i in range(16):
        x1 = _m32(x1 - _m32(_m32(_lshift(x0, 4) + k2) ^ _m32(x0 + s) ^ _m32(_rshift(x0, 5) + k3)))
        x0 = _m32(x0 - _m32(_m32(_lshift(x1, 4) + k0) ^ _m32(x1 + s) ^ _m32(_rshift(x1, 5) + k1)))
        s = _m32(s - d)
    bs = bytearray(8)
    struct.pack_into('>2I', bs, 0, x0, x1)
    return bs

def _m32(x):
    return x & 0xffffffff

def _lshift(x, n):
    return _m32(x << n)

def _rshift(x, n):
    return _m32((x % 0x100000000) >> n)
