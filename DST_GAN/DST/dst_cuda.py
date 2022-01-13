# svn -q export https://github.com/cs50victor/ml_models/trunk/style_transfer_textures textures
# svn -q export https://github.com/cs50victor/ml_models/trunk/upscale upscaleModels
import sys,os,shlex,torch
import cv2 as cv
import numpy as np
import subprocess as sp
from PIL import Image
import tensorflow as tf
import tensorflow_hub as hub
import matplotlib as mpl
import matplotlib.cm as mtpltcm
import matplotlib.pylab as plt

# print("TF Version: ", tf.__version__)
# print("TF Hub version: ", hub.__version__)
# print("Eager mode enabled: ", tf.executing_eagerly())
# print("Built with Cuda: ", tf.test.is_built_with_cuda())
# print("GPU available: ", tf.config.list_physical_devices('GPU'))

im_size=256
device="cuda"
pts_path="example/NBBresults"
activation_path="example/NBBresults/correspondence_activation.txt"
output_path="example/CleanedPts"
NBB=1
max_num_points=80
b=10
output_dir="example/DSTresults"
max_iter=250
checkpoint_iter=50
content_weight=8
warp_weight=0.5
reg_weight=50
optim="sgd"
lr=0.2
verbose=0
save_intermediate=0
save_extra=0

def setEnvs():
  sp.run('bash setEnv.bash', shell=True, env=os.environ.copy()) 
  for k,v in os.environ.items():
    print(f"{k}:{v}")

def thermal(imagePath):
    #initialize the colormap
    colormap = mtpltcm.jet
    cNorm = mpl.colors.Normalize(vmin=0, vmax=255)
    scalarMap = mtpltcm.ScalarMappable(norm=cNorm, cmap=colormap)

    img = cv.imread(imagePath)
    # Our operations on the frame come here
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    #add blur to make it more realistic
    blur = cv.GaussianBlur(gray,(15,15),0)
    #assign colormap
    finalImg = scalarMap.to_rgba(blur, bytes=True)

    # Save the image
    imageName = imagePath.replace('in/', '')
    name, ext = imageName.split(".")
    cv.imwrite(f"out/{name}_thermal.{ext}", finalImg)

def autoPadding(start, stop, limit ):
    """Return correct padding value."""
    if stop == start:
        return start 
    elif stop < start:
        return limit if stop<limit else stop
    else:
        return limit if stop>limit else stop

def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.5, threshold=0):
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

def detectFace(image, padding=200):
    """Detects faces in an image and upscaled them"""
    face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 
                                'haarcascade_frontalface_default.xml')
    # eye_cascade = cv.CascadeClassifier(cv.data.haarcascades + 
    #                                 'haarcascade_eye.xml')

    img = cv.imread(image)
    imgW = img.shape[1]
    imgH = img.shape[0]

    faces = face_cascade.detectMultiScale(img)
    face = faces[0]
    paddingW, paddingH  = padding,padding 
    x, y, w, h = [ v for v in face ]
    hStart,hStop = autoPadding(y, y-paddingH, 1), autoPadding(y+h,y+h+paddingH,imgH)
    wStart,wStop = autoPadding(x, x-paddingW, 1), autoPadding(x+w,x+w+paddingW,imgW)
    
    face_region =  img[hStart:hStop, wStart:wStop]

    sr = cv.dnn_superres.DnnSuperResImpl_create()
    sr.readModel("upscaleModels/FSRCNN_x3.pb")
    sr.setModel("fsrcnn",3)
    face_upscaled = unsharp_mask(sr.upsample(face_region))
    imageName = image.replace('in/', '')
    print(f"upscaled -> {imageName}")
    cv.imwrite(f"upscaled/{imageName}", face_upscaled)
    
def tensor_to_image(tensor):
  tensor = np.array(tensor * 255, dtype=np.uint8)
  if np.ndim(tensor)>3:
    assert tensor.shape[0] == 1
    tensor = tensor[0]
  return Image.fromarray(tensor)

def crop_center(image):
  """Returns a cropped square image."""
  shape = image.shape
  new_shape = min(shape[1], shape[2])
  offset_y = max(shape[1] - shape[2], 0) // 2
  offset_x = max(shape[2] - shape[1], 0) // 2
  image = tf.image.crop_to_bounding_box(
      image, offset_y, offset_x, new_shape, new_shape)
  return image

def load_image(image_path, image_size=(256, 256), preserve_aspect_ratio=True):
  """Loads and returns a preprocessed image."""
  # Load and convert to float32 numpy array, 
  #                       add batch dimension, and normalize to range [0, 1].
  img = tf.io.decode_image(
      tf.io.read_file(image_path),
      dtype=tf.float32)[tf.newaxis, ...]
  img = crop_center(img)
  img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
  return img

