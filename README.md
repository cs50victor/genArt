## Create virtualenv 
- virtualenv -p python3 genArt
## Activate venv
- source genArt/bin/activate
## Deactivate venv
- deactivate

## Blender python directory
"c:\Program Files\Blender Foundation\Blender 3.0\3.0\python\bin\python.exe" -m pip list

# Fix PILLOW installation problem
"c:\Program Files\Blender Foundation\Blender 3.0\3.0\python\bin\python.exe" -m ensurepip --default-pip
"c:\Program Files\Blender Foundation\Blender 3.0\3.0\python\bin\python.exe" -m pip install Pillow


# Social Media
- Behance
- Dribble
- Twitter
- Instagram
- Art Station
  
# Libraries to play with
keras
pytorch
pytorch3d
tensorflow
numpy
matplotlib
Pillow
pylint
cython
scikit-learn

nltk
spacy
scipy
keras
opencv
pandas
statsmodel
gensim
theano

- https://github.com/nywang16/Pixel2Mesh
- https://github.com/deepmind/deepmind-research/blob/master/polygen/training.ipynb
- https://medium.com/swlh/generative-art-design-b81a81f99b2a
- https://github.com/NVlabs/stylegan
- https://github.com/NVlabs/stylegan2-ada-pytorch

“How to Generate (Almost) Anything,” which encouraged students to use deep learning software for creative projects.


We trained a GAN (Generative Adversarial Network) on thousands of dress designs. The AI algorithm learned how to generate new designs that don't exist in the dataset. We picked one of the designs AI hallucinated and decided to bring it to reality! 

# Jupyter notebook local runtime
pip install jupyterlab jupyter_http_over_ws
jupyter serverextension enable --py jupyter_http_over_ws


jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=8888 --NotebookApp.port_retries=0

# Remove bg virtualenv - USE GIT BASH
virtualenv --python=python3.8 vnv
source vnv/scripts/activate (unix) 

pip3 install numpy opencv-contrib-python rembg matplotlib sklearn tensorflow tensorflow_hub sketchify --no-cache-dir


**Basic installation for dst_vnv**
pip3 install numpy opencv-contrib-python rembg matplotlib sklearn sketchify noise --no-cache-dir

rembg -p withbg portraits


https://colab.research.google.com/drive/1i04HzQJJODfqYOZ8REk98PuJy-SzxxWL?usp=sharing


https://github.com/dvschultz/ml-art-colabs
"GT Alpina Typewriter" font
https://artificial-images.com/project/linnaeus-pip-machine-learning-eugenics/ background color


class ndarray_pydata(np.ndarray):
    def __bool__(self) -> bool:
        return len(self) > 0

edges = edges_np.view(ndarray_pydata)
faces = faces_np.view(ndarray_pydata)
mesh.from_pydata(vertices, edges, faces)


## Workflow
raw_img -> cropAndUpscale -> removebg 
    -> themal, grayscale, sketch
    a -> apply texture filters 
        -> upscaled img, themal, grayscale, sketch
    b -> STYLE GAN to upscaled img, grayscale, sketch
    
    -> removebg from a and b 
    > add white background


use alisha.jpeg
- loop  img:dir(raw)            -- "raw/"
  -> removebg("raw", "in") [in] -- "in/"
  --------------------- Colab notebook ---------------
  -> detectFace(path) [in]
  -> thermal, grey, sketch
  -> for texture in os.listdir("textures/"):
              ....
              tensor_to_image(output_image).save(f"out/{name}_{textureNum}.{ext}")[out]
  -> for pic in os.listDir("in/"):
    -> for portaits in portatraits:
        .... [out]
  -----------------------------------------------------
  -> download , rename dir , removebg, add white bg in same new dir
  -> thermal, grey, sketch for all output images
  
replace img eyes

# pyenv (mac)
pyenv virtualenv 3.8.12 dst_vnv
pyenv activate dst_vnv | pyenv deactivate
pyenv uninstall dst_vnv      

https://colab.research.google.com/drive/1i04HzQJJODfqYOZ8REk98PuJy-SzxxWL#scrollTo=Mp4LBsttKvFN
