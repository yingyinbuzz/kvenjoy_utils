
from PIL import Image

def __getpixel(image, x, y):
    """ Get pixel from image at given (x, y) coordinate.
    If given coordinate is out of range, returns a non-stroke pixel.

    Arguments:
    image -- The PIL image object.
    x     -- X coordinate of the pixel.
    y     -- Y coordinate of the pixel.
    """
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

                stroke_count = 0
                for yy in range(y - stroke_size, y + stroke_size):
                    for xx in range(x - stroke_size, x + stroke_size):
                        if is_stroke(__getpixel(image, xx, yy)):
                            stroke_count += 1
                be_stroke = stroke_count >= (stroke_size * stroke_size) / 2

                if be_stroke:
                    new_image.putpixel((x, y), make_stroke())
                else:
                    new_image.putpixel((x, y), p)
    return new_image
