from PIL import Image, ImageDraw
from geometry import Point, midpoint
from fractions import gcd
import itertools
import math
import animation

screen_width = 400
screen_height = 400
logical_left = -2
logical_right = 2
logical_top = 2
logical_bottom = -2
logical_width = logical_right - logical_left
logical_height = logical_bottom - logical_top

def logical_to_screen(p):
    x = (p.x - logical_left) * screen_width / logical_width
    y = (p.y - logical_top) * screen_height / logical_height
    return Point(x,y).map(int)

def dot(draw, p, radius=3, **kwargs):
    kwargs.setdefault("fill", "black")
    draw.chord((p.x-radius, p.y-radius, p.x+radius, p.y+radius), 0, 359, **kwargs)

def logical_dot(draw, p, radius=3, **kwargs):
    dot(draw, logical_to_screen(p), int(radius*screen_width/logical_width), **kwargs)

def frange(start, stop, step):
    for i in itertools.count():
        cur = start + step*i
        if cur > stop:
            break
        yield cur

def make_image(f):
    def trefoil(theta):
        r = math.sin(theta * 3)
        return Point(r*math.cos(theta), r*math.sin(theta))

    theta = f * math.pi
    bands = []
    offsets = (0, 120, 240)
    for offset in offsets:
        img = Image.new("L", (screen_width, screen_height), "black")
        draw = ImageDraw.Draw(img)

        p = trefoil(theta + math.radians(offset))
        logical_dot(draw, p, math.cos(math.radians(30)), fill=0xFF, outline=0xFF)
        bands.append(img)

    return Image.merge("RGB", bands)

seconds = 3
delay = 2 #in centiseconds
frames = seconds * 100 / delay
images = []
for f in frange(0, 1, 1.0/frames):
    print "{:03}%\r".format(int(f*100)),
    images.append(make_image(f))

animation.make_gif(images, delay=delay)