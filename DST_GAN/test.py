import os
import cv2
import itertools
import numpy as np
from utils import *
from pprint import pprint
from random import randint, choice
from PIL import Image
from time import time, strftime, localtime

avgAreas = {}
signature = "1010001"

def extractEyes(fileName):
    faceX, faceY, faceW, faceH = avgAreas["fx"], avgAreas["fy"], avgAreas["fw"], avgAreas["fh"]
    leftEyeX, leftEyeY, leftEyeW, leftEyeH = avgAreas[
        "lex"], avgAreas["ley"], avgAreas["lew"], avgAreas["leh"]
    rightEyeX, rightEyeY, rightEyeW, rightEyeH = avgAreas[
        "rex"], avgAreas["rey"], avgAreas["rew"], avgAreas["reh"]

    img = cv2ReadRGB(f'step_3/{fileName}')
    name, ext = fileName.split(".")
    face = img[faceY:faceY+faceH, faceX:faceX+faceW]
    leftEye = face[leftEyeY: leftEyeY +
                   leftEyeH, leftEyeX: leftEyeX + leftEyeW]
    cv2.imwrite(f'step_4/{name}_eye_1.png', leftEye)
    rightEye = face[rightEyeY: rightEyeY +
                    rightEyeH, rightEyeX: rightEyeX + rightEyeW]
    cv2.imwrite(f'step_4/{name}_eye_2.png', rightEye)

def distortEyes(fileName, eyeCombos):
    faceX, faceY, faceW, faceH = avgAreas["fx"], avgAreas["fy"], avgAreas["fw"], avgAreas["fh"]
    leftEyeX, leftEyeY, leftEyeW, leftEyeH = avgAreas[
        "lex"], avgAreas["ley"], avgAreas["lew"], avgAreas["leh"]
    rightEyeX, rightEyeY, rightEyeW, rightEyeH = avgAreas[
        "rex"], avgAreas["rey"], avgAreas["rew"], avgAreas["reh"]

    img = cv2ReadRGB(f'step_3/{fileName}')
    name, ext = fileName.split(".")
    eyeAreas = [[leftEyeX, leftEyeY, leftEyeW, leftEyeH],
                [rightEyeX, rightEyeY, rightEyeW, rightEyeH]]

    # * using index 0 , only get combinations for 2 eyes
    twoEyeCombs = eyeCombos[0]

    for x in range(len(twoEyeCombs)):
        twoEyeComb = twoEyeCombs[x]
        if len(twoEyeComb) > 2:
            pprint(f"more than two eyes in this combination:{twoEyeComb}")
            break

        temp_img = img.copy()
        temp_roi_color = temp_img[faceY:faceY+faceH, faceX:faceX+faceW]

        for y in range(len(twoEyeComb)):
            eyeFile = twoEyeComb[y]

            eyeImg = cv2ReadRGB(f"step_4/{eyeFile}")
            ex, ey, ew, eh = eyeAreas[y]
            eye_height, eye_width = randint(
                int(eh*1.1), int(eh*1.4)), randint(int(ew*1.1), int(ew*1.4))
            resized_img = cv2.resize(
                eyeImg, (eye_height, eye_width), interpolation=cv2.INTER_AREA)
            resized_img_h, resized_img_w, _ = resized_img.shape
            temp_roi_color[ey:ey+resized_img_h,
                           ex:ex+resized_img_w, :] = resized_img

        cv2.imwrite(f'step_5/{name}_combo_{x}.png', temp_img)

def stepOne():
    # * Remove bg from raw files
    print(f"+++ [Step 1] +++")

    removebg("step_0", "step_1")

def stepThree():
    # * Backup & remove bg from gcolab files
    print(f"+++ [Step 3] +++")
    # bkupDir = "step_2_bkup"
    # copyDir(bkupDir,"step_2")
    removebg("step_2", "step_3")

def stepFour():
    """ get all eyes into step_4, 
        and remove invalid images from step_3
    """
    print(f"+++ [Step 4] +++")

    faceAreas = averageFaceAreas()
    avgAreas.update(faceAreas)
    for imgFile in os.listdir("step_3/"):
        if imgFile.endswith(".png"):
            extractEyes(imgFile)

