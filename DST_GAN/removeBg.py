import subprocess as sp 

def removebg(rawDir, cleanDir):
    sp.run(["rembg","-p",rawDir, cleanDir])

removebg("input2", "in")