def show_n(images, titles=('',)):
  """Displays a plot of images with their titles"""
  n = len(images)
  image_sizes = [image.shape[1] for image in images]
  w = (image_sizes[0] * 6) // 320
  plt.figure(figsize=(w * n, w))
  gs = mpl.gridspec.GridSpec(1, n, width_ratios=image_sizes)
  for i in range(n):
    plt.subplot(gs[i])
    try:
      plt.imshow(images[i][0], aspect='equal')
    except:
      plt.imshow(images[i], aspect='equal')
    plt.title(titles[i] if len(titles) > i else '')
  plt.show()

def transformInput():

    hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
    hub_module = hub.load(hub_handle)
    style_img_size = (256, 256)  # Recommended to keep it at 256, based on dataset.
    
    commands = [
                shlex.split("python NBB/main.py --results_dir ${pts_path} --imageSize\
                    ${im_size} --fast --datarootA ${content_path} --datarootB\
                    ${style_path}"),
                shlex.split("python cleanpoints.py ${content_path} ${style_path}\
                    ${content_pts_path} ${style_pts_path} ${activation_path}\
                    ${output_path} ${im_size} ${NBB} ${max_num_points} ${b}"),
                shlex.split("python -W ignore main.py ${content_path} ${style_path}\
                    ${content_pts_path} ${style_pts_path} ${output_dir}\
                    ${output_prefix} ${im_size} ${max_iter} ${checkpoint_iter}\
                    ${content_weight} ${warp_weight} ${reg_weight} ${optim}\
                    ${lr} ${verbose} ${save_intermediate} ${save_extra} ${device}")
    ]

    for inputFile in os.listdir("in/"):
      print(f"input file - {inputFile}")
      path = f"in/{inputFile}"
      detectFace(path)
      thermal(path)
      # The output image size can be arbitrary.
      name, ext = inputFile.split(".")
      output_image_sizes = [512]
      textureNum,portraitNum = 0,0 

      for output_image_size in output_image_sizes:
        print(f"-- processing : {output_image_size}x{output_image_size}")
        input_image = load_image(f"upscaled/{inputFile}", 
                                (output_image_size, output_image_size))
        
        thermal_image = load_image(f"out/{name}_thermal.{ext}", 
                                (output_image_size, output_image_size))
        # show_n([input_image,thermal_image],
        #         titles=['Input image','Thermal Image'])
        
        resizedInputDir = f"DST/example/{name}_{output_image_size}.{ext}"
        tensor_to_image(input_image).save(resizedInputDir)
        content_path = resizedInputDir.replace("DST/","")
        
        for texture in os.listdir("textures/"):
            textureNum += 1
            print(f"---- using textures : {texture}")
            style_image = load_image(f"textures/{texture}", style_img_size)
            style_image = tf.nn.avg_pool(style_image, ksize=[3,3],
                                        strides=[1,1], padding='SAME')
            output_image = hub_module(tf.constant(input_image), 
                                        tf.constant(style_image))[0]
            tensor_to_image(output_image).save(f"out/{name}_{textureNum}.{ext}")
            # show_n([input_image, style_image, output_image],
            #        titles=['Input image', 'Style image', 'Output image'])

        for portrait in os.listdir("DST/portraits"):
          portraitNum += 1
          print(f"\n-------- USING PORTRAITS : [         {portrait}         ]\n")
          cwd = os.getcwd()
          os.chdir('DST')
          from utils_misc import pil_loader, pil_resize_long_edge_to, pil_to_tensor

          style_path = f"portraits/{portrait}"
          output_prefix = portrait.split('.')[0]
          # Load and resize input images
          content_pil = pil_resize_long_edge_to(pil_loader(content_path),
                                                int(im_size))

          style_pil = pil_resize_long_edge_to(pil_loader(style_path), 
                                              int(im_size))

          content_im_orig = pil_to_tensor(content_pil).to(device)
          style_im_orig = pil_to_tensor(style_pil).to(device)

          
          for i in range(len(commands)):
            if i == 2:
              content_pts_path = "example/NBBresults/correspondence_A.txt"
              style_pts_path = "example/NBBresults/correspondence_B.txt"
            elif i==3:
              content_pts_path = "example/CleanedPts/correspondence_A.txt"
              style_pts_path = "example/CleanedPts/correspondence_B.txt"
              
            process = sp.Popen(commands[i], shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
            for line in process.stdout.readlines():
                print (line)
                retval = process.wait()

          """
          Fix later
          - Plot input and output images
          result_pil = pil_resize_long_edge_to(pil_loader(f"example/DSTresults/example.png"),
                                              int(os.environ["im_size"]))
          show_n([content_pil, style_pil,result_pil],titles=["Input image with points",
                                                              "Style image with points",
                                                              "Output image"])
          """
          os.chdir(cwd)

transformInput()