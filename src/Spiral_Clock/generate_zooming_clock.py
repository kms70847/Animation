"""
given a rectangular donut with interior radius r and exterior radius R.
there is a polar space mapping such that, on the positive Y axis, the donut is distorted such that the exterior radius on the left aligns with the interior radius on the right, producing a clockwise-inwards swirl.

suppose an angle system with 0 and 360 lying on this discontinuity. The radius of points on 0 are multiplied by 1. The radius of points on 360 are multiplied by r/R. The distortion rate at other angles is the interpolation of these two extremes.
"""


from geometry import Point
from PIL import Image, ImageDraw
import math
import animation

image_size = 610
outer_radius = 305-25
inner_radius = 305-150

t = 1

def rebase(x, a, b, c, d):
    def normalize(x,a,b):
        return (x - a) / float(b-a)
    def denormalize(x, c,d):
        return (x*(d-c)) + c
    x = normalize(x, a, b)
    return denormalize(x, c, d)

def get_polar(p):
    rad = p.magnitude()
    theta = p.angle()
    assert theta >= -math.pi
    assert theta <= math.pi
    if theta < 0: theta += 2*math.pi
    return theta, rad

def get_cartesian(theta, rad):
    x = math.cos(theta) * rad
    y = math.sin(theta) * rad
    return Point(x,y)

#given a coordinate in the distorted system, finds the associated coordinate in the original system.
#the coordinate may or may not be an integer value; inter-pixel interpolation may be needed for image reconstruction.
def get_coords(p, R, r):
    global t
    if p.x == 0 and p.y == 0:
        return Point(0,0)
    theta, rad = get_polar(p)
    min_distortion = 1
    max_distortion = float(r)/R
    distortion = rebase(theta, 0, 2*math.pi, min_distortion, max_distortion)
    rad *= distortion
    rad *= t
    while rad > R:
        rad *= max_distortion
    while rad < r:
        rad /= max_distortion
    return get_cartesian(theta, rad)

#temporary function that does all the point manipulating math in one convenient spot
def f(p):
    delta = Point(image_size/2, image_size/2)
    p -= delta
    p = get_coords(p, outer_radius, inner_radius)
    p += delta
    #we only need this if we don't interpolate later
    #p = p.map(round)
    return p

def nice_get(img, pix, p):
    def get_neighbors(p):
        upper_left = p.map(int)
        candidates = [upper_left + delta for delta in Point(0,0), Point(1,0), Point(0,1), Point(1,1)]
        return [p for p in candidates if in_range(p)]
    def in_range(p):
        if not 0 <= p.x < img.size[0]: return False
        if not 0 <= p.x < img.size[1]: return False
        return True
    def average(colors):
        r = sum(color[0] for color in colors) / len(colors)
        g = sum(color[1] for color in colors) / len(colors)
        b = sum(color[2] for color in colors) / len(colors)
        return (r,g,b)

    #round down to nearest integer coord
    p = p.map(int)
    if not in_range(p): return (255,0,255)
    return pix[p.x, p.y]

    #alternate solution: nearest neighbor average. A bit slower than the rounding solution.
    neighbors = get_neighbors(p)
    default = (255,0,255)
    if not neighbors: return default
    colors = [pix[p.x, p.y] for p in neighbors]
    return average(colors)

def distort(src):
    src_pix = src.load()
    dst = Image.new("RGB", src.size)
    dst_pix = dst.load()

    for i in range(dst.size[0]):
        for j in range(dst.size[1]):
            p = f(Point(i,j))
            dst_pix[i,j] = nice_get(src, src_pix, p)

    return dst

src = Image.open("clock.png")
imgs = []
frames = 16
for i in range(frames):
    print "Creating image {}...".format(i+1)
    t = (float(outer_radius)/inner_radius)**rebase(i, 0, frames, 0,1)
    print "time mult:", t
    dst = distort(src)
    imgs.append(dst)
    print "Created."

print "Creating gif..."
animation.make_gif(imgs, delay=4)
print "Created."