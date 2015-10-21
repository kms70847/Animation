import math
import animation
from PIL import Image, ImageFont, ImageDraw


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

def lerp(start, end, steps, kind="linear"):
    step = float(end-start) / steps
    for i in range(steps):
        x = i / float(steps)
        y = ease(x, kind)
        print i, x, y
        yield start + (end-start)*y

def circle(draw, center, radius, **options):
    center = map(int, center)
    left = center[0] - radius
    top = center[1] - radius
    right = left + 2*radius
    bottom = top + 2*radius
    draw.arc((left, top, right, bottom), 0, 360, **options)

def frob(draw, center, radius, angle, skew, **options):
    if radius < 2: return
    circle(draw, center, radius, **options)
    dy = (radius/2) * math.sin(angle)
    dx = (radius/2) * math.cos(angle)
    left  = (center[0] - dx, center[1] - dy)
    right = (center[0] + dx, center[1] + dy)
    frob(draw, left,  radius/2, angle+skew, skew, **options)
    frob(draw, right, radius/2, angle+skew, skew, **options)

def from_degrees(angle):
    return angle * 2 * math.pi / 360.0

imgs = []
size = 200
margin = 10
for angle in lerp(0, 180, 64, kind="cubic"):
    im = Image.new("RGB", (size+margin*2, size+margin*2), "white")
    draw = ImageDraw.Draw(im)
    frob(draw, (margin+size/2, margin+size/2), size/2, from_degrees(angle), from_degrees(angle),  fill="black")
    imgs.append(im)

animation.make_gif(imgs)