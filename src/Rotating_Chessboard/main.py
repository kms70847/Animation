from PIL import Image, ImageDraw
from geometry import Point
import math
import animation

#maps an x in the range(0,1) to a y in the range (0,1).
#when x is 0, y is 0; when x is 1, y is 1.
#for all intermediate values, y may differ from x.
def ease(x, kind="linear"):
    f = {
    "linear": lambda x: x,
    "trig": lambda x: 1-((math.cos(x*math.pi)/2)+0.5),
    "cubic": lambda x: 3*x**2 - 2*x**3
    }[kind]
    return f(x)    

def iter_lattice(ul, br):
    for i in range(ul.x, br.x):
        for j in range(ul.y, br.y):
            yield Point(i,j)

def exp(angle, radius):
    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    return Point(x,y)

def render_squares(**kargs):
    square_size = kargs.get("square_size", 128)
    cols = kargs.get("cols", 8)
    fg = kargs.get("fg", "black")
    bg = kargs.get("bg", "white")
    theta = kargs.get("theta", math.radians(45))
    parity = kargs.get("parity", 0)

    size = cols * square_size
    square_radius = math.sqrt(2) * square_size / 2

    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)

    for p in iter_lattice(Point(-1,-1), Point(1+cols, 1+cols)):
        if (p.x+p.y) % 2 == parity: continue
        square_center = (p + Point(0.5, 0.5)) * square_size
        corners = [square_center + exp(theta + math.radians(angle), square_radius) for angle in (45, 135, 225, 315)]
        draw.polygon([p.map(round).tuple() for p in corners], outline=fg, fill=fg)
    return img.resize((size/2, size/2), Image.ANTIALIAS)

frames = []
total_frames = 32
for i in range(total_frames):
    print i
    f = float(i) / total_frames
    f = ease(f, "cubic")
    theta = math.radians(f * 90)
    frames.append(render_squares(theta=theta))
for i in range(8): frames.append(frames[-1])

for i in range(total_frames):
    print i
    f = float(i) / total_frames
    f = ease(f, "cubic")
    theta = math.radians(f * -90)
    frames.append(render_squares(fg="white", bg="black", parity=1, theta=theta))
for i in range(8): frames.append(frames[-1])


animation.make_gif(frames)