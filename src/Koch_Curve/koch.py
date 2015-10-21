import pygame
import math
import sys
import time

from geometry import Point, distance, midpoint
from animation import make_gif
from PIL import Image

ticks_per_second = 30
levelDurationInSeconds = 0.5
framesPerLevel = int(levelDurationInSeconds * ticks_per_second)

white = (255,255,255)
black = (0,0,0)

windowSize = Point(800,800)

pygame.init()
screen = pygame.display.set_mode(windowSize.tuple())

class LineSegment:
    def __init__(self, a, b):
        self.a, self.b = a,b
    def draw(self, surface):
        if self.a == self.b:
            return
        pygame.draw.line(surface, white, self.a.map(round).tuple(), self.b.map(round).tuple())

def image_from_surface(surface):
    data = pygame.image.tostring(surface, "RGB")
    return Image.fromstring("RGB", surface.get_size(), data)

#given two points A and B, and an angle theta.
#finds a third point C such that ABC is an isocoles triangle, and angle ABC equals theta.
def solveTriangle(A,B, theta):
    c = distance(A,B)
    iota = math.pi - 2*theta
    a = b = c * math.sin(theta)/math.sin(iota)
    epsilon = theta + math.atan2(A.y - B.y, A.x - B.x)
    cx = A.x - math.cos(epsilon)*a
    cy = A.y - math.sin(epsilon)*a
    return Point(cx, cy)

def drawLine(A,B, surface):
    LineSegment(A,B).draw(surface)

def drawBulgingLine(A, B, theta, surface):
    C = solveTriangle(A,B,theta)
    drawLine(A,C, surface)
    drawLine(C,B, surface)

#all eased drawing functions take the arguments:
#A,B: start and end points
#amt_done: a float between 0 and 1, representing how close to completion the current level is
#level: the level of recursion to perform.
#surface: the surface to draw on.
maxAngle = math.pi/4
def drawLevyCurve(A,B, amt_done, level, surface):
    if level == 0:
        theta = amt_done * maxAngle
        drawBulgingLine(A,B, theta, surface)
    else:
        C = solveTriangle(A,B,maxAngle)
        drawLevyCurve(A, C, amt_done, level-1, surface)
        drawLevyCurve(C, B, amt_done, level-1, surface)

def drawKoch(A, E, amt_done, level, surface):
    B = midpoint(A,E, 1/3.0)
    D = midpoint(A,E, 2/3.0)
    if level == 0:
        theta = amt_done * maxAngle
        C = solveTriangle(B,D, theta)
        drawLine(A,B, surface)
        drawLine(B,C, surface)
        drawLine(C,D, surface)
        drawLine(D,E, surface)
    else:
        C = solveTriangle(B,D, maxAngle)
        drawKoch(A,B, amt_done, level-1, surface)
        drawKoch(B,C, amt_done, level-1, surface)
        drawKoch(C,D, amt_done, level-1, surface)
        drawKoch(D,E, amt_done, level-1, surface)

def drawStuff(frame, surface, easingFunc):
    level = frame / framesPerLevel
    frame = frame % framesPerLevel
    amt_done = frame * 1.0 / framesPerLevel
    A = Point(windowSize.x/2, windowSize.y * 0.90)
    B = Point(windowSize.x/2, windowSize.y * 0.10)
    easingFunc(A,B, amt_done, level, surface)


def animateEasing(easingFunc):
    frame = 0
    levels = 5
    screenshots = []
    while frame < framesPerLevel * levels:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(black)
        drawStuff(frame, screen, easingFunc)
        pygame.display.flip()
        screenshots.append(image_from_surface(screen))
        time.sleep(1.0 / ticks_per_second)
        frame += 1
    make_gif(screenshots)


animateEasing(drawKoch)