import os,sys
import cv2 as cv
import numpy as np
from time import time, strftime, localtime
sys.path.append('C:/Users/Admin/Desktop/genArt/utils')
from tools import repo

def autoPadding(start, stop, limit ):
    if start==None or stop==None  or limit==None:
        raise Exception("Missing parameter!")
     
    if stop == start:
        return start 
    elif stop < start:
        end = limit if stop+1<limit else stop+1
        return end
    end = limit if stop+1>limit else stop+1
    return end

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

def detectFace(image):
    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 
                                'haarcascade_frontalface_default.xml')
    # eye_cascade = cv.CascadeClassifier(cv.data.haarcascades + 
    #                                 'haarcascade_eye.xml')

    img = cv.imread(image)
    imgH = img.shape[1]
    imgW = img.shape[0]
    minisize = (imgH,imgW)

    # miniframe = cv.resize(img, minisize)

    faces = face_cascade.detectMultiScale(img)
    
    for f in faces:
        paddingW, paddingH  = [800,800] 
        x, y, w, h = [ v for v in f ]
        hStart,hStop = autoPadding(y, y-paddingH, 1), autoPadding(y+h,y+h+paddingH,imgH)
        wStart,wStop = autoPadding(x, x-paddingW, 1), autoPadding(x+w,x+w+paddingW,imgW)

        face_region =  img[hStart:hStop, wStart:wStop]

        sr = cv.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(f"{repo}/docker/ml_models/EDSR_x4.pb")
        sr.setModel("edsr",4)
        face_upscaled = unsharp_mask(sr.upsample(face_region))
    
        # cv.imshow("Img:", face_upscaled)
        # cv.waitKey(0)
        # cv.destroyAllWindows()

        fname, ext = os.path.splitext(image)
        cv.imwrite(f"{fname}_cropped{ext}", face_upscaled)
    return


time_start = time()
detectFace(f"{repo}/input/rocky-bg.png")
print(f"\n{strftime('%I:%M:%S %p',localtime())}")
print("Script execution time: [%.7f] seconds" % (time() - time_start))