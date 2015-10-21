import output
import animation
import itertools
from gridFractal import GridFractal

def chunk(seq):
    return (seq[0:3], seq[3:6], seq[6:9])

def flatten(grid):
    return grid[0] + grid[1] + grid[2]

def empty_grid():
    return [[False for _ in range(3)] for __ in range(3)]

value = lambda grid: sum(2**idx for idx, value in enumerate(flatten(grid)) if value)

def transformed(grid, mapping_func):
    ret = empty_grid()
    for i in range(3):
        for j in range(3):
            new_i, new_j = mapping_func(i,j)
            ret[new_j][new_i] = grid[j][i]
    return tuple(map(tuple,ret))

#flipping across the line y=x
flipped = lambda grid: transformed(grid, lambda i, j: (j, i))
#counterclockwise rotation
x = [
    [(2,0), (2,1), (2,2)],
    [(1,0), (1,1), (1,2)],
    [(0,0), (0,1), (0,2)]
]
rotated = lambda grid: transformed(grid, lambda i, j: x[j][i])

def alternatives(grid):
    def multi_rotated(grid, x):
        if x == 0: return grid
        return multi_rotated(rotated(grid), x-1)
    for i in range(4):
        cur = multi_rotated(grid, i)
        yield cur
        yield flipped(cur)

def canonical(grid):
    return sorted(alternatives(grid), key=value)[0]

def all_canonical():
    grids = set()
    for flat_grid in itertools.product([False, True], repeat=9):
        grid = chunk(flat_grid)
        assert len(grid) == 3
        assert len(grid[0]) == 3
        grid = canonical(grid)
        grids.add(grid)
    return grids

for grid in all_canonical():
    print value(grid)
    im = output.make_img(GridFractal(grid))
    im.save("all_grid_images/{}.png".format(value(grid)))