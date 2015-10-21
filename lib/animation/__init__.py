#prerequisites: ImageMagick (http://www.imagemagick.org/script/index.php)
import itertools
import os
import os.path
import subprocess
import shutil
import math

def generate_unused_folder_name():
    base = "temp_{}"
    for i in itertools.count():
        name = base.format(i)
        if not os.path.exists(name):
            return name

def make_gif(imgs, **kwargs):
    """creates a gif in the current directory, composed of the given images.
    parameters:
     - imgs: a list of PIL image objects.
    optional parameters:
     - name: the name of the gif file. 
      - default: "output.gif"
     - delay: the number of 'ticks' between frames. 1 tick == 10 ms == 0.01 seconds. anything smaller than 2 will cause display problems. 
      - default: 2
     - delete_temp_files: True if the temporary directory containing each individual frame should be deleted, False otherwise.
      - default: True
    """
    name = kwargs.get("name", "output.gif")
    delay = kwargs.get("delay", 2)
    dir_name = generate_unused_folder_name()
    #create directory and move into it
    os.mkdir(dir_name)
    os.chdir(dir_name)
    

    #create images. Use leading zeroes to ensure lexicographic order.
    num_digits = max(1, int(math.log(len(imgs))))
    for i, img in enumerate(imgs):
        img.save("img_{:0{padding}}.png".format(i, padding=num_digits))

    #create gif
    #cmd = "imgconvert -delay {} img_*.png -layers optimize output.gif".format(delay)
    cmd = ["imgconvert", "-delay", str(delay), "img_*.png", "-layers", "optimize",  "output.gif"]
    subprocess.call(cmd)

    #move gif out of temp directory
    shutil.copyfile("output.gif", "../{}".format(name))

    #return to original directory, and delete temp
    os.chdir("..")
    if kwargs.get("delete_temp_files", True):
        shutil.rmtree(dir_name)