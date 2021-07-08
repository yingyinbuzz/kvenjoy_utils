
def build_coord_matrix(img, stroke_checker):
    (w, h) = img.size
    cm = [[0 for x in range(w + 4)] for y in range(h + 4)]
    img_data = img.getdata()
    (x, y) = (0, 0)
    for p in img_data:
        if stroke_checker(p):
            cm[y + 1][x + 1] = 1
        x += 1
        if x >= w:
            x = 0
            y += 1
    return cm

def decompose_paths(cm):
    pass

