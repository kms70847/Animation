import math
import animation
from math import sin, cos
from geometry import Point

from PIL import Image, ImageDraw

def planar_apply(p, f, axis):
    if axis == "x":
        y,z = f(Point(p.y, p.z)).tuple()
        return Point(p.x, y, z)
    elif axis == "y":
        x,z = f(Point(p.x, p.z)).tuple()
        return Point(x, p.y, z)
    elif axis == "z":
        x,y = f(Point(p.x, p.y)).tuple()
        return Point(x, y, p.z)
    else:
        raise Exception("Unexpected axis {}".format(axis))

def exp(radius, angle):
    return Point(radius*math.cos(angle), radius*math.sin(angle))

def rotated(p, angle):
    theta = math.atan2(p.y,p.x)
    theta += angle
    radius = p.magnitude()
    return exp(radius, theta)

def planar_rotated(p, angle, axis):
    f = lambda p: rotated(p, angle)
    return planar_apply(p, f, axis)

#---------------------------------------- end of point geometry stuff ----------------------------------------

def frange(start, stop, step):
    i = 0
    while True:
        cur = start + (step * i)
        if cur > stop: break
        yield cur
        i += 1

def dot(draw, p, radius=3, **kwargs):
    kwargs.setdefault("fill", "black")
    draw.chord((p.x-radius, p.y-radius, p.x+radius, p.y+radius), 0, 359, **kwargs)

def make_frame(f):
    longitude_resolution = 16
    lattitude_resolution = 16
    points = []
    for f_long in frange(0, 1, 1./longitude_resolution):
        theta = f_long * 2*math.pi
        for f_latt in frange(0, 1, 1./lattitude_resolution):
            
            f_latt = (f_latt + f_long/lattitude_resolution)%1
            iota = (f_latt-0.5) * math.pi

            #adding this component causes the dots to march from one pole to another
            iota = iota + f*math.pi/lattitude_resolution
            if iota >= math.pi/2: iota += math.pi

            #this used to be a parametric equation to make the dots undulate up and down, but it didn't look good.
            radius = 1

            y = radius * sin(iota)
            #adding iota in these next two lines causes each lattitudinal ring to be rotated w.r.t its neighbors
            x = radius * cos(iota) * cos(theta+iota)
            z = radius * cos(iota) * sin(theta+iota)

            points.append(Point(x,y,z))

    size = 800
    margin = 50
    to_screen = lambda s: int(((s+1)/2.0)*(size-margin*2)) + margin

    points = [planar_rotated(p, math.radians(-45), "z") for p in points]
    points = [planar_rotated(p, math.radians(45), "y") for p in points]

    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    dot_size_resolution = 6
    dot_size = lambda z: dot_size_resolution-math.floor(((z + 1)/2)*dot_size_resolution)

    for p in points:
        dot(draw, p.map(to_screen), dot_size(p.z))
    return img.resize((size/2, size/2), Image.ANTIALIAS)

images = []
frames = 40
for i in range(frames):
    print i
    images.append(make_frame(float(i)/frames))

animation.make_gif(images)