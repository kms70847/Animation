import math
import animation
from math import sin, cos
from geometry import Point, dot_product, cross_product

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

def cyclic_pairs(seq):
    for i in range(len(seq)):
        j = (i+1) % len(seq)
        yield seq[i], seq[j]

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

def angle_3d(a,b):
    return math.acos(dot_product(a,b) / (a.magnitude() * b.magnitude()))

#finds the point of intersection of line ab and segment cd.
def line_segment_intersection(a,b,c,d):
    #a line can be expressed as the set of points p for which
    #(p - p0) dot n = 0
    #where p0 is a point on the line and n is a normal vector to the line.
    #the vector equation for a line segment is
    #p = f*c + (1-f)*d = f*c - f*d + d = f*(c-d) + d
    #where f is a number between 0 and 1 inclusive.
    #
    #(f*(c-d) + d - p0) dot n = 0
    #((f*(c-d)) dot n) - ((p0 - d) dot n) = 0
    #((f*(c-d)) dot n) = ((p0 - d) dot n)
    #f*((c-d) dot n) = ((p0 - d) dot n)
    #f = ((p0 - d) dot n) / ((c-d) dot n)
    p0 = a
    n = exp(1, (a-b).angle() + math.radians(90))
    f = dot_product(p0-d, n) / dot_product(c-d, n)
    if 0 <= f <= 1:
        return (c+d)*f - d
    return None

def segment_segment_intersection(a,b,c,d):
    p = line_segment_intersection(a,b,c,d)
    q = line_segment_intersection(c,d,a,b)
    if p is None or q is None:
        return None
    return p

def get_bbox(poly):
    return (
        min(p.x for p in poly),
        min(p.y for p in poly),
        max(p.x for p in poly),
        max(p.y for p in poly)
    )

def point_in_polygon(p, poly):
    bbox = get_bbox(poly)
    if p.x < bbox[0] or p.y < bbox[1] or p.x > bbox[2] or p.y > bbox[3]:
        return False
    far_away_point = Point(-100, 0)
    count = 0
    for a,b in cyclic_pairs(poly):
        x = segment_segment_intersection(far_away_point, p, a, b) 
        if x is not None:
            count += 1
    return count %2 == 1

def lies_behind(p, poly):
    #draw a line from the viewer's position to p, and see if it intersects the plane formed by poly.
    #formula courtesy of https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
    a,b,c = poly
    n = cross_product(b-a, c-a)
    p0 = a
    l = Point(0,0,1)
    l0 = p

    if dot_product(l,n) == 0: 
        #I think this only happens when the poly is viewed edge-on.
        return False
    d = dot_product(p0 - l0, n) / dot_product(l,n)
    return d < 0

def flattened(p):
    return Point(p.x, p.y)
def is_occluded_by(p, poly):
    p = flattened(p)
    poly = map(flattened, poly)
    return point_in_polygon(p, poly)
    

def make_frame(f):
    def get_torus_point(big_r, little_r, theta, iota):
        return Point(
            (big_r + little_r * cos(theta)) * cos(iota),
            (big_r + little_r * cos(theta)) * sin(iota),
            little_r*sin(theta)
        )
    big_r = 0.66
    little_r = 0.33
    points = []
    normals = []
    slices = []
    minor_resolution = 16
    major_resolution = 32
    minor_offset = -f*2*math.pi/minor_resolution
    major_offset = f*2*math.pi/major_resolution
    for theta in frange(minor_offset, minor_offset+2*math.pi, 2*math.pi / minor_resolution):
        slice = []
        for iota in frange(major_offset, major_offset+2*math.pi, 2*math.pi / major_resolution):
            adjusted_iota = iota + theta/major_resolution
            p = get_torus_point(big_r, little_r, theta, adjusted_iota)
            shell_p = get_torus_point(big_r, little_r+1, theta, adjusted_iota)
            normal = shell_p - p
            points.append(p)
            normals.append(normal)
            slice.append(p)
        slices.append(slice)

    polys = []
    for slice_a, slice_b in cyclic_pairs(slices):
        for (a,b),(c,d) in zip(cyclic_pairs(slice_a), cyclic_pairs(slice_b)):
            polys.append((a,b,c))
            polys.append((d,b,c))

    size = 800
    margin = 50
    to_screen = lambda s: int(((s+1)/2.0)*(size-margin*2)) + margin

    rotations = [
        (math.radians(-45), "x"),
        (math.radians(45), "y")
    ]

    for angle, axis in rotations:
        points =  [planar_rotated(p, angle, axis) for p in points]
        normals = [planar_rotated(p, angle, axis) for p in normals]
        polys =  [[planar_rotated(p, angle, axis) for p in poly  ] for poly in polys]

    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    dot_size_resolution = 6
    dot_size = lambda z: dot_size_resolution-math.floor(((z + 1)/2)*dot_size_resolution)

    for idx, (p,n) in enumerate(zip(points, normals)):
        #print "{} / {}\r".format(idx, len(points)),

        #backface culling
        angle = angle_3d(n, Point(0,0,1))
        if angle < math.radians(90): continue

        #occlusion culling
        # if any(lies_behind(p, poly) and not any(p == vertex for vertex in poly) and is_occluded_by(p, poly) for poly in polys ):
           # continue

        
        #0 for points directly facing the camera, 1 for ones perpendicular
        magnitude = (angle - math.radians(180)) / math.radians(-90)
        #magnitude = magnitude ** 1/3.0
        x = int(255*magnitude)
        color = "#{:02x}{:02x}{:02x}".format(x,x,x)

        dot(draw, p.map(to_screen), dot_size(p.z), fill=color)

    draw_edges = False
    if draw_edges:
        for poly in polys:
            for a,b in cyclic_pairs(poly):
                draw.line(flattened(a.map(to_screen)).tuple() + flattened(b.map(to_screen)).tuple(), fill="black")
    return img.resize((size/2, size/2), Image.ANTIALIAS)


images = []
frames = 40
for i in range(frames):
    print i
    images.append(make_frame(float(i)/frames))

animation.make_gif(images)

#make_frame(0).save("output.png")