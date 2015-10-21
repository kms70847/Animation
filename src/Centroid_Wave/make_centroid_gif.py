import math
from PIL import Image, ImageDraw
import animation

images = []
frames = 63

def circle(draw, center, radius, **options):
    draw.chord((center[0]-radius, center[1] - radius, center[0]+radius, center[1] + radius), 0, 359, **options)


size = 800
circle_radius = 20
dot_radius = 3
distance_between_centers = 28

#number of circles you need to traverse until you find a circle with the same rotation as your starting point.
#must be even to make the last frame stitch properly to the first one.
#frames % (rotational_period / 2) should equal zero if you want to 
rotational_period = 14
angle_delta = math.radians(360/rotational_period)

def iter_circle_centers(f):
    circles_per_row = int(1 + math.ceil(float(size) / distance_between_centers))
    for i in range(-circles_per_row, circles_per_row):
        for j in range(circles_per_row*2):
            x = int((i + f*rotational_period/2) * distance_between_centers)
            y = int((j - f*rotational_period/2) * distance_between_centers)
            yield i,j,x, y
    

#we don't have to render all the frames because it repeats after this many frames
if frames % (rotational_period / 2) == 0:
    max_frame = frames/(rotational_period/2)
else:
    print "frames does not divide rotational period; rendering full sequence"
    max_frame = frames

for t in range(max_frame):
    f = float(t) / frames
    print t,
    theta = math.radians(360 * f)



    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    for i,j, x, y in iter_circle_centers(f):
        circle(draw, (x, y), circle_radius, outline="gray")

    #we need two loops so the dots always render in front of the circles
    for i,j, x, y in iter_circle_centers(f):
        angle = angle_delta * (i-j)
        dot_x = int(x + math.cos(theta+angle) * circle_radius)
        dot_y = int(y + math.sin(theta+angle) * circle_radius)
        circle(draw, (dot_x, dot_y), dot_radius, outline="black", fill="black")

    #draw.rectangle((0,0, int(size*f), 5), fill="red")
    
    img = img.resize((size/2, size/2), Image.ANTIALIAS)
    images.append(img)

animation.make_gif(images, delay=4, name="output.gif")