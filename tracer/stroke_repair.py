
from PIL import Image

def __getpixel(image, x, y):
    if x >= 0 and x < image.size[0] and y >=0 and y < image.size[1]:
        return image.getpixel((x, y))
    else:
        return (255, 255, 255) if image.mode == 'RGB' else 255

def repair_strokes(image, stroke_size, is_stroke, make_stroke):
    """Repain holes in given stroke image.
    Arguments:
    image        -- The PIL image object to be repaired.
    stroke_size  -- Detected stroke size  for the given image.
    is_stoke     -- A callable object to check whether a given pixel is stroke or not.
    make_stroke  -- A callable object to make a new stroke pixel.
    return       -- A new image objec holds repaired stroke image.
    """
    w, h = image.size
    new_image = Image.new(image.mode, image.size)
    for y in range(h):
        for x in range(w):
            p = image.getpixel((x, y))
            if is_stroke(p):
                new_image.putpixel((x, y), p)
            else:
                be_stroke = False
                if not be_stroke:
                    hollow = 0
                    for offset in range(-stroke_size, stroke_size):
                        if not is_stroke(__getpixel(image, x, y + offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= stroke_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-stroke_size, stroke_size):
                        if not is_stroke(__getpixel(image, x + offset, y)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= stroke_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-stroke_size, stroke_size):
                        if not is_stroke(__getpixel(image, x + offset, y + offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= stroke_size
                if not be_stroke:
                    hollow = 0
                    for offset in range(-stroke_size, stroke_size):
                        if not is_stroke(__getpixel(image, x + offset, y - offset)):
                            hollow += 1
                    be_stroke = be_stroke or hollow <= stroke_size

                if be_stroke:
                    new_image.putpixel((x, y), make_stroke())
                else:
                    new_image.putpixel((x, y), p)
    return new_image
