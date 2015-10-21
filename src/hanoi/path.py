from geometry import Point, distance, midpoint
import math

class Path:
    """
    abstract Path class.
    represents the positions a moving object passes through over time.
    Path subclasses are immutable.
    """
    def at(self, frac=None, **kargs):
        """
        returns the position on the path that occurs at a given time.
        The time argument can be provided in a number of ways.
        `obj.at(T)` or `obj.at(frac=T)`: 
            T is a number between 0 and 1 representing how complete the path is.
            0 returns the starting point; 1 returns the end point.
        `obj.at(dist=T)`:
            T is a number between 0 and obj.distance representing the distance along the path of the desired point.
            0 returns the starting point; obj.distance returns the end point.
        """
        raise Exception("invoked an abstract method")
    def reversed(self):
        """returns a new path object with the start and end points switched"""
        raise Exception("invoked an abstract method")

#todo: determine how to decorate class methods.
#def translate_dist(at_func)
#    """decorator for Path.at. Subclasses should decorate their `at` methods if they want `frac` to automatically be populated with the proper value."""
#    def func(self, frac=None, **kargs):
#        if frac = None: frac = kargs.get("frac", kargs.get("dist", 0)/float(self.distance))
#        return at_func(frac)
#    return func

class LinearPath(Path):
    """A straight path between two points."""
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.distance = distance(self.start, self.end)
    def at(self, frac=None, **kargs):
        if frac == None: frac = kargs.get("frac", kargs.get("dist", 0)/float(self.distance))
        return midpoint(self.start, self.end, frac)
    def reversed(self):
        return LinearPath(self.end, self.start)

class ChordPath(Path):
    """A path following the curve of a semicircle."""
    def __init__(self, center, radius, start, end):
        """
        center - the center of the semicircle.
        radius - the radius of the semicircle.
        start, end - angles (in radians) of the start and end points. May be any real number.
        if start < end, then the path will travel counterclockwise. The path is clockwise otherwise.
        """
        self.center = center
        self.radius = radius
        self.distance = self.radius * abs(start - end)
        self.start = start
        self.end = end
    def at(self, frac=None, **kargs):
        if frac == None: frac = kargs.get("frac", kargs.get("dist", 0)/float(self.distance))
        
        def midpoint(a,b, frac):
            return a*(1-frac) + b*frac

        theta = midpoint(self.start, self.end, frac)
        x = self.center.x + self.radius * math.cos(theta)
        y = self.center.y + self.radius * math.sin(theta)
        return Point(x, y)
    def reversed(self):
        return ChordPath(self.center.copy(), self.radius, self.end, self.start)

class CompositePath(Path):
    """A path composed of other paths."""
    def __init__(self, paths):
        """
        paths - a collection of Path objects.
        """
        self.paths = paths
        self.distance = sum(path.distance for path in paths)
    def at(self, frac=None, **kargs):
        if frac == None: frac = kargs.get("frac", kargs.get("dist", 0)/float(self.distance))
        assert frac <= 1, "Expected frac in [0,1], got {}".format(frac)
        dist = frac * self.distance
        for path in self.paths:
            if dist <= path.distance:
                return path.at(dist=dist)
            else:
                dist -= path.distance
        raise Exception("dist {} exceeded size of path {}".format(dist, self.distance))
    def reversed(self):
        return CompositePath([path.reversed() for path in self.paths][::-1])