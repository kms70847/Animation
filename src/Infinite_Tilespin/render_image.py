from multiprocessing import Pool
from PIL import Image, ImageDraw
from geometry import Point, cross_product
import time
import math
import animation

"""
Renders a 3d scene.

The camera is at (0, CAMERA_Y, 0).

the center of the viewing frame is at (0, VIEWING_Y, VIEWING_Z). 
It is axis-aligned and perpendicular to the Z axis. 
Its dimensions are defined by VIEWING_WIDTH and VIEWING_HEIGHT.

The surface plane lies on the origin and is perpendicular to the Y axis.
"""
WIDTH  = 200
HEIGHT = 200

ANTIALIASED = True
if ANTIALIASED:
    WIDTH *= 2
    HEIGHT *= 2

CAMERA_Y = 2
VIEWING_Y = CAMERA_Y - 1/2. - 1/8.
VIEWING_Z = 1/2.
VIEWING_WIDTH = 1
VIEWING_HEIGHT = 1

def generate_intersection_data():

    intersection_data = {}

    for i in range(WIDTH):
        for j in range(HEIGHT):
            x = (i - WIDTH  / 2.) * 2 * VIEWING_WIDTH  / WIDTH
            y = (j - HEIGHT / 2.) * 2 * VIEWING_HEIGHT / HEIGHT + VIEWING_Y
            z = VIEWING_Z
            
            #`pos = p1 * (1-t) + p2*t` describes the path of a particle traveling in a straight line, passing through p1 at time t=0 and p2 at time t=1.
            #using the camera as p1 and the current view frame point as p2, we want to find the position where the particle passes through the surface plane.

            #first, solve for t, given the y coordinates of each point.
            if CAMERA_Y == y:    #particle travels parallel to surface plane.
                t = None
            else:
                t = CAMERA_Y / (CAMERA_Y - y)

            #then solve for x and z, provided an intersection actually occurs.
            if t <= 0 or t is None:
                surface_x = None
                surface_z = None
            else:
                #this simplifies nicely thanks to our camera being above the origin.
                surface_x  = x*t
                surface_z = z*t

            intersection_data[i,j] = {"x": surface_x, "z": surface_z, "t": t}

    return intersection_data

def generate_intersection_data():
    intersection_data = {}
    look_at = Point(0, -2, 3).normalized()
    right = Point(1,0,0)
    up = cross_product(look_at, right).normalized()
    camera_pos = Point(0, CAMERA_Y, 0)

    #prefetch these values so that we don't have to do them inside the doubly-nested loop
    r_vals = [right*(i-WIDTH/2. ) * 2 * VIEWING_WIDTH  / WIDTH  for i in range(WIDTH)]
    u_vals = [up   *(j-HEIGHT/2.) * 2 * VIEWING_HEIGHT / HEIGHT for j in range(HEIGHT)]

    for i in range(WIDTH):
        print i,
        for j in range(HEIGHT):
            p = camera_pos + look_at + r_vals[i] + u_vals[j]
            x,y,z = p.x, p.y, p.z

            if CAMERA_Y == y:    #particle travels parallel to surface plane.
                t = None
            else:
                t = CAMERA_Y / (CAMERA_Y - y)

            #then solve for x and z, provided an intersection actually occurs.
            if t <= 0 or t is None:
                surface_x = None
                surface_z = None
            else:
                #this simplifies nicely thanks to our camera being above the origin.
                surface_x  = x*t
                surface_z = z*t

            intersection_data[i,j] = {"x": surface_x, "z": surface_z, "t": t}

    return intersection_data

def ease(f):
    return math.sin(f*math.pi/2)

def render_template_image(f):
    def render_single_quarter_rotation(f, bg_color, fg_color):
        f = ease(ease(f))
        img = Image.new("RGB", (256, 256), bg_color)
        draw = ImageDraw.Draw(img)
        radius = 128
        theta = f * math.pi / 2
        coords = [(128 + radius*math.cos(theta+delta), 128 + radius*math.sin(theta+delta)) for delta in map(math.radians, (0, 90, 180, 270))]
        draw.polygon(coords, fill=fg_color)
        return img
    f *= 2
    if f < 1:
        return render_single_quarter_rotation(f%1, "white", "black")
    else:
        img = render_single_quarter_rotation(f%1, "black", "white")
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        old_pix = img.load()
        new_img = img.copy()
        new_pix = new_img.load()
        for i in range(256):
            for j in range(256):
                new_pix[i,j] = old_pix[(
                    (i+128) % 256,
                    (j+128) % 256
                )]
        return new_img

def render_projected_image(template_image, intersection_data):
    def attenuate(color, distance):
        def lerp(a,b, f):
            return a + f*(b-a)
        max_distance = 20
        distance = min(distance, max_distance)
        f = math.sin(math.pi * distance / max_distance / 2)
        return tuple(int(lerp(channel, 0xA0, f)) for channel in color)

    white = (255,255,255)
    black = (0,0,0)
    blue = (0x80,0x80,0xA0)

    template_pix = template_image.load()
    def get_color(x,y):
        x *= template_image.size[0]
        y *= template_image.size[0]
        return template_pix[int(x), int(y)]


    img = Image.new("RGB", (WIDTH, HEIGHT), white)
    pix = img.load()
    for i,j in intersection_data:
        x,z,t = map(intersection_data[i,j].get, "xzt")
        if x is None:
            color = blue
        else:
            color = attenuate(get_color(x%1, z%1), t)
        pix[i,HEIGHT-j-1] = color

    #print("Completed color picking.")

    if ANTIALIASED:
        img = img.resize((WIDTH/2, HEIGHT/2), Image.ANTIALIAS)
        img = Image.eval(img, lambda x: x-x%2)

    return img

def render_image(f, intersection_data):
    return render_projected_image(render_template_image(f), intersection_data)

#compatibility shim because 2.7 doesn't implement this
def starmap(pool, func, iterable, verbose=False):
    def callback(x):
        if verbose: print ".",
    async_results = []
    for i, item in enumerate(iterable):
        async_results.append(pool.apply_async(func, item, callback=callback))
    return [item.get() for item in async_results]

def main(use_multicore = True):
    intersection_data = generate_intersection_data()
    num_frames = 64

    f_values = [float(i)/num_frames for i in range(num_frames)]
    if use_multicore:
        arguments = [(f, intersection_data) for f in f_values]
        print("Starting pool...")
        pool = Pool()
        frames = starmap(pool, render_image, arguments, verbose=True)
        print("Pool complete.")

    else:
        frames = []
        for i, f in enumerate(f_values):
            print i,
            frames.append(render_image(f, intersection_data))

    animation.make_gif(frames)

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("Completed in {} second(s).".format(time.time() - start_time))
