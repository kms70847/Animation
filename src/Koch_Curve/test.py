from PIL import Image, ImageDraw
from geometry import Point, midpoint
import animation
import math

#returns a rotated counter-clockwise around b
def rotated_about(a,b, angle):
    if a == b: return a
    cur_angle = (a-b).angle()
    angle += cur_angle
    radius = (a-b).magnitude()
    dx = radius*math.cos(angle)
    dy = radius*math.sin(angle)
    return b + Point(dx, dy)

def koch(draw, a, b, frac, depth):
    if depth == 1:
        draw.line(a.tuple()+b.tuple(), fill="black")
    else:
        angle = frac * math.radians(360)
        p = midpoint(a,b, 1/3.0)
        r = midpoint(a,b, 2/3.0)
        q = rotated_about(r,p,angle)
        for p1, p2 in pairs((a,p,q,r,b)):
            koch(draw, p1, p2, frac, depth-1)

def pairs(seq):
    return zip(seq, seq[1:])

def cyclic_pairs(seq):
    for i in range(len(seq)):
        a = seq[i]
        b = seq[(i+1)%len(seq)]
        yield a,b

def make_img(f):
    size = 400
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)
    angles = [math.radians(x) for x in (330, 210, 90)]
    corners = [Point(size/2, size/2) + (Point(math.cos(theta), math.sin(theta)) * size/2) for theta in angles]
    for a,b in cyclic_pairs(corners):
        koch(draw, a, b, f, 6)
    return img

def eased(f):
    return ((1 + math.cos((f * math.pi * 2)-math.pi))/2)

images = []
frames = 200
for i in range(1,frames+1):
    f = float(i)/frames
    #f = eased(f)
    print i, f
    images.append(make_img(f))
animation.make_gif(images, delay=2)