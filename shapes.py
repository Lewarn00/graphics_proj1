import numpy as np

class Shape():
    def __init__(self):
        self.type = None
        self.color = np.array([0.0,0.0,0.0])

class Triangle(Shape):

    def __init__(self,pts,color):
        """
        :param pts: numpy array of shape (3,2) representing vertices in viewbox coordinates
        :param color: numpy array of shape (3) representing color with values in [0,1]
        """
        self.pts = pts
        self.type = "triangle"
        self.color = color


class Line(Shape):

    def __init__(self,pts,width,color):
        """
        :param pts: numpy array of shape (2,2), each row is an endpoint in viewbox coordinates
        :param width: line width
        :param color: numpy array of shape (3) representing color with values in [0,1]
        """
        self.pts = pts
        self.type = "line"
        self.color = color
        self.width = width

class Circle(Shape):
    def __init__(self, center, radius, color):
        """
        :param center: numpy array of shape (2), gives the coordinates of the center of the circle
        :param radius: radius of the circle
        :param color: numpy array of shape (3) representing color with values in [0,1]
        """
        self.center = center
        self.radius = radius
        self.type = "circle"
        self.color = color

class SVG(Shape):
    def __init__(self,x,y,h,w):
        """ Origin will always be tested as (0,0)
        :param x: x coordinate of origin
        :param y: y coordinate of origin
        :param h: viewbox height
        :param w: viewbox width
        """
        self.origin = np.array([x,y])
        self.h = h
        self.w = w
        self.type = "svg"



