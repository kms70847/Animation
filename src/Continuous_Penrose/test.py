import math
from geometry import Point, midpoint

from PIL import Image, ImageDraw


phi = (1 + math.sqrt(5)) / 2

def exp(radius, angle):
    return Point(math.cos(angle)*radius, math.sin(angle)*radius)

# def kite(a,b,c, depth):
    # if depth == 1:
        # draw.polygon(a.tuple()+b.tuple()+c.tuple(), outline="black", fill="white")
    # else:
        # p = midpoint(a,b, (phi-1)/phi)
        # q = midpoint(a,c, 1/phi)
        # dart(p,q,a, depth-1)
        # kite(b,p,q, depth-1)
        # kite(b,c,q, depth-1)

# def dart(d,e,f, depth):
    # if depth == 1:
        # draw.polygon(d.tuple()+e.tuple()+f.tuple(), outline="black", fill="gray")
    # else:
        # p = midpoint(e,f, (phi-1)/phi)
        # dart(p,d,e, depth-1)
        # kite(f,p,d, depth-1)

kitefill = "white"
dartfill = "gray"
outline = None

def kite(a,b,c, depth, parent="k"):
    if depth <= 1:
        if parent == "k" or depth == 1:
            draw.polygon(a.tuple()+b.tuple()+c.tuple(), outline=outline, fill=kitefill)
        else:
            ab = midpoint(a,b, depth)
            ac = midpoint(a,c,depth)
            draw.polygon(a.tuple()+ab.tuple()+ac.tuple(), outline=outline, fill=kitefill)
            draw.polygon(b.tuple() + c.tuple() + ac.tuple() + ab.tuple(), outline=outline, fill=dartfill)
    else:
        p = midpoint(a,b, (phi-1)/phi)
        q = midpoint(a,c, 1/phi)
        dart(p,q,a, depth-1, "k")
        kite(b,p,q, depth-1, "k")
        kite(b,c,q, depth-1, "k")

def dart(d,e,f, depth, parent="d"):
    if depth <= 1:
        if parent == "d" or depth == 1:
            draw.polygon(d.tuple()+e.tuple()+f.tuple(), outline=outline, fill=dartfill)
        else:
            fd = midpoint(f,d, depth)
            fe = midpoint(f,e, depth)
            draw.polygon(f.tuple() + fd.tuple() + fe.tuple(), outline=outline, fill=dartfill)
            draw.polygon(d.tuple() + e.tuple() + fe.tuple() + fd.tuple(), outline=outline, fill=kitefill)
    else:
        p = midpoint(e,f, (phi-1)/phi)
        dart(p,d,e, depth-1, "d")
        kite(f,p,d, depth-1, "d")

def bounce(frames):
    return frames + [frames[-1]] * 12 + list(frames[::-1]) + [frames[0]]*12

draw = None
def render(frac):
    global draw
    radius = 1000
    center = Point(radius, radius)

    img = Image.new("RGB", (radius*2, radius*2), "white")
    draw = ImageDraw.Draw(img)

    spokes = [center + exp(radius, math.radians(theta)) for theta in range(0, 360, 36)]
    for i in range(10):
        b = spokes[i]
        c = spokes[(i+1)%len(spokes)]
        if i %2 == 1: b,c = c,b
        kite(center, b,c,frac)

    img = img.resize((radius/2, radius/2), Image.ANTIALIAS)
    return img

import animation
frames = []
for i in range(64):
    print i,
    frames.append(render(1 + (i / 8.)))

animation.make_gif(bounce(frames), delay=8)