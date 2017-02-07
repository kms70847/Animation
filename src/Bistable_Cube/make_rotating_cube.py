from geometry import Point, distance, cross_product, dot_product
from itertools import product, combinations
from math import cos, sin, radians, acos, pi
from PIL import Image, ImageDraw
from collections import defaultdict
import animation
import cycle

IMG_SIZE = 400
MARGIN = 20

def angle_between(v1, v2):
    return acos(dot_product(v1, v2) / (v1.magnitude() * v2.magnitude()))

def memoize(fn):
    cache = {}
    def f_(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return f_

def rotate(v, k, theta):
    k = k.normalized()
    return v * cos(theta) + cross_product(k, v) * sin(theta) + k * (dot_product(k,v))*(1 - cos(theta))

@memoize
def get_unit_cube():
    points = [Point(x,y,z) for x,y,z in product((-1,1), repeat=3)]
    edges = []
    for i, a in enumerate(points):
        for j, b in enumerate(points):
            if i < j and distance(a,b) == 2:
                edges.append((i,j))

    assert len(edges) == 12, "expected 12 edges, got {}".format(len(edges))
    face_points = cycle.get_minimal_cycles(cycle.graph_from_edge_tuples(edges))
    faces = []
    for seq in face_points:
        face = []
        for i in range(len(seq)):
            j = (i+1)%len(seq)
            a,b = seq[i], seq[j]
            a,b = sorted((a,b))
            face.append(edges.index((a,b)))
        faces.append(face)
    assert len(faces) == 6

    normals = []
    for face in faces:
        corners = {points[p] for i in face for p in edges[i]}
        center = sum(corners, Point(0.,0.,0.)) / len(points)
        normals.append(center)

    return points, edges, faces, normals

def render(f, **kwargs):
    """kargs:
    interior_color - the color of the interior edges of the polyhedron. default: gray.
    exterior_color - the color of the exterior edges of the polyhedron. default: black.
    axis: - the principle axis of rotation. default: the x axis.
    """

    points, edges, faces, normals = get_unit_cube()

    faces_by_edge = defaultdict(list)
    for face_idx, face in enumerate(faces):
        for edge_idx in face:
            faces_by_edge[edge_idx].append(face_idx)

    axis = kwargs.get("axis", Point(1,0,0))

    theta = f * 90
    points = [rotate(p, axis, radians(theta)) for p in points]
    points = [rotate(p, Point(0,1,0), radians(45)) for p in points]

    normals = [rotate(p, axis, radians(theta)) for p in normals]
    normals = [rotate(p, Point(0,1,0), radians(45)) for p in normals]

    # min_x = min(p.x for p in points)
    # max_x = max(p.x for p in points)
    # min_y = min(p.y for p in points)
    # max_y = max(p.y for p in points)

    min_x = -2.
    max_x = 2.
    min_y = -2.
    max_y = 2.

    screen_min_x = 0
    screen_max_x = IMG_SIZE
    screen_min_y = 0
    screen_max_y = IMG_SIZE

    def project(p):
        def interpolate(x, L1, R1, L2, R2):
            return (((x - L1) / (R1 - L1)) * (R2 - L2)) + L2
        return Point(
            interpolate(p.x, min_x, max_x, screen_min_x, screen_max_x),
            interpolate(p.y, min_y, max_y, screen_min_y, screen_max_y),
        )

    points = map(project, points)

    margin = 20
    img = Image.new("RGB", (IMG_SIZE*2, IMG_SIZE*2), "white")
    draw = ImageDraw.Draw(img)

    edges_by_category = {"back": [], "front": [], "outline": []}
    camera_normal = Point(0,0,1)
    for edge_idx, edge in enumerate(edges):
        adjacent_faces = faces_by_edge[edge_idx]
        assert len(adjacent_faces) == 2
        adjacent_normals = [normals[i] for i in adjacent_faces]

        angles = [angle_between(n, Point(0,0,1)) for n in adjacent_normals]
        if all(angle_between(n, camera_normal) > radians(90) for n in adjacent_normals):
            edges_by_category["front"].append(edge)
        elif all(angle_between(n, camera_normal) <= radians(90) for n in adjacent_normals):
            edges_by_category["back"].append(edge)
        else:
            edges_by_category["outline"].append(edge)


    interior_color = kwargs.get("interior_color", "gray")
    exterior_color = kwargs.get("exterior_color", "black")
    for category, color in zip(("front", "outline"), (interior_color, exterior_color)):
        for i,j in edges_by_category[category]:
            a,b = points[i], points[j]
            a = a * 2
            b = b * 2
            draw.line(a.tuple() + b.tuple(), fill=color)

    return img.resize((IMG_SIZE, IMG_SIZE), Image.ANTIALIAS)

def get_frames(fn, num_frames, verbose=False):
    frames = []
    for i in range(num_frames):
        if verbose: print i,
        f = float(i) / num_frames
        frames.append(fn(f))
    return frames

def make_composite_image():
    white = (255,255,255)
    gray = (128,128,128)
    interpolate_scalar = lambda a,b,f: a*(1-f) + b*f
    interpolate_color = lambda a,b,f: tuple(int(interpolate_scalar(a_channel, b_channel,f)) for a_channel, b_channel in zip(a,b))
    ease = lambda f: sin(f * pi/2)

    frames = []

    ambiguous_rotation = get_frames(lambda f: render(f, interior_color="white"), 32)
    x_rotation = get_frames(lambda f: render( f, axis=Point(1,0,0)), 32)
    z_rotation = get_frames(lambda f: render(-f, axis=Point(0,0,1)), 32)
    x_rotation_fading_in  = get_frames(lambda f: render( f, axis=Point(1,0,0), interior_color=interpolate_color(white, gray, ease(f))), 32)
    x_rotation_fading_out = get_frames(lambda f: render( f, axis=Point(1,0,0), interior_color=interpolate_color(gray, white, ease(f))), 32)
    z_rotation_fading_in  = get_frames(lambda f: render(-f, axis=Point(0,0,1), interior_color=interpolate_color(white, gray, ease(f))), 32)
    z_rotation_fading_out = get_frames(lambda f: render(-f, axis=Point(0,0,1), interior_color=interpolate_color(gray, white, ease(f))), 32)
    
    frames.extend(ambiguous_rotation)
    frames.extend(x_rotation_fading_in)
    frames.extend(x_rotation)
    frames.extend(x_rotation_fading_out)
    frames.extend(ambiguous_rotation)
    frames.extend(z_rotation_fading_in)
    frames.extend(z_rotation)
    frames.extend(z_rotation_fading_out)
    return frames
    

frames = make_composite_image()
animation.make_gif(frames, delay=4)