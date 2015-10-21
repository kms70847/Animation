import pygame
import math
import sys
import time

from geometry import Point, distance
from event import Event, ChainedEvent, SimulEvent
from animation import make_gif
from PIL import Image

ticks_per_second = 30
levelDurationInSeconds = 0.5
framesPerLevel = int(levelDurationInSeconds * ticks_per_second)

white = (255,255,255)
black = (0,0,0)

windowSize = Point(400,400)

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

def solveTriangle(A,B, theta):
    c = distance(A,B)
    iota = math.pi - 2*theta
    a = b = c * math.sin(theta)/math.sin(iota)
    epsilon = theta + math.atan2(A.y - B.y, A.x - B.x)
    cx = A.x - math.cos(epsilon)*a
    cy = A.y - math.sin(epsilon)*a
    return Point(cx, cy)

def drawBulgingLine(A, B, theta, surface):
    C = solveTriangle(A,B,theta)
    a = LineSegment(B,C)
    b = LineSegment(A,C)
    a.draw(surface)
    b.draw(surface)

maxAngle = math.pi/4

def drawLevyCurve(A,B, theta, level, surface):
    if level == 0:
        drawBulgingLine(A,B, theta, surface)
    else:
        C = solveTriangle(A,B,maxAngle)
        drawLevyCurve(A,C,theta, level-1, surface)
        drawLevyCurve(C,B,theta, level-1, surface)

def drawStuff(frame, surface):
    level = frame / framesPerLevel
    frame = frame % framesPerLevel
    theta = maxAngle * frame / framesPerLevel
    A = Point(windowSize.x/2, windowSize.y * 0.60)
    B = Point(windowSize.x/2, windowSize.y * 0.40)
    drawLevyCurve(A,B, theta, level, surface)
    

frame = 0
levels = 13
screenshots = []
while frame < framesPerLevel * levels:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(black)
    drawStuff(frame, screen)
    pygame.display.flip()
    screenshots.append(image_from_surface(screen))
    time.sleep(1.0 / ticks_per_second)
    frame += 1

make_gif(screenshots)