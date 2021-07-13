
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

def find_closed_path(cm, path):
    (x, y, dx, dy) = path[-1]
    (x, y) = (x + dx, y + dy)
    if (x, y) == (path[0][0], path[0][1]):
        # Path closed
        return
    if cm[y - 1][x - 1] == 1 and cm[y - 1][x] == 0:
        dx = 0
        dy = -1
    elif cm[y - 1][x] == 1 and cm[y][x] == 0:
        dx = 1
        dy = 0
    elif cm[y][x] == 1 and cm[y][x - 1] == 0:
        dx = 0
        dy = 1
    elif cm[y][x - 1] == 1 and cm[y - 1][x - 1] == 0:
        dx = -1
        dy = 0
    else:
        raise Exception('Could not route path at ({}, {})'.format(x, y))
    path.append((x, y, dx, dy))
    find_closed_path(cm, path)

def find_path(cm):
    sp = find_stroke_pixel(cm)
    if sp is None:
        return None
    (sx, sy) = sp
    p = [(sx, sy, 0, 1)]
    find_closed_path(cm, p)
    return p

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
    print_matrix(cm, "Matrix")
    p = find_path(cm)
    invert_by_path(cm, p)
    print_matrix(cm, "After inverting path")
    p2 = find_path(cm)
    invert_by_path(cm, p2)
    print_matrix(cm, "After inverting path again")
    cm1 = mark_path(cm, p, p2)
    print_matrix(cm1, "Marked paths")
