
def build_coord_matrix(img, stroke_checker):
    (w, h) = img.size
    cm = [[0 for x in range(w + 3)] for y in range(h + 3)]
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

def find_stroke_pixel(cm):
    (w, h) = (len(cm[0]), len(cm))
    # Locate first stroke pixel
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if cm[y][x] != 0:
                sx = x
                sy = y
                return (x, y)
    return None

def find_path(cm):
    sp = find_stroke_pixel(cm)
    if sp is None:
        return None
    (sx, sy) = sp
    (x, y, dx, dy) = (sx, sy, 0, 1)
    path = []
    point_cnt = 0
    yx_offsets = ((-1, -1, -1,  0,  0, -1),
                  (-1,  0,  0,  0,  1,  0),
                  ( 0,  0,  0, -1,  0,  1),
                  ( 0, -1, -1, -1, -1,  0))
    offsets = ((2, 2, 2),
               (3, 0, 1),
               (0, 0, 0))
    while True:
        point_cnt += 1
        path.append((x, y, dx, dy))
        (x, y) = (x + dx, y + dy)
        if (x, y) == (sx, sy):
            break
        found = False
        offset = offsets[dx + 1][dy + 1]
        for i in range(4):
            dys, dxs, dyb, dxb, ddx, ddy = yx_offsets[(i + offset) % 4]
            if cm[y + dys][x + dxs] == 1 and cm[y + dyb][x + dxb] == 0:
                dx = ddx
                dy = ddy
                found = True
                break
        if not found:
            raise Exception('Could not route path at ({}, {})'.format(x, y))
    return path

def invert_by_path(cm, path):
    # Build scan points
    sps = {}
    for (x, y, dx, dy) in path:
        if dy == 1 or dy == -1:
            y = y - 1 if dy == -1 else y
            if y in sps:
                sps[y].append((x, y, dx, dy))
            else:
                sps[y] = [(x, y, dx, dy)]
    sls = [sorted([p for p in sps[y]], key=lambda p : p[0]) for y in sorted(sps.keys())]
    segments = []
    for line in sls:
        start_x = None
        for x, y, dx, dy in line:
            if start_x is None:
                if dy == 1:
                    start_x = x
            else:
                if dy == -1:
                    segments.append((y, start_x, x))
                    start_x = None
    for y, sx, ex in segments:
        for x in range(sx, ex):
            cm[y][x] = 0 if cm[y][x] == 1 else 1

def mark_path(cm, *paths):
    cmo = [[x for x in line] for line in cm]
    for path in paths:
        for (x, y, dx, dy) in path:
            if dx == -1:
                cmo[y][x] = 2
            elif dx == 1:
                cmo[y][x] = 3
            elif dy == -1:
                cmo[y][x] = 4
            elif dy == 1:
                cmo[y][x] = 5
    return cmo

matrix_chars = {0: ' ', 1: '.', 2: '<', 3: '>', 4: '^', 5: 'v'}
def print_matrix(cm, tag):
    print('---- {} ----'.format(tag))
    lno = -1
    for line in cm:
        lno += 1
        print('{:10}'.format(lno), end='')
        for x in line:
            print(matrix_chars[x], end='')
        print()

def decompose_paths(cm):
    paths = []
    while True:
        p = find_path(cm)
        if p is None:
            break
        paths.append(p)
        invert_by_path(cm, p)
    return paths
