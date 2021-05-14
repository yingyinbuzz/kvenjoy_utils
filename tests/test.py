import unittest
import random
import io
import kvenjoy.tea
import kvenjoy.cipher
import kvenjoy.io
from kvenjoy.gfont import *
from kvenjoy.gap import *
from kvenjoy.converter import *

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
        self.assertEqual(stm.getvalue(), bytes(range(16)))

    def test_read_short(self):
        stm = io.BytesIO(bytes(range(16)))
        shorts = kvenjoy.io.read_short(stm, 8)
        self.assertEqual(shorts, (0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f))

    def test_write_short(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_short(stm, 0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f)
        self.assertEqual(stm.getvalue(), bytes(range(16)))

    def test_read_int(self):
        stm = io.BytesIO(bytes(range(16)))
        ints = kvenjoy.io.read_int(stm, 4)
        self.assertEqual(ints, (0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f))

    def test_write_int(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_int(stm, 0x00010203, 0x04050607, 0x08090a0b, 0x0c0d0e0f)
        self.assertEqual(stm.getvalue(), bytes(range(16)))

    def test_read_float(self):
        stm = io.BytesIO(bytes([0x44, 0xf7, 0x40, 0x00, 0x44, 0xf7, 0xa0, 0x00, 0x44, 0xf9, 0xe0, 0x00, 0x44, 0xfa, 0x20, 0x00]))
        floats = kvenjoy.io.read_float(stm, 4)
        self.assertEqual(floats, (1978, 1981, 1999, 2001))

    def test_write_float(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_float(stm, 1978, 1981, 1999, 2001)
        self.assertEqual(stm.getvalue(),bytes([0x44, 0xf7, 0x40, 0x00, 0x44, 0xf7, 0xa0, 0x00, 0x44, 0xf9, 0xe0, 0x00, 0x44, 0xfa, 0x20, 0x00]))

    def test_read_utf_string(self):
        stm = io.BytesIO(bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0x59, 0x41, 0x4e, 0x47]))
        strings = kvenjoy.io.read_utf_string(stm, 2)
        self.assertEqual(strings, ('YIN', 'YANG'))

    def test_write_utf_string(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_utf_string(stm, 'YIN', 'YANG')
        self.assertEqual(stm.getvalue(), bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0x59, 0x41, 0x4e, 0x47]))

    def test_read_raw_string(self):
        stm = io.BytesIO(bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0xed, 0x41, 0x4e, 0x47]))
        strings = kvenjoy.io.read_raw_string(stm, 2)
        self.assertEqual(strings, (b'YIN', b'\xedANG'))

    def test_write_raw_string(self):
        stm = io.BytesIO(bytearray())
        kvenjoy.io.write_raw_string(stm, b'YIN', b'\xedANG')
        self.assertEqual(stm.getvalue(), bytes([0x00, 0x03, 0x59, 0x49, 0x4e, 0x00, 0x04, 0xed, 0x41, 0x4e, 0x47]))

