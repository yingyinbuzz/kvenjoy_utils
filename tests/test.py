import unittest
import kvenjoy.tea

class TestTEA(unittest.TestCase):
    def test_encryption(self):
        plain = bytes([2, 0, 0, 9, 0, 2, 1, 6])
        key = bytes([1, 9, 8, 9, 0, 8, 2, 6, 1, 9, 9, 2, 0, 8, 2, 8])
        cipher = kvenjoy.tea.encrypt(plain, key)
        self.assertEqual(cipher, bytes([0xc8, 0x7f, 0x39, 0xd5, 0xca, 0xed, 0x8c, 0x0b]))

    def test_decryption(self):
        cipher = bytes([0xc8, 0x7f, 0x39, 0xd5, 0xca, 0xed, 0x8c, 0x0b])
        key = bytes([1, 9, 8, 9, 0, 8, 2, 6, 1, 9, 9, 2, 0, 8, 2, 8])
        plain = kvenjoy.tea.decrypt(cipher, key)
        self.assertEqual(plain, bytes([2, 0, 0, 9, 0, 2, 1, 6]))

if __name__ == '__main__':
    unittest.main()
