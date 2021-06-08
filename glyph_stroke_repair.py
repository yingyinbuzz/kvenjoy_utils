#!/usr/bin/env python3

from PIL import Image
from tracer.stroke_size import *

def is_stroke_grayscale(p):
    return p < 128

def make_stroke_pixel_grayscale():
    return 0

def is_stroke_rgb(p):
    r, g, b = p
    return r < 128 and g < 128 and b < 128

def make_stroke_pixel_rgb():
    return (0, 0, 0)

def getpixel(image, x, y):
    if x >= 0 and x < image.size[0] and y >=0 and y < image.size[1]:
        return image.getpixel((x, y))
    else:
        return (255, 255, 255) if image.mode == 'RGB' else 255

if __name__ == '__main__':
    import sys
    import os
    image_file = sys.argv[1]
    s_size = int(sys.argv[2])
    image = Image.open(image_file)
    w, h = image.size
    new_image = Image.new(image.mode, image.size)
    is_stroke = is_stroke_rgb if image.mode == 'RGB' else is_stroke_grayscale
    make_stroke_pixel = make_stroke_pixel_rgb if image.mode == 'RGB' else make_stroke_pixel_grayscale
    for y in range(h):
        for x in range(w):
            p = image.getpixel((x, y))
            if is_stroke(p):
                new_image.putpixel((x, y), p)
            else:
                be_stroke = False
                if not be_stroke:
                    hollow = 0
                    for offset in range(-s_size, s_size):
                        if not is_stroke(getpixel(image, x, y + offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= s_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-s_size, s_size):
                        if not is_stroke(getpixel(image, x + offset, y)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= s_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-s_size, s_size):
                        if not is_stroke(getpixel(image, x + offset, y + offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= s_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-s_size, s_size):
                        if not is_stroke(getpixel(image, x + offset, y - offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= s_size

                if be_stroke:
                    new_image.putpixel((x, y), make_stroke_pixel())
                else:
                    new_image.putpixel((x, y), p)
    new_image.save('{}_repaired.png'.format(os.path.splitext(image_file)[0]))
