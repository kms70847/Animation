from fractal import Fractal
from geometry import Point
from boundingbox import BoundingBox

def product(max):
    """cartesian product of range(max) and range(max)"""
    for i in range(max):
        for j in range(max):
            yield (i,j)

class GridFractal(Fractal):
    def __init__(self, grid):
        """
            initializes the GridFractal object.
            `grid` is a 3x3 list of boolean values indicating which cells of the grid will be filled.
        """
        self.grid = grid
        self.foci = []
        for i, j in product(3):
            if self.grid[j][i]:
                self.foci.append(Point(i/2.0, j/2.0))

        #we'll make the center foci the first one, if it exists
        if self.grid[1][1]:
            self.foci.remove(Point(1/2.0, 1/2.0))
            self.foci.insert(0, Point(1/2.0, 1/2.0))

        self.zoom_change = 3
    def draw(self, im_draw, bbox):
        def draw_grid(depth, bbox):
            if depth == 1:
                im_draw.rectangle(bbox.tuple(), fill="black")
            else:
                width = bbox.width/3.0
                height = bbox.height/3.0
                for i, j in product(3):
                    if not self.grid[j][i]: continue
                    left = bbox.left + width*i
                    top = bbox.top + height*j
                    child_bbox = BoundingBox(left, top, left+width, top+height)
                    draw_grid(depth-1, child_bbox)
        draw_grid(6, bbox)