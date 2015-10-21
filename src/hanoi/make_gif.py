from PIL import Image, ImageDraw
from geometry import Point
import math
import hanoi
import animation
import path

def add_progress_bar(imgs, **kargs):
    """adds a progress bar to the bottom of each image"""
    def vert_stitch(a, b):
        """combines two images top to bottom"""
        width = max(a.size[0], b.size[0])
        height = a.size[1] + b.size[1]
        im = Image.new("RGB", (width, height), "white")
        im.paste(a, (0,0))
        im.paste(b, (0, a.size[1]))
        return im
    def create_progress_bar(width, height, frac, bg_color, fore_color, border_color):
        im = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(im)
        draw.rectangle([0,0, width-1, height-1], outline=border_color)
        fore_width = int(frac*(width-2))
        draw.rectangle([1,1, fore_width, height-2], outline=fore_color, fill=fore_color)
        return im
    
    ret = []
    height = kargs.get("height", 10)
    for i, img in enumerate(imgs):
        frac = float(i) / (len(imgs)-1)
        bar = create_progress_bar(img.size[0], height, frac, "white", "blue", "black")
        ret.append(vert_stitch(img, bar))
    return ret
    
def circle(draw, center, radius, **options):
    """draws a circle on the given drawing surface."""
    center = center.map(int)
    ul = center - Point(radius, radius)
    dr = center + Point(radius, radius)
    draw.chord(ul.tuple()+dr.tuple(), 0, 360, **options)

def from_degrees(angle):
    """converts degrees to radians."""
    return 2 * math.pi * angle / 360

def from_radial(angle, radius):
    """finds the x and y values for a point on the unit circle with the given angle and radius"""
    x = math.cos(angle)*radius
    y = math.sin(angle)*radius
    return Point(x,y)

def frange(start, end, steps):
    """
    yields `steps` values evenly distributed between (start, end].
    ex. frange(0, 1, 4) gives [0, 0.25, 0.50, 0.75]
    """
    frac = (end - start) / float(steps)
    for i in range(steps):
        yield start + i*frac    

def flip_y(im):
    """mirrors an image over the x axis."""
    source_pix = im.load()
    im = im.copy()
    dest_pix = im.load()
    width, height = im.size
    for i in range(width):
        for j in range(height):
            dest_pix[i,j] = source_pix[i, height-j-1]
    return im

def rounded_corner_path(start_x, end_x, min_y, max_y):
    """creates a U shaped path between the start and end points."""
    if start_x > end_x:
        return rounded_corner_path(end_x, start_x, min_y, max_y).reversed()
    radius = min(max_y - min_y, (end_x - start_x)/2)
    paths = []
    #first curve
    paths.append(path.ChordPath(Point(start_x+radius, min_y), radius, from_degrees(180), from_degrees(90)))
    #linear path between first and second curve, if it exists
    if radius * 2 <= end_x - start_x:
        y = min_y + radius
        left = start_x + radius
        right = end_x - radius
        paths.append(path.LinearPath(Point(left, y), Point(right, y)))
    #second curve
    paths.append(path.ChordPath(Point(end_x-radius, min_y), radius, from_degrees(90), from_degrees(0)))
    return path.CompositePath(paths)

