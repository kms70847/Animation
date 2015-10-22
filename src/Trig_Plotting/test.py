from PIL import Image, ImageDraw
from geometry import Point, midpoint
import itertools
import math
import animation

screen_width = 800
screen_height = 400
logical_left = -1
logical_right = 15
logical_top = 4
logical_bottom = -4
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

def pairs(seq):
    for a,b in zip(seq[0::2], seq[1::2]):
        yield a,b

def dot(draw, p, radius=3, **kwargs):
    kwargs.setdefault("fill", "black")
    draw.chord((p.x-radius, p.y-radius, p.x+radius, p.y+radius), 0, 359, **kwargs)

def line(draw, a,b, **kwargs):
    style = kwargs.pop("style", "solid")
    if style == "solid":
        draw.line(a.tuple()+b.tuple(), **kwargs)
    elif style == "dotted":
        segment_size = 10
        length = (b-a).magnitude()
        if length == 0: return
        points = [midpoint(a,b,f) for f in frange(0,1, float(segment_size)/length)]
        for a,b in pairs(points):
            line(draw, a,b, **kwargs)
    else:
        raise Exception("Unknown line style {}".format(style))

def logical_dot(draw, p, radius=3, **kwargs):
    dot(draw, logical_to_screen(p), **kwargs)

def logical_circle(draw, center, radius, **kwargs):
    kwargs.setdefault("outline", "black")
    r = int(abs(radius * screen_width / logical_width))
    p = logical_to_screen(center)
    draw.chord((p.x-r, p.y-r, p.x+r, p.y+r), 0, 359, **kwargs)

def logical_line(draw, a, b, **kwargs):
    kwargs.setdefault("fill", "black")
    a = logical_to_screen(a)
    b = logical_to_screen(b)
    line(draw, a,b, **kwargs)

def logical_graph(draw, f, **kwargs):
    left = kwargs.pop("left", logical_left)
    right = kwargs.pop("right", logical_right)
    resolution = 100
    step = float(right - left) / resolution
    points = [Point(x, f(x)) for x in frange(left, right, step)]
    for a,b in zip(points, points[1:]):
        if (a-b).magnitude() < 10:
            logical_line(draw, a, b, **kwargs)

def make_image(theta):
    img = Image.new("RGB", (screen_width, screen_height), "white")
    draw = ImageDraw.Draw(img)

    #center of circle
    c = Point(0,0)
    #radius of circle
    r = 1

    #intersection of circle and ray extending from c, with angle theta WRT the x axis
    p = c + Point(r*math.cos(theta), r*math.sin(theta))
    #point 90 degrees away from p
    p_chord = c + Point(r*math.cos(theta+math.radians(90)), r*math.sin(theta + math.radians(90)))
    #antipode of p
    neg_p = c + Point(r*math.cos(theta+math.radians(180)), r*math.sin(theta + math.radians(180)))


    #boundary line where we will begin graphing functions
    boundary_x = c.x+r
    #point at which tan(theta) intersects boundary
    boundary_intersect = Point(boundary_x, r*math.tan(theta))

    #determine whether p or its antipode is farther right
    if theta <= math.radians(90) or theta >= math.radians(270):
        tan_right_p = p
        tan_left_p = neg_p
    else:
        tan_right_p = neg_p
        tan_left_p = p
  

    logical_circle(draw, c, r)

    logical_line(draw, c, p)
    logical_line(draw, p, p_chord, fill="gray")
    logical_line(draw, Point(boundary_x, logical_top), Point(boundary_x, logical_bottom))     
    logical_line(draw, tan_right_p, boundary_intersect, fill="red", style = "dotted")
    logical_line(draw, tan_left_p, c-boundary_intersect, fill="red", style="dotted")
    logical_line(draw, p, Point(r, p.y), fill="green", style="dotted")
    logical_line(draw, p_chord, Point(r, p_chord.y), fill="blue", style="dotted")

    logical_dot(draw, c)
    logical_dot(draw, p)
    logical_dot(draw, p_chord, fill="gray")

    logical_graph(draw, lambda x: r*math.tan(theta - x + 1), left=boundary_x, fill="red")
    logical_graph(draw, lambda x: r*math.sin(theta - x + 1), left=boundary_x, fill="green")
    logical_graph(draw, lambda x: r*math.cos(theta - x + 1), left=boundary_x, fill="blue")

    draw.rectangle((0,0,87,52), fill="#FFFF88", outline="black")
    draw.text((5,  5), "Red: tangent", fill="red")
    draw.text((5, 20), "Green: sine", fill="green")
    draw.text((5, 35), "Blue: cosine", fill="blue")

    return img

images = []
for theta in range(0, 360, 6):
    print theta
    #this is stupid, but the range can't include 90 or 270, 
    #or else the tangent calculations will run forever.
    #so we'll use an offset of one.
    images.append(make_image(math.radians(theta+1)))
animation.make_gif(images, delay=4)