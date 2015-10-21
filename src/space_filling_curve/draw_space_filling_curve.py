from PIL import Image, ImageDraw

from geometry import Point

size = 500

def space_filling_curve(level):
    curve = "L"
    rules = {
        "L": "lRlfLrfrLflRl",
        "R": "rLrfRlflRfrLr"
    }
    for i in range(level):
        curve = "".join(rules.get(c, c) for c in curve)
    return curve

def transform(x, old_min, old_max, new_min, new_max):
    x -= old_min
    x /= old_max-old_min
    x *= new_max-new_min
    x += new_min
    return x

#using region 4 system (origin at top left)
up = Point(0,-1)
down = Point(0,1)
left = Point(-1,0)
right = Point(1,0)
def turned_left(dir):
    return {up: left, left: down, down: right, right: up}.get(dir)
def turned_right(dir):
    return {up: right, right:down, down:left, left:up}.get(dir)

def render_curve(c, curve_frac=1, forward_frac=0):
    assert curve_frac == 1 or forward_frac == 0
    #we need this small hack so that the top divot grows from the top down, rather than the two bulges growing from the bottom up.
    #but we only want to do it when forward_frac is 0, or else the fs we are replacing will render improperly.
    if curve_frac != 1:
        c = c.replace("LrfrL", "flflRlflf")
        c = c.replace("RlflR", "frfrLrfrf")

    points = []
    p = Point(0,0)
    points.append(p)
    facing = down
    for symbol in c:
        if symbol == "l":
            facing = turned_left(facing)
        elif symbol == "r":
            facing = turned_right(facing)
        elif symbol == "f":
            p = p + (facing * transform(forward_frac, 0, 1, 1, 0.333))
            points.append(p)
        elif symbol in ["L", "R"]:
            turned = turned_right if symbol == "R" else turned_left
            #todo: guard against floating point errors
            p = p + facing*curve_frac
            points.append(p)
            facing = turned(facing)
            p = p + facing
            points.append(p)
            facing = turned(facing)
            p = p + facing*curve_frac
            points.append(p)
        else:
            raise Exception("unrecognized symbol {}".format(symbol))
    return points

def render_lines(points):
    im = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(im)
    for a, b in zip(points, points[1:]):
        draw.line([a.tuple(), b.tuple()], fill="black")
    return im

from animation import make_gif


imgs = []
def frob(curve, curve_frac, forward_frac):
    points = render_curve(curve, curve_frac, forward_frac)
    width = max(p.x for p in points)
    points = [(p * 0.80 * size / width) + Point(size/10, size/10) for p in points]
    im = render_lines(points)
    imgs.append(im)

def delay(n):
    imgs.append(imgs[-1])
    
max_depth = 6
for i in range(max_depth+1):
    print "generating curve depth {}".format(i)
    curve = space_filling_curve(i)
    for frac in [x * 0.10 for x in range(1, 11)]:
        frob(curve, frac, 0)
    if i == 0 or i == max_depth: continue
    delay(5)
    for frac in [x * 0.10 for x in range(1, 11)]:
        frob(curve, 1, frac)
    delay(5)

#pause on the last frame
delay(40)

print "making gif..."
make_gif(imgs, delay=4)