class TestGFont(unittest.TestCase):
    def test_load(self):
        gfont_content = bytes([
            0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x70, 0x44, 0x62, 0x13, 0x7e, 0x0e, 0xd6, 0x64, 0x3f,
            0x50, 0xf6, 0x03, 0x3a, 0xd0, 0xd0, 0x44, 0x12, 0xe6, 0x79, 0xb7, 0x23, 0x45, 0xb1, 0x4a, 0x5c,
            0x55, 0x5b, 0x68, 0x51, 0x17, 0x91, 0x57, 0xe0, 0x6e, 0x7b, 0x7c, 0x98, 0xb0, 0xec, 0x64, 0x00,
            0x01, 0x07, 0x59, 0x97, 0xf3, 0xf5, 0x28, 0x6e, 0xff, 0xc8, 0x55, 0x62, 0x22, 0xa1, 0x9b, 0xf7,
            0xee, 0xdd, 0x4a, 0x3a, 0xc4, 0x7a, 0xa8, 0xcc, 0xd7, 0x73, 0xfe, 0x66, 0x44, 0xef, 0x04, 0x0d,
            0x64, 0x5d, 0x76, 0x4c, 0xa0, 0xb2, 0x22, 0xbc, 0x6a, 0x39, 0x6f, 0x5a, 0x8f, 0xf0, 0xe8, 0x07,
            0xa0, 0x60, 0x9d, 0xa0, 0x2a, 0xba, 0xab, 0x8a, 0xf7, 0xe8, 0xef, 0xdf, 0x92, 0xea, 0x9a, 0x28,
            0x06, 0xae, 0x1c, 0x29, 0xa3, 0x78, 0x17, 0x67, 0x00, 0x00, 0x00, 0x02, 0x00, 0x21, 0x00, 0x00,
            0x00, 0x08, 0xbe, 0xff, 0xff, 0xfe, 0xc2, 0x94, 0x00, 0x00, 0xc1, 0xab, 0xff, 0xff, 0xc2, 0x36,
            0x00, 0x02, 0xc2, 0x3b, 0xff, 0xff, 0xc2, 0xbf, 0x00, 0x00, 0xc2, 0x79, 0xff, 0xfe, 0xc2, 0x8f,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x02, 0x00, 0x22, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00,
            0x00, 0x00, 0xc2, 0x98, 0x00, 0x00, 0xc2, 0x45, 0xff, 0xfe, 0xc2, 0x97, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x02, 0x00, 0x01, 0x50, 0x4b, 0x03, 0x04, 0x14, 0x00, 0x08, 0x08, 0x08, 0x00, 0x5a, 0x4b,
            0xac, 0x52, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00,
            0x00, 0x00, 0x33, 0x33, 0x63, 0x50, 0x64, 0x60, 0x60, 0xe0, 0xd8, 0xf7, 0xff, 0xff, 0xbf, 0x43,
            0x53, 0x18, 0x18, 0x0e, 0xae, 0xfe, 0xff, 0xff, 0x90, 0x19, 0x03, 0xd3, 0x21, 0x6b, 0x20, 0xbd,
            0x9f, 0x81, 0xe1, 0x50, 0x25, 0x50, 0xbc, 0x9f, 0x01, 0x04, 0x98, 0x18, 0x98, 0x00, 0x50, 0x4b,
            0x07, 0x08, 0x7b, 0x0d, 0x8f, 0xd5, 0x2a, 0x00, 0x00, 0x00, 0x2c, 0x00, 0x00, 0x00, 0x50, 0x4b,
            0x03, 0x04, 0x14, 0x00, 0x08, 0x08, 0x08, 0x00, 0x5a, 0x4b, 0xac, 0x52, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x33, 0x34, 0x63, 0x50,
            0x62, 0x60, 0x60, 0x60, 0x01, 0x62, 0x86, 0x43, 0x33, 0x80, 0xd8, 0xf5, 0xff, 0xbf, 0x43, 0xd3,
            0x41, 0x3c, 0x06, 0x26, 0x06, 0x46, 0x00, 0x50, 0x4b, 0x07, 0x08, 0xa1, 0x80, 0xb5, 0x73, 0x19,
            0x00, 0x00, 0x00, 0x1c, 0x00, 0x00, 0x00, 0x50, 0x4b, 0x01, 0x02, 0x14, 0x00, 0x14, 0x00, 0x08,
            0x08, 0x08, 0x00, 0x5a, 0x4b, 0xac, 0x52, 0x7b, 0x0d, 0x8f, 0xd5, 0x2a, 0x00, 0x00, 0x00, 0x2c,
            0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x33, 0x50, 0x4b, 0x01, 0x02, 0x14, 0x00, 0x14, 0x00, 0x08,
            0x08, 0x08, 0x00, 0x5a, 0x4b, 0xac, 0x52, 0xa1, 0x80, 0xb5, 0x73, 0x19, 0x00, 0x00, 0x00, 0x1c,
            0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x5a, 0x00, 0x00, 0x00, 0x33, 0x34, 0x50, 0x4b, 0x05, 0x06, 0x00, 0x00, 0x00, 0x00, 0x02,
            0x00, 0x02, 0x00, 0x60, 0x00, 0x00, 0x00, 0xa3, 0x00, 0x00, 0x00, 0x00, 0x00])
        stm = io.BytesIO(gfont_content)
        font = Font.load(stm)
        self.assertEqual(font.version, 7)
        self.assertEqual(font.vendor, 'kvenjoy')
        self.assertEqual(font.type, 1)
        self.assertEqual(font.name, 'Test')
        self.assertEqual(font.author, 'Author')
        self.assertEqual(font.description, 'Description')
        self.assertEqual(font.boundary, 300)
        self.assertEqual(font.password, 'pASSWORD')
        self.assertEqual(font.unknown, b'')
        self.assertEqual(font.uuid, '379865e6-84d8-4310-b227-45249f5afb44')
        self.assertEqual(len(font.glyphs), 2)

        g = font.glyphs[0]
        self.assertEqual(len(g.strokes), 1)
        s = g.strokes[0]
        self.assertEqual(len(s.points), 2)
        self.assertIsInstance(s.points[0], Point)
        self.assertEqual(s.points[0].x, -0.4999999403953552)
        self.assertEqual(s.points[0].y, -74.0)
        self.assertIsInstance(s.points[1], BezierPoint)
        self.assertEqual(s.points[1].cx1, -21.499998092651367)
        self.assertEqual(s.points[1].cy1, -45.50000762939453)
        self.assertEqual(s.points[1].cx2, -46.999996185302734)
        self.assertEqual(s.points[1].cy2, -95.5)
        self.assertEqual(s.points[1].x, -62.49999237060547)
        self.assertEqual(s.points[1].y, -71.5)

        g = font.glyphs[1]
        self.assertEqual(len(g.strokes), 1)
        s = g.strokes[0]
        self.assertEqual(len(s.points), 2)
        self.assertIsInstance(s.points[0], Point)
        self.assertEqual(s.points[0].x, 0.0)
        self.assertEqual(s.points[0].y, -76.0)
        self.assertIsInstance(s.points[1], Point)
        self.assertEqual(s.points[1].x, -49.49999237060547)
        self.assertEqual(s.points[1].y, -75.5)

    def test_save(self):
        version = 7
        vendor = 'kvenjoy'
        type = 1
        name = 'Test'
        author = 'Author'
        description = 'Description'
        boundary = 300
        password = 'pASSWORD'
        unknown = b''
        uuid = '379865e6-84d8-4310-b227-45249f5afb44'
        glyphs = list((
            Glyph(
                0x21,
                [
                    Stroke([
                        Point(-0.4999999403953552, -74.0),
                        BezierPoint(
                            -21.499998092651367, -45.50000762939453,
                            -46.999996185302734, -95.5,
                            -62.49999237060547, -71.5)
                        ])
                ]),
            Glyph(
                0x22,
                [
                    Stroke([
                        Point(0.0, -76.0),
                        Point(-49.49999237060547, -75.5)
                        ])
                ])
            ))
        font = Font(version, vendor, type, name, author, description, boundary, password, unknown, uuid, glyphs)
        stm = io.BytesIO()
        Font.save(stm, font)
        stm.seek(0)
        font1 = Font.load(stm)

        self.assertEqual(font1.version, 7)
        self.assertEqual(font1.vendor, 'kvenjoy')
        self.assertEqual(font1.type, 1)
        self.assertEqual(font1.name, 'Test')
        self.assertEqual(font1.author, 'Author')
        self.assertEqual(font1.description, 'Description')
        self.assertEqual(font1.boundary, 300)
        self.assertEqual(font1.password, 'pASSWORD')
        self.assertEqual(font1.unknown, b'')
        self.assertEqual(font1.uuid, '379865e6-84d8-4310-b227-45249f5afb44')
        self.assertEqual(len(font1.glyphs), 2)

        g = font1.glyphs[0]
        self.assertEqual(len(g.strokes), 1)
        s = g.strokes[0]
        self.assertEqual(len(s.points), 2)
        self.assertIsInstance(s.points[0], Point)
        self.assertEqual(s.points[0].x, -0.4999999403953552)
        self.assertEqual(s.points[0].y, -74.0)
        self.assertIsInstance(s.points[1], BezierPoint)
        self.assertEqual(s.points[1].cx1, -21.499998092651367)
        self.assertEqual(s.points[1].cy1, -45.50000762939453)
        self.assertEqual(s.points[1].cx2, -46.999996185302734)
        self.assertEqual(s.points[1].cy2, -95.5)
        self.assertEqual(s.points[1].x, -62.49999237060547)
        self.assertEqual(s.points[1].y, -71.5)

        g = font1.glyphs[1]
        self.assertEqual(len(g.strokes), 1)
        s = g.strokes[0]
        self.assertEqual(len(s.points), 2)
        self.assertIsInstance(s.points[0], Point)
        self.assertEqual(s.points[0].x, 0.0)
        self.assertEqual(s.points[0].y, -76.0)
        self.assertIsInstance(s.points[1], Point)
        self.assertEqual(s.points[1].x, -49.49999237060547)
        self.assertEqual(s.points[1].y, -75.5)

