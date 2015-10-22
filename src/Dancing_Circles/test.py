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

def frange(start, stop, step):
    for i in itertools.count():
        cur = start + step*i
        if cur > stop:
            break
        yield cur

def logical_poly(draw, points, **kwargs):
    kwargs.setdefault("outline", "black")
    points = map(logical_to_screen, points)
    draw.polygon([p.tuple() for p in points], **kwargs)

def radial_curve(draw, inner_r, outer_r, right_theta, left_theta):
    assert left_theta > right_theta
    resolution = 64
    unit_curve = [Point(math.cos(theta), math.sin(theta)) for theta in frange(right_theta, left_theta, (left_theta-right_theta)/resolution)]
    points = [p * inner_r for p in unit_curve] + [p*outer_r for p in reversed(unit_curve)]

    logical_poly(draw, points, fill="black")
    

rings = 15

def make_image(f):
    img = Image.new("RGB", (screen_width, screen_height), "white")
    draw = ImageDraw.Draw(img)

    for i in range(1, rings+1):
        j = (rings+1-i)
        angle = f * 2 * math.pi * j
        r = i * 0.1
        radial_curve(draw, r, r+0.05, angle, angle+math.radians(90))

    return img

def eased(f):
    return (1+math.sin((f*math.pi) - math.pi/2))/2

seconds = 5
delay = 2 #in centiseconds
frames = seconds * 100 / delay
images = []
for f in frange(0, 1, 1.0/frames):
    print "\r", f, eased(f),
    images.append(make_image(eased(f)))

animation.make_gif(images, delay=delay)
