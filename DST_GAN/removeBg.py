import subprocess as sp 

def removebg(rawDir, cleanDir):
    sp.run(["rembg","-p",rawDir, cleanDir])

removebg("input2", "in")


# from rembg.bg import remove
# rembg -o path/to/output.png path/to/input.png
# import numpy as np
# import io
# from PIL import Image

# input_path = 'input.png'
# output_path = 'out.png'

# # Uncomment the following line if working with trucated image formats (ex. JPEG / JPG)
# # ImageFile.LOAD_TRUNCATED_IMAGES = True

# f = np.fromfile(input_path)
# result = remove(f)
# img = Image.open(io.BytesIO(result)).convert("RGBA")
# img.save(output_path)