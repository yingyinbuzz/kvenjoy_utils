"""
Implements a cipher that encrypts/decrypts a given buffer of arbitrary size.
"""
import random
import kvenjoy.tea

def encrypt(plain, key):
    """Encrypt given plaintext buffer.

    Both input and output are of type 'bytes' or 'bytearray'.

    Arguments:
    plain  -- Plaintext to be encrypted.
    key    -- Encryption key (128 bits).
    return -- Ciphertext.
    """
    plain_buf = bytearray()

    # Prepend indicator and random salts
    plain_size = len(plain) + 10
    padding_size = plain_size % 8
    if padding_size != 0:
        padding_size = 8 - padding_size
    plain_size += padding_size
    plain_buf.append(0x20 | padding_size)
    plain_buf.extend([_random() for i in range(padding_size)])
    for i in range(2):
        plain_buf.append(_random())

    # Append plaintext
    plain_buf.extend(plain)

    # Append trailing zero paddings
    plain_buf.extend([0] * (plain_size - len(plain_buf)))

    # Encrypt each block
    cipher = bytearray()
    lcb = bytearray([0] * 8)
    lpb = bytearray([0] * 8)
    for i in range(len(plain_buf) // 8):
        pb = plain_buf[i * 8:i * 8 + 8]
        cpb = _xor(pb, lcb, 8)
        lcb = kvenjoy.tea.encrypt(cpb, key)
        lcb = _xor(lcb, lpb, 8)
        cipher.extend(lcb)
        lpb = cpb
    return cipher

def decrypt(cipher, key):
    """Decrypt given ciphertext buffer.

    Both input and output are of type 'bytes' or 'bytearray'.

    Arguments:
    cipher -- Ciphertext to be decrypt.
    key    -- Decryption key (128 bits).
    return -- Plaintext.
    """
    lpb = bytearray([0] * 8)
    lcb = bytearray([0] * 8)
    plain = bytearray()
    for i in range(len(cipher) // 8):
        cb = cipher[i * 8:i * 8 + 8]
        ccb = _xor(cb, lpb, 8)
        lpb = kvenjoy.tea.decrypt(ccb, key)
        plain.extend(_xor(lpb, lcb, 8))
        lcb = cb
    padding_size = plain[0] & 0x07
    plain_size = len(cipher) - 10 - padding_size
    return plain[3 + padding_size:3 + padding_size + plain_size]

def _random():
    """Make a random number in range [50, 128)"""
    return 50 + random.randint(0, 77)

def _xor(bs1, bs2, n):
    """Return exclusive or of two given byte arrays"""
    bs = bytearray(n)
    for i in range(n):
        bs[i] = bs1[i] ^ bs2[i]
    return bs
