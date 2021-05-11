import unittest
import random
import io
import kvenjoy.tea
import kvenjoy.cipher
import kvenjoy.io

class TestTEA(unittest.TestCase):
    plain = bytes([2, 0, 0, 9, 0, 2, 1, 6])
    key = bytes([1, 9, 8, 9, 0, 8, 2, 6, 1, 9, 9, 2, 0, 8, 2, 8])
    cipher = bytes([0xc8, 0x7f, 0x39, 0xd5, 0xca, 0xed, 0x8c, 0x0b])

    def test_encryption(self):
        c = kvenjoy.tea.encrypt(TestTEA.plain, TestTEA.key)
        self.assertEqual(c, TestTEA.cipher)

    def test_decryption(self):
        p = kvenjoy.tea.decrypt(TestTEA.cipher, TestTEA.key)
        self.assertEqual(p, TestTEA.plain)

class TestCipher(unittest.TestCase):
    key = bytes([1, 9, 8, 9, 0, 8, 2, 6, 1, 9, 9, 2, 0, 8, 2, 8])

    def test_encryption_and_decryption(self):
        for i in range(32):
            plain = bytes([random.randint(0, 255) for x in range(i)])
            c = kvenjoy.cipher.encrypt(plain, TestCipher.key)
            p = kvenjoy.cipher.decrypt(c, TestCipher.key)
            self.assertEqual(','.join([' {:02x}'.format(x) for x in p]),
                             ','.join([' {:02x}'.format(x) for x in plain]))

class TestIO(unittest.TestCase):
    def test_read_byte(self):
        stm = io.BytesIO(bytes(range(16)))
        bs = kvenjoy.io.read_byte(stm, 16)
        self.assertEqual(bs, (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f))

    def test_write_byte(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_byte(stm, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f)
        stm.seek(0)
        self.assertEqual(stm.read(), bytes(range(16)))

    def test_read_short(self):
        stm = io.BytesIO(bytes(range(16)))
        shorts = kvenjoy.io.read_short(stm, 8)
        self.assertEqual(shorts, (0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f))

    def test_write_short(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_short(stm, 0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f)
        stm.seek(0)
        self.assertEqual(stm.read(), bytes(range(16)))

    def test_read_int(self):
        stm = io.BytesIO(bytes(range(16)))
        ints = kvenjoy.io.read_int(stm, 4)
        self.assertEqual(ints, (0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f))

    def test_write_int(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_int(stm, 0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f)
        stm.seek(0)
        self.assertEqual(stm.read(), bytes(range(16)))

    def test_read_float(self):
        stm = io.BytesIO(bytes([0x44, 0xf7, 0x40, 0x00, 0x44, 0xf7, 0xa0, 0x00, 0x44, 0xf9, 0xe0, 0x00, 0x44, 0xfa, 0x20, 0x00]))
        floats = kvenjoy.io.read_float(stm, 4)
        self.assertEqual(floats, (1978, 1981, 1999, 2001))

    def test_write_float(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_float(stm, 1978, 1981, 1999, 2001)
        stm.seek(0)
        self.assertEqual(stm.read(),bytes([0x44, 0xf7, 0x40, 0x00, 0x44, 0xf7, 0xa0, 0x00, 0x44, 0xf9, 0xe0, 0x00, 0x44, 0xfa, 0x20, 0x00]))

    def test_read_utf_string(self):
        stm = io.BytesIO(bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0x59, 0x41, 0x4e, 0x47]))
        strings = kvenjoy.io.read_utf_string(stm, 2)
        self.assertEqual(strings, ('YIN', 'YANG'))

    def test_write_utf_string(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_utf_string(stm, 'YIN', 'YANG')
        stm.seek(0)
        self.assertEqual(stm.read(), bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0x59, 0x41, 0x4e, 0x47]))

    def test_read_raw_string(self):
        stm = io.BytesIO(bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0xed, 0x41, 0x4e, 0x47]))
        strings = kvenjoy.io.read_raw_string(stm, 2)
        self.assertEqual(strings, (b'YIN', b'\xedANG'))

    def test_write_raw_string(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_raw_string(stm, b'YIN', b'\xedANG')
        stm.seek(0)
        self.assertEqual(stm.read(), bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0xed, 0x41, 0x4e, 0x47]))

if __name__ == '__main__':
    unittest.main(),
