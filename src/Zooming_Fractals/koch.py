from fractal import Fractal
from geometry import Point, midpoint, distance
import math

def from_degrees(angle):
    return math.pi* 2 * angle / 360

def rotated_about(p, center, theta):
    radius = distance(p, center)
    angle = math.atan2(p.y - center.y, p.x - center.x)
    angle += theta
    dx = radius * math.cos(angle)
    dy = radius * math.sin(angle)
    return center + Point(dx, dy)


class Koch(Fractal):
    def __init__(self):
        self.zoom_change = 3
        self.left = Point(0,0)
        self.right = Point(1,0)
        self.foci = [midpoint(self.left, self.right) + Point(0, math.tan(from_degrees(60))/6)]
    def draw(self, im_draw, bbox):
        def koch(start, end, depth):
            if depth == 1:
                im_draw.line(start.tuple() + end.tuple(), fill="black")
            else:
                #transform the line into a collection of four line segments.
                #Resembling this: _/\_
                a = start
                e = end
                b = midpoint(a,e, 1/3.0)
                d = midpoint(a,e, 2/3.0)
                #b,c, and d form an equilateral triangle,
                #so we only need to rotate d about b by 30 degrees to get c.
                c = rotated_about(d, b, from_degrees(60))
                points = [a,b,c,d,e]
                for start, end in zip(points, points[1:]):
                    koch(start, end, depth-1)
        start, end = self.rebased(self.left, bbox), self.rebased(self.right, bbox)
        koch(start, end, 6)