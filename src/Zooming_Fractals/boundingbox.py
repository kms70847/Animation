from geometry import Point

class BoundingBox:
    def __init__(self, *args):
        if len(args) == 4: #user passed in four scalars
            self.left, self.top, self.right, self.bottom = args
        elif len(args) == 2: #two Points representing upper left and bottom right
            self.left, self.top = args[0].tuple()
            self.right, self.bottom = args[1].tuple()
        self.ul = Point(self.left, self.top)
        self.ur = Point(self.right, self.top)
        self.bl = Point(self.left, self.bottom)
        self.br = Point(self.right, self.bottom)
        self.width = self.right - self.left
        self.height = self.bottom - self.top
    def tuple(self):
        return (self.left, self.top, self.right, self.bottom)