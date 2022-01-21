import os, cv2
import numpy as np
from math import ceil
import subprocess as sp 
from random import randint
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

def loadCascades():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
                                'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
                                    'haarcascade_eye.xml')
    # mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 
    #                                 'haarcascade_smile.xml')  
    return [face_cascade,eye_cascade]

def cv2ReadRGB(path):
    pil_img = Image.open(path).convert('RGB')
    open_cv_image = np.array(pil_img) 
    # Convert RGB to BGR 
    return open_cv_image[:, :, ::-1].copy()


def removebg(rawDir, cleanDir):
    sp.run(["rembg","-p",rawDir, cleanDir])

def copyDir(orig, copy):
    sp.run(["cp","-a",f"{orig}/.", f"{copy}/"])

def vignette(input_image):
    rows, cols = input_image.shape[:2]
   
    # generating vignette mask using Gaussian
    # resultant_kernels
    X_resultant_kernel = cv2.getGaussianKernel(cols,200)
    Y_resultant_kernel = cv2.getGaussianKernel(rows,200)
    
    #generating resultant_kernel matrix
    resultant_kernel = Y_resultant_kernel * X_resultant_kernel.T
    
    #creating mask and normalising by using np.linalg
    # function
    mask = 255 * resultant_kernel / np.linalg.norm(resultant_kernel)
    output = np.copy(input_image)
    
    # applying the mask to each channel in the input image
    for i in range(3):
        output[:,:,i] = output[:,:,i] * mask
    return output

def random_color(startNum=150):
        rand = lambda: randint(startNum, 255)
        return [rand(),rand(),rand()]

def reduceOpacity(img, opacity):
    assert opacity >= 0 and opacity <= 1
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    else:
        img = img.copy()
    alpha = img.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    img.putalpha(alpha)
    return img

def cleanFilters(opacity=0.1):
    for fileName in os.listdir(f"filters/"):
            if fileName.endswith(".png") or fileName.endswith(".jpeg") \
                or fileName.endswith(".jpg"):
                    name = fileName.split(".")[0]
                    img = Image.open(f"filters/{fileName}")
                    img = reduceOpacity(img, opacity)
                    newSize = (512,512)
                    img = img.resize(newSize)
                    img.save(f"filters/nobg/{name}.png",quality=100)

def addBg(imgPath):
    fileName,ext = imgPath.split(".")
    im = Image.open(imgPath)
    r,g,b = random_color(startNum=200)
    fill_color = (r,g,b)
    im = im.convert("RGBA")   
    if im.mode in ('RGBA', 'LA'):
        background = Image.new(im.mode[:-1], im.size, fill_color)
        background.paste(im, im.split()[-1]) # omit transparency
        im = background
    return [im.convert("RGB"),fill_color]
    # .save(f'{outputDir}/withbg_{fileName}.{ext}',quality=100)

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result
    
def addTextToImg(image, text, nameArea=None, margin=None, isSignature=False,color="black",
        fontFamily = "go3v2.ttf"): 
    fontFamily = f"fonts/{fontFamily}" 
    fontSize, tempMargin = 0,0
    if not isSignature: 
        if not nameArea:
            raise Exception("+++ No name area provided! +++")
        fontSize, tempMargin = getAutoFontDetails(image, text, fontFamily, nameArea)
    
    if not margin:
        margin = tempMargin

    if isSignature:
        # GirlOnAnAlley.ttf SunmoraBold-nRaEM.ttf
        fontFamily = f"fonts/signature/GirlOnAnAlley.ttf"    
        font = ImageFont.truetype(fontFamily, 15)
        editable_image = ImageDraw.Draw(image)
        editable_image.text(margin, text, font=font, fill=color, align="left")
    else:   
        font = ImageFont.truetype(fontFamily, fontSize)
        editable_image = ImageDraw.Draw(image)
        editable_image.text(margin, text, font=font, fill=color, align="center")
    return image

def getAutoFontDetails(image, txt, fontFamily, nameArea):

    W, H = nameArea
    draw = ImageDraw.Draw(image)
    # portion of image width you want text width to be
    txtArea = Image.new('RGB',nameArea)

    fontsize = 1  # starting font size
    font = ImageFont.truetype(fontFamily, fontsize)

    while (font.getsize(txt)[0] < W) and (font.getsize(txt)[1] < H):
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype(fontFamily, fontsize)

    font = ImageFont.truetype(fontFamily, fontsize-2)
    w, h = draw.textsize(txt, font=font)
    wDiff, hDiff = (W-w)/2, (H-h)/2
    if w > (0.5*W):
        ratio = w/W
        shiftInc = ceil((1-(ratio)) * 100)
        if len(txt)>15:
            wDiff -= (wDiff/shiftInc - ratio**ratio)
        else:
            wDiff += (wDiff/shiftInc + ratio**ratio)
    
    # print(f"+++ [image: {W}x{H}], [text: {w}x{h}], diff:[{wDiff}, {hDiff}] [{wDiff}+{w}+{wDiff}={wDiff+wDiff+w}]\n+++ '{txt}'")

    margin = (wDiff, hDiff)
    return [fontsize, margin]

def averageFaceAreas():
   
    face_cascade,eye_cascade = loadCascades()[:2]                             
    averageValues = {"fx":[],"fy":[],"fw":[],"fh":[],
                    "lex":[],"ley":[],"lew":[],"leh":[],
                    "rex":[],"rey":[],"rew":[],"reh":[]}

    dirs = ["step_2/","step_3/"]
    for dir in dirs:
        for fileName in os.listdir(dir):
            if fileName.endswith(".png"):
                img = cv2ReadRGB(f'step_3/{fileName}')
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                for _ in range(30):
                    try:
                        face = face_cascade.detectMultiScale(gray, 1.3, 5)[0]
                        x,y,w,h = face
                        averageValues["fx"].append(x)
                        averageValues["fy"].append(y)
                        averageValues["fw"].append(w)
                        averageValues["fh"].append(h)

                        roi_gray = gray[y:y+h, x:x+w]
                        roi_color = img[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray)

                        eyeNum = 1
                        for i in range(len(eyes)):
                            (ex,ey,ew,eh) = eyes[i]
                            if i == 0:
                                averageValues["lex"].append(ex)
                                averageValues["ley"].append(ey)
                                averageValues["lew"].append(ew)
                                averageValues["leh"].append(eh)
                            elif i == 1:
                                averageValues["rex"].append(ex)
                                averageValues["rey"].append(ey)
                                averageValues["rew"].append(ew)
                                averageValues["reh"].append(eh)
                            else:
                                break
                    except IndexError as err:
                        print(f"{dir}{fileName} has no faces!++")
                        break
    for key in averageValues:
        avg = sum(averageValues[key])/len(averageValues[key])
        stop = len(averageValues[key])
        start = 0
        while start < stop:
            num = averageValues[key][start]
            if abs(num-avg)>6:
                averageValues[key].pop(i)
                stop -= 1
            start +=1

        averageValues[key] = ceil(averageValues[key][-1])

    return averageValues
