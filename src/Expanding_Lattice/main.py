from geometry import Point, exp
import math
from PIL import Image, ImageDraw
import animation

class Lattice:
    """A uniform distribution of points in 2d space.
    given a point `o` and two linearly independent vectors `u`, `v`:
        `o+ m*u + n*v` represents every point in the lattice, for any integers m and n.
    """
    def __init__(self, o, u, v):
        self.o = o
        self.u = u
        self.v = v
    def __mul__(self, a):
        return Lattice(self.o, self.u*a, self.v*a)
    def get(self, m, n):
        return self.o + m*self.u + n*self.v
    def points_within(self, rect):
        if self.o not in rect:
            raise Exception("not implemented yet for rects not containing o")
        #pretty standard flood fill search. we'll use (m,n) tuples because it's easier to find neighbors that way.
        def neighbors(tup):
            m,n = tup
            return [(m-1,n),(m,n-1),(m+1,n),(m,n+1)]
        seen = set()
        to_visit = {(0,0)}
        while to_visit:
            cur = to_visit.pop()
            seen.add(cur)
            p = self.get(*cur)
            if p in rect:
                yield p
                for neighbor in neighbors(cur):
                    if neighbor not in seen:
                        to_visit.add(neighbor)

class Rect:
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
    def with_margin(self, m):
        return Rect(self.x1-m, self.x2+m, self.y1-m, self.y2+m)
    def __contains__(self, p):
        def lies_within(a,b,x):
            if a > b: a,b = b,a
            return a <= x <= b
        return lies_within(self.x1, self.x2, p.x) and lies_within(self.y1, self.y2, p.y)

def iter_cycle(seq):
    for i, x in enumerate(seq):
        yield (x, seq[(i+1) % len(seq)])

def rotated(vector, angle):
    return exp(vector.angle()+angle, vector.magnitude())

window_size = 800 #will halve this later for antialiasing purposes
def render(f, lattice):
    theta = math.radians(45*f)
    square_radius = math.sqrt(2) * math.sin(math.pi/2 - theta) * lattice.u.magnitude()/2
    corner_deltas = [exp(radius=square_radius, angle=theta+lattice.u.angle()+math.radians(45+ 90*x)) for x in range(4)]

    img = Image.new("RGB", (window_size, window_size), "white")
    draw = ImageDraw.Draw(img)
    r = Rect(0,window_size, 0,window_size)
    for p in lattice.points_within(r.with_margin(lattice.u.magnitude())):
        corners = [p + delta for delta in corner_deltas]
        for a,b in iter_cycle(corners):
            draw.line(a.tuple()+b.tuple(), fill="black")
    return img

def ease(f):
    return math.sin(f * math.pi / 2)

frames = []
num_frames = 80

d = 80
origin = Point(window_size/2, window_size/2)
lattice = Lattice(origin, Point(0,d), Point(d,0))

for s in range(2):
    for i in range(num_frames):
        print i,
        f = float(i)/num_frames
        q = float(num_frames*s + i) / (num_frames*2)
        z = 2**q
        frames.append(render(ease(f), lattice*z))

    lattice.u = rotated(lattice.u, math.radians(45)) / math.sqrt(2)
    lattice.v = rotated(lattice.v, math.radians(45)) / math.sqrt(2)

frames = [frame.resize((window_size/2, window_size/2), Image.ANTIALIAS) for frame in frames]

animation.make_gif(frames)