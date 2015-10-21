import math
import sys
import itertools
from PIL import Image
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

from geometry import Point, distance, midpoint
Point.draw = lambda self: glVertex3f(self.x, self.y, self.z)

from animation import make_gif

class Polygon:
    def __init__(self, *points):
        self.points = list(points)
    def draw(self):
        for p in self.points:
            p.draw()
    def copy(self):
        points = [p.copy() for p in self.points]
        return Polygon(*points)

class Body:
    def __init__(self, *faces):
        self.faces = list(faces)
    def draw(self):
        for face in self.faces:
            glBegin(GL_LINE_LOOP)
            face.draw()
            glEnd()
    def map_(self, func):
        ret = self.copy()
        for face in ret.faces:
            for idx, point in enumerate(face.points):
                face.points[idx] = func(point)
        return ret
    def copy(self):
        faces = [f.copy() for f in self.faces]
        return Body(*faces)
    


framesPerSecond = 30
msPerFrame = 1000 / framesPerSecond

def subDivide(polygon, depth):
    if depth == 0:
        return [polygon]
    assert(len(polygon.points) == 3)
    a,b,c = polygon.points
    ab = midpoint(a,b)
    bc = midpoint(b,c)
    ca = midpoint(c,a)
    subFaces = [
        subDivide(Polygon(a, ab, ca), depth-1),
        subDivide(Polygon(b, bc, ab), depth-1),
        subDivide(Polygon(c, ca, bc), depth-1),
        subDivide(Polygon(ab, bc, ca), depth-1)
    ]
    faces = sum(subFaces, [])
    return faces

def makeTetra():
    vertices = [
        Point( 1, 0, 0),
        Point(-1, 0, 0),
        Point( 0, 1, 0),
        Point( 0,-1, 0),
        Point( 0, 0, 1),
        Point( 0, 0,-1)
    ]
    faces = []
    for a,b,c in itertools.combinations(vertices, 3):
        if distance(a,b) == distance(b,c) and distance(a,b) == distance(a,c):
            poly = Polygon(a,b,c)
            faces.extend(subDivide(poly,2))
    return Body(*faces)

def normalized(point, center, r):
    delta = point - center
    delta /= delta.magnitude()
    delta *= r
    return center + delta

def mutated(body, amtMutated):
    center = Point(0,0,0)
    def shift(point):
        dest = normalized(point, center, 1)
        return midpoint(point, dest, amtMutated)
    return body.map_(shift)

def normalize(body, center, r):
    for face in body.faces:
        for idx, point in enumerate(face.points):
            delta = point - center
            delta /= delta.magnitude()
            delta *= r
            face.points[idx] = center + delta

tetra = makeTetra()
bodyToDraw = mutated(tetra, 0.0)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glColor(255,255,255)
    bodyToDraw.draw()

    """
    glColor(255,0,0)
    glBegin(GL_LINES)
    glVertex3f(0,0,0)
    glVertex3f(0,1,0)
    glEnd()
    """

    glutSwapBuffers();


def init():
    glEnable(GL_DEPTH_TEST);

    glMatrixMode(GL_PROJECTION);
    gluPerspective(40.0,
     1.0,
     1.0, 10.0);
    glMatrixMode(GL_MODELVIEW);
    gluLookAt(0.0, 2.0, 3.0,  
    0.0, 0.0, 0.0,      
    0.0, 1.0, 0.);      


t = 0
def timer(*args):
    global t
    t += 1
    rotationsPerSecond = 0.25
    degreesPerRotation = 360
    anglePerFrame = rotationsPerSecond * degreesPerRotation / framesPerSecond
    glRotatef(anglePerFrame, 0.0, 1.0, 0.0);

    theta = t*anglePerFrame * math.pi / 180.0
    amtMutated = 1-((math.cos(theta) +1)/2)
    global bodyToDraw
    bodyToDraw = mutated(tetra, amtMutated)
    
    glutPostRedisplay()
    
    if theta <= 2*math.pi:
        screenshots.append(takeScreenshot())
    else:
        glutLeaveMainLoop()
    
    glutTimerFunc(msPerFrame, timer, None)


def takeScreenshot():
    width = 200
    height = 200
    im = Image.new("RGBA", (width,height))
    
    buffer = (GLubyte * (3*width*height))(0)
    glReadPixels(0,0,200,200,GL_RGB,GL_UNSIGNED_BYTE, buffer)
    im = Image.new("RGB", (200,200))
    for i in range(width):
        for j in range(height):
            startIdx = (j*width+i)*3
            r = buffer[startIdx+0]
            g = buffer[startIdx+1]
            b = buffer[startIdx+2]
            im.putpixel((i,height-j-1), (r,g,b))
    return im

screenshots = []
def main():
    glutInit(len(sys.argv), sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
    glutCreateWindow("wireframe tetrahedron");
    glutReshapeWindow(200,200)
    glutDisplayFunc(display);
    glutTimerFunc(msPerFrame, timer, None)
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
    init();
    glutMainLoop();
    make_gif(screenshots)
    return 0;

main()