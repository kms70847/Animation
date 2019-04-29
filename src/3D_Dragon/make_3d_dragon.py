import numpy as np
import math
from PIL import Image, ImageDraw
import animation

NUM_GENERATIONS = 13
NUM_FRAMES = 64

def apply_l_system(tokens, rules):
    return [result_token for token in tokens for result_token in rules[token]]

def get_rotation_matrix(axis_name, theta):
    c = math.cos(theta)
    s = math.sin(theta)
    mats = {
        "x": [[1,0,0],[0,c,-s],[0,s,c]],
        "y": [[c,0,s],[0,1,0],[-s,0,c]],
        "z": [[c,-s,0],[s,c,0],[0,0,1]]
    }
    return np.array(mats[axis_name])

def chunk(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i: i+size]

rules = {
    'Fu': ('Fl', 'Lu'), 'Fd': ('Fr', 'Rd'), 'Fl': ('Fd', 'Dl'), 'Fr': ('Fu', 'Ur'), 
    'Bu': ('Br', 'Ru'), 'Bd': ('Bl', 'Ld'), 'Bl': ('Bu', 'Ul'), 'Br': ('Bd', 'Dr'), 
    'Uf': ('Ur', 'Rf'), 'Ub': ('Ul', 'Lb'), 'Ul': ('Uf', 'Fl'), 'Ur': ('Ub', 'Br'), 
    'Df': ('Dl', 'Lf'), 'Db': ('Dr', 'Rb'), 'Dl': ('Db', 'Bl'), 'Dr': ('Df', 'Fr'), 
    'Lf': ('Lu', 'Uf'), 'Lb': ('Ld', 'Db'), 'Lu': ('Lb', 'Bu'), 'Ld': ('Lf', 'Fd'), 
    'Rf': ('Rd', 'Df'), 'Rb': ('Ru', 'Ub'), 'Ru': ('Rf', 'Fu'), 'Rd': ('Rb', 'Bd')
}

unit_vectors = {'F': (0, 0, 1), 'B': (0, 0, -1), 'U': (0, 1, 0), 'D': (0, -1, 0), 'L': (-1, 0, 0), 'R': (1, 0, 0), 'O': (0, 0, 0)}

#generate system
s = ["Fu"]
for _ in range(NUM_GENERATIONS):
    s = apply_l_system(s, rules)

#calculate direction and magnitude of each step in walk
walk_steps = [(0,0,0)]
for token in s:
    walk_steps.append(unit_vectors[token[0]])

#calculate coordinates of walk
coords = np.cumsum(walk_steps, 0)

#rotate coordinates so it makes a complete revolution per cycle
frame_coords = []
print("Applying rotations to canonical coordinates.")
for i in range(NUM_FRAMES):
    print(f"{i+1} / {NUM_FRAMES}")
    f = float(i) / NUM_FRAMES
    m = get_rotation_matrix("x", math.radians(-10))
    m = m @ get_rotation_matrix("y", f * 2 * math.pi)
    frame_coords.append(coords @ m.T)

#concatenate all frames and convert to pixel coordinates.
all_coords = np.concatenate(frame_coords)

margin = 10
total_size = 250
operable_size = total_size - margin*2

#determine ratio between logical space and pixel space.
left = min(all_coords[:,0])
right = max(all_coords[:,0])
top = min(all_coords[:,1])
bottom = max(all_coords[:,1])
ratio = max(right-left, bottom-top)/operable_size
print(left, right, top, bottom)

all_coords = ((all_coords - [left, top, 0]) / ratio) + margin

#chunk into individual frames and render
images = []
print("Rendering frames.")
for frame_idx, frame_coord in enumerate(chunk(all_coords, len(coords))):
    print(f"{frame_idx+1} / {NUM_FRAMES}")
    img = Image.new("RGB", (total_size, total_size), "white")
    draw = ImageDraw.Draw(img)
    for i in range(len(frame_coord)-1):
        x1,y1,_ = frame_coord[i]
        x2,y2,_ = frame_coord[i+1]
        draw.line((x1,y1,x2,y2), fill="black")
    images.append(img)

print("Creating gif.")
animation.make_gif(images, delay=4)