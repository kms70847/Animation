from geometry import Point
from PIL import Image, ImageDraw
from boundingbox import BoundingBox

def make_img(fractal):
    size = Point(200,200)
    
    bbox = BoundingBox(Point(0,0), size)

    im = Image.new("RGB", size.tuple(), "white")
    draw = ImageDraw.Draw(im)
    fractal.draw(draw, bbox)
    return im

def make_zoomed_img(fractal, amt, foci_idx=0):
    zoom = fractal.zoom_change ** amt
    size = Point(200,200)
    focus = fractal.foci[foci_idx]
    cam_center = Point(focus.x * size.x, focus.y * size.y)
    def transform(p):
        return ((p-cam_center)*zoom)+cam_center
    bbox = BoundingBox(transform(Point(0,0)), transform(size))

    im = Image.new("RGB", size.tuple(), "white")
    draw = ImageDraw.Draw(im)
    fractal.draw(draw, bbox)
    return im

def make_animation(fractal, frames, foci_idx=0):
    def frange(start, end, step):
        delta = end - start
        for i in range(step):
            frac = float(i) / step
            yield start + delta*frac
    return [make_zoomed_img(fractal, x, foci_idx) for x in frange(0,1, 16)]