def make_img(pegs, free_ring=None, source=None, dest=None, frac=None):
    """
    pegs - a list of lists of integers representing the size of the rings on each peg.
    free_ring - the size of the ring that is currently moving, or `None` if no ring is moving.
    source - the index of the peg the free ring is traveling from.
    dest - the index of the peg the free ring is traveling to.
    frac - the distance the free ring has traveled. ranges between 0 and 1.
    """
    #recommended: make all integer constants even. Most of these will be divided by two at some point, and we don't want any rounding errors.

    #difference in width of two rings whose size varies by one (ex. a ring of size 3 vs a ring of size 4)
    ring_delta = 10
    ring_height = 10
    rings = [ring for tower in pegs for ring in tower]
    if free_ring != None: rings.append(free_ring)

    #distance between pegs that both contain the widest ring.
    margin = 10
    peg_width = 10
    peg_height = ring_height * (len(rings) + 1)

    ring_width = lambda size: peg_width + size*ring_delta    
    max_ring_width = max(ring_width(ring) for ring in rings) if rings else ring_width(0)
    peg_center = lambda i: max_ring_width/2 + (i* (max_ring_width + margin)) + margin
    free_ring_radius = (peg_center(1) - peg_center(0))/2

    width = (max_ring_width + margin) * len(pegs) + margin
    height = peg_height + margin + free_ring_radius


    ring_style = {"outline": "black", "fill": "white"}
    peg_style = {"outline": "black", "fill": "black"}
    bg_color = "white"

    im = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(im)


    #draw pegs
    for i in range(len(pegs)):
        x = peg_center(i) - peg_width / 2
        draw.rectangle((x, 0, x+peg_width, peg_height), **peg_style)

    #draw rings
    for i, peg in enumerate(pegs):
        for j, ring in enumerate(peg):
            x = peg_center(i) - ring_width(ring)/2
            y = ring_height*j
            draw.rectangle((x, y, x+ring_width(ring), y+ring_height), **ring_style)

    #free ring
    if free_ring != None:
        #construct the Path that the free ring is taking. the center of the ring passes through the path.
        first_open_pos = lambda peg: Point(peg_center(peg), ring_height * (0.5 + len(pegs[peg])))
        top = lambda peg: Point(peg_center(peg), peg_height)
        path_segments = []
        #traveling to the top of the source peg
        path_segments.append(path.LinearPath(first_open_pos(source), top(source)))
        #curve over
        path_segments.append(rounded_corner_path(peg_center(source), peg_center(dest), top(source).y, top(source).y + free_ring_radius))
        #traveling to the base of the dest peg
        path_segments.append(path.LinearPath(top(dest), first_open_pos(dest)))
        #construct path
        free_path = path.CompositePath(path_segments)
        
        #determine position of center of ring
        center = free_path.at(frac)
        left = center.x - ring_width(free_ring)/2
        bottom = center.y - ring_height/2
        
        #draw (finally!)
        draw.rectangle((left, bottom, left+ring_width(free_ring), bottom+ring_height), **ring_style)
        
    return flip_y(im)


def make_hanoi(size):
    size = 5
    imgs = [make_img(state.values()) for state in hanoi.iter_hanoi_state(0, 2, 1, size)]
    animation.make_gif(imgs, delay=15, name="hanoi_{}.gif".format(size))

def make_smooth_hanoi(size):
    if size > 6: raise Exception("ImageMagick cannot generate a gif of size {}".format(size))
    def state_diff(prev, cur):
        """
        identifies which ring has moved between the two states, and its source/dest.
        returns a (size, source, dest) tuple.
        """
        
        size = None
        for i in range(3):
            if len(prev[i]) < len(cur[i]):
                dest = i
            elif len(prev[i]) > len(cur[i]):
                source = i
                size = prev[i][-1]
        if size == None:
            raise Exception("No difference detected between states {} and {}".format(prev, cur))
        return (size, source, dest)
        
    imgs = []
    prev = None
    for state in hanoi.iter_hanoi_state(0, 2, 1, size):
        if prev: #create transition between prev and state
            assert sum(len(tower) for tower in prev.values()) == size, "expected prev of size {}, got {}".format(size, prev)
            free_ring, source, dest = state_diff(prev, state)
            prev[source].pop()
            for frac in frange(0,1,32):
                imgs.append(make_img(prev.values(), free_ring, source, dest, frac))
        imgs.append(make_img(state.values()))
        prev = state
    for i in range(10):
        imgs.append(imgs[-1])
    imgs = add_progress_bar(imgs)
    animation.make_gif(imgs, delay=2, name="smooth_hanoi_{}.gif".format(size))

make_smooth_hanoi(6)