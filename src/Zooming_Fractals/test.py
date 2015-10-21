import output
import animation
import itertools

from koch import Koch
from gridFractal import GridFractal
from sierpinsky import Sierpinsky

def exists(filename):
    try:
        file = open(filename)
        file.close()
        return True
    except:
        return False

fractals = {
    "koch": lambda: Koch(),
    "sierpinsky": lambda: Sierpinsky(),
    "grid_plus": lambda: GridFractal([[False, True, False],[True, True, True],[False, True, False]]),
    "grid_h": lambda: GridFractal([[True, False, True],[True, True, True],[True, False, True]]),
    "grid_t": lambda: GridFractal([[False, True, False],[False, True, False],[True, True, True]]),
    "grid_o": lambda: GridFractal([[False, True, True],[True, True, True],[True, True, False]]),
}

for key in sorted(fractals.keys()):
    filename = key + ".gif"
    if exists(filename):
        print "Already exists:\t{}".format(filename)
    else:
        fractal = fractals[key]()
        imgs = output.make_animation(fractal, 16)
        animation.make_gif(imgs, name=filename)
        print "created:\t{}.".format(filename)