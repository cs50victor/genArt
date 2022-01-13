import cv2 as cv
import numpy as np
import random
from edges import Edges
from background import Background
from PIL import Image, ImageOps

filePath = "sketchbook/test2.png"
fileName = filePath.split("/")[1]

class Sketch:
    def __init__(self, image):
        self.img = cv.imread(image)

    def sketch(self):
        grey = cv.cvtColor(self.img, cv.COLOR_BGR2GRAY)
        inv = 255 - grey
        blur = cv.GaussianBlur(inv, (13,13), 0)
        return cv.divide(grey, 255-blur, scale=256)

def sketch():
    img = Image.open(filePath)

    sketch = Sketch(filePath).sketch()
    cv.imwrite(f"sketchbook/sketch_{fileName}", sketch)
    bg = Background(img.size, octaves=6).background()
    edges = Edges(filePath).edges()
    #sketchTrans = cv.cvtColor(sketch, cv.COLOR_GRAY2RGBA)

    mask = edges[3]
    sketch = cv.bitwise_and(sketch, edges, edges)
    (thresh, sketch) = cv.threshold(sketch, 240, 255, cv.THRESH_BINARY)
    #sketch = cv.multiply(sketch, np.array(bg), scale=(1./128))


    h, w = sketch.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    #mask[1:h+1, 1:w+1] = sketch
    sketchColor = cv.cvtColor(sketch, cv.COLOR_GRAY2RGBA)
    white = np.all(sketchColor == [255,255,255,255], axis=-1)
    sketchColor[white, -1] = 0
    cv.imwrite(f"sketchbook/final_{fileName}", sketchColor)
    final = Image.fromarray(sketchColor)
    # final.show()

sketch()

def addBg():
    images = [filePath]
    for i in images:
        im = Image.open(r'{0}'.format(i))
        fill_color = (255,255,255)
        im = im.convert("RGBA")   
        if im.mode in ('RGBA', 'LA'):
            background = Image.new(im.mode[:-1], im.size, fill_color)
            background.paste(im, im.split()[-1]) # omit transparency
            im = background
        im.convert("RGB").save(r'sketchbook/newimage_{0}'.format(fileName))

addBg()