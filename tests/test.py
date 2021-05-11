import unittest
import random
import kvenjoy.tea
import kvenjoy.cipher

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

if __name__ == '__main__':
    unittest.main(),
