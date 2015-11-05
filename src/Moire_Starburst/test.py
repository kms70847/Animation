import math
import animation
import itertools
from geometry import Point
from PIL import Image, ImageDraw

#returns the determinate of
#| a b |
#| c d |
def determinate(a,b,c,d):
    return a*d - b*c

#copied straight from Wikipedia.
#returns None if the lines are parallel.
def _intersection(x1, y1, x2, y2, x3, y3, x4, y4):
    x_numerator = determinate(
        determinate(x1, y1, x2, y2),
        determinate(x1, 1, x2, 1),
        determinate(x3, y3, x4, y4),
        determinate(x3, 1, x4, 1)
    )
    x_denominator = determinate(
        determinate(x1, 1, x2, 1),
        determinate(y1, 1, y2, 1),
        determinate(x3, 1, x4, 1),
        determinate(y3, 1, y4, 1)
    )

    y_numerator = determinate(
        determinate(x1, y1, x2, y2),
        determinate(y1, 1, y2, 1),
        determinate(x3, y3, x4, y4),
        determinate(y3, 1, y4, 1)
    )

    y_denominator = x_denominator
    if x_denominator == 0:
        return None
    return Point(float(x_numerator)/x_denominator, float(y_numerator)/y_denominator)

#finds the intersection of line segments AB and CD
def intersection(a,b,c,d):
    args = a.tuple()+b.tuple()+c.tuple()+d.tuple()
    return _intersection(*args)

def exp(radius, angle):
    return Point(math.cos(angle)*radius, math.sin(angle)*radius)

#returns the points of a regular polygon.
def poly(center, radius, num_sides):
    for i in range(num_sides):
        angle = 2*math.pi * i / num_sides
        yield center + exp(radius, angle)
        
def starburst(center, radius, num_rays):
    #where possible, join collinear rays
    if num_rays %2 == 0:
        points = list(poly(center, radius, num_rays))
        return [(points[i], points[i+num_rays/2]) for i in range(num_rays/2)]
    else:
        return [(center, p) for p in poly(center, radius, num_rays)]

def dot(draw, p, radius=3, **kwargs):
    kwargs.setdefault("fill", "black")
    draw.chord((p.x-radius, p.y-radius, p.x+radius, p.y+radius), 0, 359, **kwargs)

def frange(start, stop, step):
    for i in itertools.count():
        cur = start + (step * i)
        if cur > stop: break
        yield cur

def make_frame(f):
    size = 800
    path_center = Point(size/2, size/2)
    path_radius = size/4
    path_p = path_center + exp(path_radius, f*2*math.pi)
    stars = [starburst(c, size, 30) for c in (Point(5*size/16, size/2), path_p)]

    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    for star in stars:
        for a,b in star:
            draw.line(a.tuple()+b.tuple(), fill="gray")

    for a,b in stars[0]:
        for c,d in stars[1]:
            p = intersection(a,b,c,d)
            if p is not None:
                dot(draw, p)

    return img.resize((size/2, size/2), Image.ANTIALIAS)

frames = 240
images = []
for f in frange(0, 1, 1.0/frames):
    print f
    images.append(make_frame(f))

animation.make_gif(images)