def stepFive():
    # * generate face/eye swap combination

    print(f"+++ [Step 5] +++")
    sortedEyes = sorted(os.listdir("step_4/"),
                        key=lambda num: num[num.find("eye_")+4:num.find(".")])
    lastFile = sortedEyes[-1]
    maxNum = int(lastFile[lastFile.find("eye_")+4:lastFile.find(".")])
    allCombinations = []
    eyeNumList = []

    for num in range(1, maxNum+1):
        eyeNumList.append([i for i in sortedEyes if f"eye_{num}" in i])
        if num == 2:
            # * Get all combinations for 2 eyes only
            allCombinations.append(list(itertools.product(*eyeNumList[:num])))
        elif num > 2:
            break

    #* remove normal images from dir
    matchingFiles = [match for match in os.listdir("step_3/") if "_512.png" in match]
    for matchingFile in matchingFiles:
        os.remove(f"step_3/{matchingFile}")
        print(f"++++ Removed {matchingFile} because it's not needed in further steps.")

    for fileName in os.listdir("step_3/"):
        if fileName.endswith(".png"):
            distortEyes(fileName, allCombinations)

def stepSix():
    print(f"+++ [Step 6] +++")
    removebg("step_5", "step_6")

def stepSeven():
    print(f"+++ [Step 7] +++")

    intputDir = "step_6"
    outputDir = "step_7"
    defaultSize = (512, 512)
    diff = (40, 40)
    mainImgSize = tuple(map(lambda i, j: i - j, defaultSize, diff))
    
    xMargin = 10
    fontHeight = 80
    fontMargin = 20
    topContMargin = fontHeight + fontMargin
    containerW, containerY = int(512+(xMargin*2)), int(512+topContMargin)
    nameArea= (512,topContMargin)
    validFonts = [i for i in os.listdir("fonts/") if (i.endswith(".ttf") or i.endswith(".otf"))]

    personName = "alisha".upper()
    nameColors = ["#000000","#e0491d"]
    signaturePos = (xMargin+5,containerY-20)

    filterImg = Image.open(f"filters/noisefilm.png")
    paperImg = Image.open(f"filters/paper2.png").resize(defaultSize)

    for fileName in os.listdir(f"{intputDir}/"):
        if fileName.endswith(".png"):
            mainImgName = fileName.split(".")[0]
            for bgNum in range(1,3):
                    nameFont=choice(validFonts)
                    container = Image.new("RGB", (containerW, containerY), (255,255,255))
                    coloredImg,rgb = addBg(f"{intputDir}/{fileName}")
                    coloredImg = coloredImg.resize(mainImgSize)
                    coloredImgBase = Image.new("RGB", (512, 512),rgb)

                    coloredImgBase.paste(coloredImg, diff)
                    coloredImgBase.paste(filterImg, mask=filterImg.split()[3])
                    coloredImgBase.paste(paperImg, mask=paperImg.split()[3])
                    container.paste(coloredImgBase,(xMargin,topContMargin))
                    withName = addTextToImg(container,personName,nameArea,
                                                fontFamily=nameFont,
                                                color=nameColors[0])
                    withSignature = addTextToImg(container,signature,
                                                    isSignature=True, color="black",
                                                    margin=signaturePos)
                    withSignature.save(f"{outputDir}/{mainImgName}_bg_{bgNum}.png",quality=100)

def stepEight():
    print(f"+++ [Step 8] +++")
    pass


time_start = time()
print(f"\n{strftime('%I:%M:%S %p',localtime())}\n")
print(f"+++ [Started] +++")
# stepOne()
# stepThree()
# stepFour()
# stepFive()
# stepSix()
stepSeven()
print(f"+++ [Steps Completed] +++")
print(f"\n{strftime('%I:%M:%S %p',localtime())}\n")
print("Script execution time: [%.7f] seconds" % (time() - time_start))
# eventually use cython and multiprocessing


"""
if bg.endswith(".png") or bg.endswith(".jpg")\
                        or bg.endswith(".jpeg"):
                    bgNum += 1
container = Image.new("RGB", (containerW, containerY), (255,255,255))
                    background = Image.open(f"bg/{bg}").resize(defaultSize)
                    mainPic = Image.open(
                        f"{intputDir}/{fileName}").resize(mainImgSize)

                    background.paste(mainPic, diff, mask=mainPic.split()[3])
                    background.paste(filterImg, mask=filterImg.split()[3])
                    background.paste(paperImg, mask=paperImg.split()[3])
                    container.paste(background,(xMargin,topContMargin))
                    withName = addTextToImg(container,personName,nameArea,color=choice(nameColors))
                    withSignature = addTextToImg(container,signature,
                                                    isSignature=True, color="black",
                                                    margin=signaturePos)
"""