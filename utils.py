import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
import json
from shapes import *
import re


def read_svg(fp: str):
    """ This function is designed to read the test cases and similarly formatted files and is not a general purpose SVG parser.
    :param fp: svg file path (string)
    :return: list containing elements of Shape class
    """


    tree = ET.parse(fp)
    root = tree.getroot()
    box = root.attrib["viewBox"].split(" ")
    svg = SVG(float(box[0]), float(box[1]), float(box[2]), float(box[3]))
    shapes = [svg]

    for s in root:
        style = s.attrib["style"].replace(" ","").split(";")
        if "d" in s.attrib: #triangle
            pts = [x.split(" ") for x in re.split("M|L|Z",s.attrib["d"]) if x]
            pts = np.array([[float(y) for y in x if y] for x in pts])
            for param in style:
                if "fill" in param:
                    rgb = param.split("rgb")[1][1:-1].split(",")
                    color = np.array([float(x) / 255 for x in rgb])
            shapes.append(Triangle(pts,color))
        elif "r" in s.attrib: # circle
            center = np.array([float(s.attrib["cx"]), float(s.attrib["cy"])])
            radius = float(s.attrib["r"])
            for param in style:
                if "fill" in param:
                    rgb = param.split("rgb")[1][1:-1].split(",")
                    color = np.array([float(x) / 255 for x in rgb])
            shapes.append(Circle(center, radius, color))
        else: #line
            pts = np.array([
                [float(s.attrib["x1"]), float(s.attrib["y1"])],
                [float(s.attrib["x2"]), float(s.attrib["y2"])]
            ])
            for param in style:
                if "stroke-width" in param:
                    width = float(param.split(":")[1][:-2])
                elif "stroke" in param:
                    rgb = param.split("rgb")[1][1:-1].split(",")
                    color = np.array([float(x) / 255 for x in rgb])

            shapes.append(Line(pts, width, color))

    return shapes

def save_image(fp: str, arr):
    """
    :param fp: path of where to save the image
    :param arr: numpy array of dimension (H,W,3), and should be between 0 and 1
    """
    im = Image.fromarray((arr * 255).astype(np.uint8))
    im.save(fp)



