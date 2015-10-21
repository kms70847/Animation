from fractal import Fractal
from geometry import Point, midpoint
import math

class Sierpinsky(Fractal):
    def __init__(self):
        self.zoom_change = 2
        #use this height for the largest isoceles triangle that can fit in the bounding box.
        #height = 1
        #use this height for an equilateral triangle.
        height = math.sqrt(3)/2
        self.foci = [Point(0.5, math.sqrt(3)/2), Point(0,0), Point(1, 0)]
    def draw(self, im_draw, bbox):
        def sier(depth, a, b, c):
            def tri(a,b,c):
                def line(start, end):
                    im_draw.line([start.tuple(), end.tuple()], fill="black")
                line(a,b); line(b,c); line(c,a)
            if depth == 1:
                tri(a,b,c)
            else:
                sier(depth-1, a, midpoint(a,b), midpoint(c,a))
                sier(depth-1, b, midpoint(b,c), midpoint(a,b))
                sier(depth-1, c, midpoint(c,a), midpoint(b,c))
        a = self.rebased(self.foci[0], bbox)
        b = self.rebased(self.foci[1], bbox)
        c = self.rebased(self.foci[2], bbox)
        sier(8, a, b, c)
