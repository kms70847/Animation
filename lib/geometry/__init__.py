import math

class Point(object):
    def __init__(self, *args, **kargs):
        self.num_dimensions = kargs.get("num_dimensions", len(args))
        self.coords = [0 for i in range(self.num_dimensions)]
        for i in range(len(args)):
            self.coords[i] = args[i]

    """Gives the distance from this point to the origin."""
    def magnitude(self):
        return math.sqrt(sum(c*c for c in self.coords))

    """
    Gives the angle of this point above the x axis.
    Measured in radians.
    Ranges between -pi and pi.
    """
    def angle(self):
        assert self.num_dimensions == 2
        assert self.x != 0 or self.y != 0
        return math.atan2(self.y,self.x)
    def tuple(self):
        return tuple(self.coords)
    def map(self, func):
        new_coords = [func(a) for a in self.coords]
        return Point(*new_coords)
    def _applyVectorFunc(self, other, f):
        assert self.num_dimensions == other.num_dimensions
        new_coords = [f(a,b) for a,b in zip(self.coords, other.coords)]
        return Point(*new_coords)
    def _applyScalarFunc(self, val, f):
        return self.map(lambda a: f(a,val))
        """
        new_coords = [f(a, val) for a in self.coords]
        return Point(*new_coords)
        """

    def normalized(self):
        return self.__div__(self.magnitude())

    def __add__(self, other):
        return self._applyVectorFunc(other, lambda a,b: a+b)
    def __sub__(self, other):
        return self._applyVectorFunc(other, lambda a,b: a-b)
    def __mul__(self, a):
        return self._applyScalarFunc(a, lambda b,c: b*c)
    def __div__(self, a):
        return self._applyScalarFunc(a, lambda b,c: b/c)
    
    def __eq__(self, other):
        try:
            return self.num_dimensions == other.num_dimensions and self.coords == other.coords
        except:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    #simple comparator for sorting purposes
    def __lt__(self, other):
        if not isinstance(other, Point): raise Exception("can only compare points to points")
        return self.coords < other.coords
    
    def __getattr__(self, name):
        if name == "x": return self.coords[0]
        if name == "y": return self.coords[1]
        if name == "z": return self.coords[2]
        raise AttributeError(name)
    def __setattr__(self, name, value):
        if name == "x": self.coords[0] = value
        elif name == "y": self.coords[1] = value
        elif name == "z": self.coords[2] = value
        else: object.__setattr__(self, name, value)
    def copy(self):
        return Point(*self.coords[:])
    def __hash__(self):
        return hash(self.tuple())
    def __repr__(self):
        use_nice_floats = False
        if use_nice_floats:
            return "Point(" + ", ".join("%.1f" % c for c in self.coords) + ")"
        else:
            return "Point(" + ", ".join(str(c) for c in self.coords) + ")"

#old version that is always three dimensions
"""
class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    def tuple(self):
        return (self.x, self.y, self.z)

    def _applyVectorFunc(self, other, f):
        return Point(f(self.x, other.x), f(self.y, other.y), f(self.z, other.z))
    def _applyScalarFunc(self, a, f):
        return self._applyVectorFunc(Point(a,a,a), f)

    def __add__(self, other):
        return self._applyVectorFunc(other, lambda a,b: a+b)
    def __sub__(self, other):
        return self._applyVectorFunc(other, lambda a,b: a-b)
    def __mul__(self, a):
        return self._applyScalarFunc(a, lambda b,c: b*c)
    def __div__(self, a):
        return self._applyScalarFunc(a, lambda b,c: b/c)
    
    def __eq__(self, other):
        try:
            return self.x == other.x and self.y == other.y and self.z == other.z
        except:
            return False

    def copy(self):
        return Point(self.x, self.y, self.z)

    def __hash__(self):
        return hash(self.tuple())

    def __repr__(self):
        #return "Point({}, {}, {})".format(self.x, self.y, self.z)
        return "Point({}, {})".format(self.x, self.y)
"""    

def distance(a,b):
    return (a-b).magnitude()

def dot_product(a,b):
    return sum(a._applyVectorFunc(b, lambda x,y: x*y).coords)

def cross_product(u,v):
    #todo: support more dimensions than three, if it is possible to do so
    x = u.y*v.z - u.z*v.y
    y = u.z*v.x - u.x*v.z
    z = u.x*v.y - u.y*v.x
    return Point(x,y,z)

def midpoint(a,b, frac=0.5):
    return a*(1-frac) + b*frac