from geometry import Point

class Fractal:
    def __init__(self):
        #difference in zoom between one level and another
        self.zoom_change = 2
        
        #points of self-similarity. zooming in on one of them will reveal the whole part again.
        #point coordinates should be between 0 and 1, inclusive. Act as though the fractal were being drawn on the quadrant 1 unit square.
        self.foci = []
        
    def rebased(self, p, bbox):
        """Given a point p in the quadrant 1 unit square, transforms it so that it lies in the bounding box."""
        x = bbox.left + p.x*bbox.width
        y = bbox.top  + p.y*bbox.height
        return Point(x,y)
    def draw(self, im_draw, bbox):
        """draws the fractal on the given ImageDraw instance, within the given bounding box."""
        raise Exception("Not implemented in abstract base class")