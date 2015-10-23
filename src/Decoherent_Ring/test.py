from PIL import Image, ImageDraw
from geometry import Point, midpoint
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

def parametric(draw, f, **kwargs):
    def to_cartesian(r, theta):
        return Point(r*math.cos(theta), r*math.sin(theta))
    resolution = kwargs.pop("resolution", 180)
    width = kwargs.pop("width", 0.04)
    polar_coords = [(f(theta), theta) for theta in frange(0, 2*math.pi, 2*math.pi/resolution)]
    inner_side = [(r-width, theta) for r, theta in polar_coords]
    outer_side = [(r+width, theta) for r, theta in reversed(polar_coords)]
    polar_coords = inner_side + outer_side
    coords = [to_cartesian(r, theta) for r, theta in polar_coords]

    kwargs.setdefault("fill", "black")
    logical_poly(draw, coords, **kwargs)
    
#parametric function describing a circle that has a perturbation on one side resembling a sine wave.
#theta is the free variable; iota controls where the smooth side points; f is the offset for the sine wave.
def waves(theta, iota, f):
    f = f * 2 * math.pi / 16
    return 1 + (((1 + math.sin(theta+iota))/2)**7) * (math.cos((theta+f)*16)/8)

def make_image(f):
    bands = []
    for offset in (0, 1/3.0, 2/3.0):
        img = Image.new("L", (screen_width, screen_height), 0x00)
        draw = ImageDraw.Draw(img)
        parametric(draw, lambda t: waves(t, f*2*math.pi, offset), outline=0xFF, fill=0xFF)
        bands.append(img)
    return Image.merge("RGB", bands)

seconds = 5
delay = 2 #in centiseconds
frames = seconds * 100 / delay
images = []
for f in frange(0, 1, 1.0/frames):
    print "{:03}".format(int(f*100))
    images.append(make_image(f))

animation.make_gif(images, delay=delay)