class TestGAP(unittest.TestCase):
    def test_load(self):
        gap_content = bytes([
            0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x63, 0x60, 0x60, 0x60, 0x64, 0x50,
            0x49, 0x36, 0x36, 0x33, 0xb3, 0x48, 0x33, 0xb4, 0xd4, 0x35, 0x48, 0x4e, 0x34, 0xd1, 0x35, 0xb1,
            0x34, 0xb2, 0xd4, 0x4d, 0x4c, 0x33, 0x33, 0xd0, 0xb5, 0xb4, 0x48, 0x35, 0x48, 0x49, 0xb2, 0x34,
            0x33, 0x30, 0x35, 0x36, 0x66, 0x60, 0x29, 0x49, 0x2d, 0x2e, 0x61, 0x60, 0x73, 0x2c, 0x2d, 0xc9,
            0xc8, 0x2f, 0x62, 0xe0, 0x76, 0x49, 0x2d, 0x4e, 0x2e, 0xca, 0x2c, 0x28, 0xc9, 0xcc, 0xcf, 0x63,
            0x60, 0x60, 0x60, 0x3a, 0x34, 0x81, 0x81, 0xc1, 0xb1, 0x00, 0xc4, 0x0a, 0x33, 0x74, 0x8a, 0x00,
            0xb2, 0x1b, 0xc0, 0x6c, 0x23, 0x20, 0xc9, 0x0c, 0xc4, 0x6c, 0x87, 0xbd, 0x18, 0x18, 0x0e, 0x3d,
            0x02, 0x8a, 0xef, 0x00, 0xd2, 0x0f, 0x80, 0xf4, 0x01, 0x06, 0x86, 0xc3, 0x22, 0x0c, 0x0c, 0x60,
            0x79, 0x46, 0x46, 0x20, 0xc5, 0x72, 0xe8, 0x0b, 0x50, 0x48, 0x12, 0x62, 0x8c, 0x53, 0x01, 0x58,
            0x8a, 0x89, 0x01, 0x22, 0x73, 0x8f, 0x81, 0xc1, 0x99, 0x15, 0x28, 0x3a, 0x0b, 0xa8, 0x79, 0x17,
            0x4c, 0x06, 0x00, 0x4e, 0x8c, 0x95, 0xb8, 0xbc, 0x00, 0x00, 0x00])
        version = 1
        uuid = 'c3668f19-0ca4-4929-af60-98e0db960533'
        name = 'test'
        author = 'Author'
        description = 'Description'

        stm = io.BytesIO(gap_content)
        gap = Gap.load(stm)

        self.assertEqual(gap.version, version)
        self.assertEqual(gap.uuid, uuid)
        self.assertEqual(gap.name, name)
        self.assertEqual(gap.author, author)
        self.assertEqual(gap.description, description)

        self.assertEqual(len(gap.variables), 2)
        v = gap.variables[0]
        self.assertEqual(v.x, -72.0)
        self.assertEqual(v.y, 15.0)
        self.assertEqual(v.name, 'V1')
        v = gap.variables[1]
        self.assertEqual(v.x, 54.0)
        self.assertEqual(v.y, 16.0)
        self.assertEqual(v.name, 'V2')

        self.assertEqual(len(gap.stroke_groups), 3)
        sg = gap.stroke_groups[0]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 3)
        self.assertEqual(sg[0].points[0].x, -202.0)
        self.assertEqual(sg[0].points[0].y, -113.0)
        self.assertEqual(sg[0].points[1].x, 23.0)
        self.assertEqual(sg[0].points[1].y, -112.0)
        self.assertEqual(sg[0].points[2].x, 24.0)
        self.assertEqual(sg[0].points[2].y, -148.0)
        sg = gap.stroke_groups[1]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 2)
        self.assertEqual(sg[0].points[0].x, -122.0)
        self.assertEqual(sg[0].points[0].y, -153.0)
        self.assertEqual(sg[0].points[1].x, 15.0)
        self.assertEqual(sg[0].points[1].y, 60.0)
        sg = gap.stroke_groups[2]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 2)
        self.assertEqual(sg[0].points[0].x, -111.0)
        self.assertEqual(sg[0].points[0].y, 133.0)
        self.assertEqual(sg[0].points[1].x, 77.0)
        self.assertEqual(sg[0].points[1].y, -93.0)

    def test_save(self):
        version = 1
        uuid = 'c3668f19-0ca4-4929-af60-98e0db960533'
        name = 'test'
        author = 'Author'
        description = 'Description'
        variables = [Variable(-72.0, 15.0, 'V1'), Variable(54.0, 16.0, 'V2')]
        stroke_groups = [
            [Stroke([Point(-202.0, -113.0), Point(23.0, -112.0), Point(24.0, -148.0)])],
            [Stroke([Point(-122.0, -153.0), Point(15.0, 60.0)])],
            [Stroke([Point(-111.0, 133.0), Point(77.0, -93.0)])]
        ]
        gap = Gap(version, uuid, name, author, description, variables, stroke_groups)
        stm = io.BytesIO()
        Gap.save(stm, gap)
        stm.seek(0)
        gap = Gap.load(stm)
        self.assertEqual(gap.version, version)
        self.assertEqual(gap.uuid, uuid)
        self.assertEqual(gap.name, name)
        self.assertEqual(gap.author, author)
        self.assertEqual(gap.description, description)

        self.assertEqual(len(gap.variables), 2)
        v = gap.variables[0]
        self.assertEqual(v.x, -72.0)
        self.assertEqual(v.y, 15.0)
        self.assertEqual(v.name, 'V1')
        v = gap.variables[1]
        self.assertEqual(v.x, 54.0)
        self.assertEqual(v.y, 16.0)
        self.assertEqual(v.name, 'V2')

        self.assertEqual(len(gap.stroke_groups), 3)
        sg = gap.stroke_groups[0]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 3)
        self.assertEqual(sg[0].points[0].x, -202.0)
        self.assertEqual(sg[0].points[0].y, -113.0)
        self.assertEqual(sg[0].points[1].x, 23.0)
        self.assertEqual(sg[0].points[1].y, -112.0)
        self.assertEqual(sg[0].points[2].x, 24.0)
        self.assertEqual(sg[0].points[2].y, -148.0)
        sg = gap.stroke_groups[1]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 2)
        self.assertEqual(sg[0].points[0].x, -122.0)
        self.assertEqual(sg[0].points[0].y, -153.0)
        self.assertEqual(sg[0].points[1].x, 15.0)
        self.assertEqual(sg[0].points[1].y, 60.0)
        sg = gap.stroke_groups[2]
        self.assertEqual(len(sg), 1)
        self.assertEqual(len(sg[0].points), 2)
        self.assertEqual(sg[0].points[0].x, -111.0)
        self.assertEqual(sg[0].points[0].y, 133.0)
        self.assertEqual(sg[0].points[1].x, 77.0)
        self.assertEqual(sg[0].points[1].y, -93.0)

