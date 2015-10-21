from PIL import Image, ImageDraw
from geometry import Point, midpoint
import itertools
import animation

def bezier_step(points, f):
    return [midpoint(points[i], points[i+1], f) for i in range(len(points)-1)]

def bezier(points, f):
    while len(points) > 1:
        points = bezier_step(points,f)
    return points[0]

def dot(draw, p, radius=3, **kwargs):
    kwargs.setdefault("fill", "black")
    draw.chord((p.x-radius, p.y-radius, p.x+radius, p.y+radius), 0, 359, **kwargs)

def line_chain(draw, points, show_vertices=True, **kwargs):
    points = [p.map(int) for p in points]
    for a,b in zip(points, points[1:]):
        draw.line(a.tuple() + b.tuple(), **kwargs)
    if show_vertices:
        for p in points:
            dot(draw, p, **kwargs)

def frange(start, stop, step):
    for i in itertools.count():
        cur = start + (step * i)
        if cur > stop: break
        yield cur

def make_image(f):
    control_points = [
        Point(58 ,283),
        Point(127 ,56),
        Point(203 ,226),
        Point(270 ,112),
        Point(342 ,169),
        Point(271 ,225),
    ]

    #this copy will get destroyed eventually
    points = control_points[:]

    colors = "gray green blue yellow orange red".split()
    color_iter = iter(colors)

    img = Image.new("RGB", (400,400), "white")
    draw = ImageDraw.Draw(img)
    while True:
        line_chain(draw, points, fill=next(color_iter))
        if len(points) == 1: break
        points = bezier_step(points, f)

    curve = [bezier(control_points, i) for i in frange(0, f, 0.01)]       
    line_chain(draw, curve, False, fill="red", width=2)

    return img

images = []
for f in frange(0,1,0.01):
    print f
    images.append(make_image(f))

animation.make_gif(images)