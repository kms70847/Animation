from math import sqrt

#Courtesy of Aran-Fey https://chat.stackoverflow.com/transcript/message/47258396#47258396
def circle_octant(r):
    r2 = r ** 2
    
    y = 0
    while y <= r:
        x = sqrt(r2 - y**2)
        
        if x-int(x) >= 0.5:
            x += 1
        else:
            # If we moved left, find out which adjacent pixel
            # the circle moved through - either the one to the
            # left or the one above (or neither?).
            # To do this, we calculate the x coordinate in the
            # center between the current pixel and the one below.
            x2 = sqrt(r2 - (y-0.5)**2)
            if x2 < int(x)+0.5:
                yield int(x), y-1
            else:
                yield int(x)+1, y
        
        x = int(x)
        
        yield x, y
        
        if x <= r//2:
            break
        
        y += 1
        

#Courtesy of Aran-Fey https://chat.stackoverflow.com/transcript/message/47258396#47258396
def circle_coords(x, y, r):
    for h, v in circle_octant(r):
        yield x+h, y+v
        yield x-h, y+v
        yield x+h, y-v
        yield x-h, y-v
        yield x+v, y+h
        yield x-v, y+h
        yield x+v, y-h
        yield x-v, y-h


def brush(g, r):
    """
    draws over an iterable of coordinates using a square "brush" of side length 1+2*r
    """
    for x,y in g:
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                yield dx+x, dy+y
    

from PIL import Image, ImageDraw

SIZE = 500
def render_echo_chamber(r):
    def screen_circle(center, r, **style):
        x,y = center
        draw.chord((x-r,y-r, x+r,y+r), 0, 359, **style)
    def logical_circle(center, r, **style):
        logical_x, logical_y = center
        screen_x = (logical_x + 0.5) * SIZE
        screen_y = (logical_y + 0.5) * SIZE
        screen_r = r * SIZE
        screen_circle((screen_x, screen_y), screen_r, **style)
        

    img = Image.new("RGB", (SIZE, SIZE), "white")
    draw = ImageDraw.Draw(img)
    if r <= 0.5:
        logical_circle((0, 0), r, outline="black")
    else:
        tiles = set(brush(circle_coords(0,0,r), 2))
        for x,y in tiles:
            logical_circle((x,y), r, outline="black")
    return img

def frange(start, stop, steps):
    for i in range(steps+1):
        f = i / float(steps)
        yield start+(f * (stop-start))

import animation
max_radius = 8
frames_per_radius = 64
frames = []
for f in frange(0, max_radius, frames_per_radius*max_radius):
    print(f)
    frames.append(render_echo_chamber(f))
animation.make_gif(frames, delay=8, delete_temp_files=True)