class TestConverter(unittest.TestCase):
    def test_gap_to_json(self):
        version = 1
        uuid = 'c3668f19-0ca4-4929-af60-98e0db960533'
        name = 'test'
        author = 'Author'
        description = 'Description'
        variables = [Variable(-10.0, -11, 'V1'), Variable(-20, -21, 'V2')]
        stroke_groups = [
            [Stroke([Point(10, 11), Point(20, 21), Point(30, 31)])],
            [Stroke([Point(100, 110), BezierPoint(110, 111, 120, 121, 130, 131)])]
        ]
        gap = Gap(version, uuid, name, author, description, variables, stroke_groups)
        jo = gap_to_json(gap)
        self.assertEqual(jo['version'], gap.version)
        self.assertEqual(jo['name'], gap.name)
        self.assertEqual(jo['uuid'], gap.uuid)
        self.assertEqual(jo['author'], gap.author)
        self.assertEqual(jo['description'], gap.description)
        self.assertEqual(len(jo['variables']), len(gap.variables))
        for (jv, v) in zip(jo['variables'], gap.variables):
            self.assertEqual(jv['x'], v.x)
            self.assertEqual(jv['y'], v.y)
            self.assertEqual(jv['name'], v.name)
        self.assertEqual(len(jo['stroke_groups']), len(gap.stroke_groups))
        for (jsg, sg) in zip(jo['stroke_groups'], gap.stroke_groups):
            self.assertEqual(len(jsg), len(sg))
            for (js, s) in zip(jsg, sg):
                self.assertEqual(len(js['points']), len(s.points))
                for (jp, p) in zip(js['points'], s.points):
                    if isinstance(p, Point):
                        self.assertEqual(jp, [p.x, p.y])
                    elif isinstance(p, BezierPoint):
                        self.assertEqual(jp, [p.cx1, p.cy1, p.cx2, p.cy2, p.x, p.y])
                    else:
                        raise Exception('Unknown type "{}"'.format(type(p).__name__))

    def test_font_to_json(self):
        version = 7
        vendor = 'kvenjoy'
        type = 1
        name = 'Test'
        author = 'Author'
        description = 'Description'
        boundary = 300
        password = 'pASSWORD'
        unknown = b''
        uuid = '379865e6-84d8-4310-b227-45249f5afb44'
        glyphs = [
            Glyph(0x41, [Stroke([Point(10, 11), Point(20, 21), Point(30, 31)])]),
            Glyph(0x42, [Stroke([Point(100, 110), BezierPoint(110, 111, 120, 121, 130, 131)])])
        ]
        font = Font(version, vendor, type, name, author, description, boundary, password, unknown, uuid, glyphs)
        jo = gfont_to_json(font)
        self.assertEqual(jo['version'], font.version)
        self.assertEqual(jo['vendor'], font.vendor)
        self.assertEqual(jo['type'], font.type)
        self.assertEqual(jo['name'], font.name)
        self.assertEqual(jo['author'], font.author)
        self.assertEqual(jo['description'], font.description)
        self.assertEqual(jo['boundary'], font.boundary)
        self.assertEqual(jo['password'], font.password)
        self.assertEqual(jo['unknown'], [x for x in font.unknown])
        self.assertEqual(jo['uuid'], font.uuid)
        self.assertEqual(len(jo['glyphs']), len(font.glyphs))
        for (jg, g) in zip(jo['glyphs'], font.glyphs):
            self.assertEqual(jg['code'], g.code)
            for (js, s) in zip(jg['strokes'], g.strokes):
                self.assertEqual(len(js['points']), len(s.points))
                for (jp, p) in zip(js['points'], s.points):
                    if isinstance(p, Point):
                        self.assertEqual(jp, [p.x, p.y])
                    elif isinstance(p, BezierPoint):
                        self.assertEqual(jp, [p.cx1, p.cy1, p.cx2, p.cy2, p.x, p.y])
                    else:
                        raise Exception('Unknown type "{}"'.format(type(p).__name__))

if __name__ == '__main__':
    unittest.main(),
