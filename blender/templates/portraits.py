import os, sys, bpy, bmesh, mathutils
import numpy as np
from math import radians
from time import time, strftime, localtime
from PIL import Image
sys.path.append('C:/Users/Admin/Desktop/genArt/utils')
from tools import *

# ------------------------
bata = bpy.data
bontext = bpy.context
bops = bpy.ops
# ------------------------
isVideo, squareImg = False, True
cameraTypes =['PERSP','PANO','ORTHO']
dict = {}

def createImgMesh():
    grey_img = Image.open(f"{repo}/input/rocky.jpg").convert('L')
    maxSize = (679,100)
    maxHeight =  50
    minHeight = 0
    grey_img.thumbnail(maxSize)
    imageNp = np.array(grey_img)
    maxPix = imageNp.max()
    minPix = imageNp.min()
    (width,height)=grey_img.size
    print(f"w,H={width},{height}")
    vertices,edges,faces = [],[],[]
    dx,dy = 1,1
    for y in range(0,height,dy):
        for x in range(0,width, dx):
            pixelIntensity = imageNp[y][x]
            z = (pixelIntensity * maxHeight)/maxPix
            vertices.append((x,y,z))

    for x in range(0,width,dx):
        for y in range(0,height-1,dy):
            face_v1 = x+y+width
            face_v2 = x+1+y*width
            face_v3 = x+1+(y+1)*width

            faces.append((face_v1,face_v2,face_v3))

            face_v1 = x+y+width
            face_v2 = x +(y+1)*width
            face_v3 = x+1+(y+1)*width

            faces.append((face_v1,face_v2,face_v3))
    
    dict["faceMeshName"] = "faceMesh"
    faceMesh = bata.meshes.new(dict["faceMeshName"])
    faceMesh.from_pydata(vertices,edges,faces)
    faceMesh.update()

    dict["faceObjName"] = "faceObj"
    faceObj = newObject(name=dict["faceObjName"],data=faceMesh)

def addPlane():
    z = setThickness + studioThickness + setSize/5
    y = -setSize/3
    mesh = bops.mesh
    # Create and name abstract plane
    ensureMode('OBJECT')
    mesh.primitive_gear(align='WORLD', location=(0, y, z),change=False)

    bontext.object.scale = (float(planeSize/1.5),float(planeSize/1.5),float(planeSize/1.5))

    plane = bontext.object
    plane.name = planeName
    ensureMode('EDIT')
    # subdivide(number_cuts= int(10 - 100)) offset=float(-30,30), uniform=float(0,1), normal=float(0,1), seed=int(0,50)
    # bm = bmesh.from_edit_mesh(bontext.object.data)
    # selected_edges = [edge for edge in bm.edges if edge.select]
    # bmesh.ops.subdivide_edges(bm,
    #                       edges=selected_edges,
    #                       cuts=30,#np.random.randint(10, 40)
    #                       )
    # bmesh.update_edit_mesh(bontext.object.data)
    # bops.transform.vertex_random(
    #     offset=np.random.uniform(-1,1), 
    #     uniform=np.random.uniform(0,1), 
    #     normal=np.random.uniform(0,1), 
    #     seed=np.random.randint(0, 5))
    bops.mesh.quads_convert_to_tris()
    bops.mesh.relax(iterations=np.random.randint(0, 6))
    ensureMode('OBJECT')
    # Rotate plane
    plane.rotation_euler[0] += radians(90)
    cursorToLocation(plane.location)
    # Add subsurf
    subSurf = plane.modifiers.new(name=pSubsurfName, type='SUBSURF')
    subSurf.show_only_control_edges = False
    subSurf.boundary_smooth = 'ALL'
    subSurf.uv_smooth = 'SMOOTH_ALL'
    subSurf.quality = 6
    # Add marble texture to plane
    displace = plane.modifiers.new(name=displaceModName, type='DISPLACE')
    displace.strength = 0.1
    displaceTexture = bata.textures.new(pMarbleTextureName, type='MARBLE')
    displaceTexture.noise_scale = float(0.8)
    displaceTexture.turbulence = float(4.2)
    displaceTexture.noise_depth = int(2)
    displace.texture = displaceTexture
    ensureMode('EDIT')
    ensureMode('OBJECT')
    # Add smoothness and thickness to plane
    solidify = plane.modifiers.new(name=pSolidifyMod, type='SOLIDIFY')
    solidify.thickness = 0.7
    solidify.use_quality_normals = True
    smoothness = plane.modifiers.new(name=pSmoothMod, type='SMOOTH')
    smoothness.iterations = 15
    smoothness.use_x = False
    smoothness.use_y = False
    smoothness.use_z = True
    
    plane.data.polygons.foreach_set('use_smooth', [True] *len(plane.data.polygons))
    
    plane.modifiers.update()
    plane.data.update()
    # create bezierCurve
    bops.curve.primitive_bezier_circle_add(
        radius=float(planeSize / 4),
        enter_editmode=False,
        rotation=(0.0, 0.0, float(radians(90))),
        scale=(1, 1, 1))
    bezierCurve = bontext.object
    bezierCurve.name = bezierCurveName
    bezierCurve.data.name = f"{bezierCurveName}_data"
    # create axes around bezier
    bops.object.empty_add(type='PLAIN_AXES',
                                    align='WORLD',
                                    scale=(1, 1, 1))
    axes = bontext.object
    axes.name = displaceAxesName
    axes.location = (0.0, 0.0, 0.0)
    # add constraint - to bezier
    displacePath = axes.constraints.new(type='FOLLOW_PATH')
    displacePath.target = bata.objects[bezierCurveName]
    displacePath.name = displacePathName
    # add modifier as displacement texture
    displace = bata.objects[planeName].modifiers[displaceModName]
    displace.texture_coords = 'OBJECT'
    displace.texture_coords_object = bata.objects[displaceAxesName]

def addPlaneMat():
    # creating a new material
    mat = newMaterial(name=planeMatName)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    r, g, b = 0, 0, 0

    # adding a output material node
    outputSurface, outputVolume, outputDisplacement = addNode(
        nodes, 'ShaderNodeOutputMaterial').inputs

    # adding a shader node
    shader = addNode(nodes, 'ShaderNodeBsdfPrincipled')
    shader.inputs["Base Color"].default_value = (r, g, b, 1)
    shader.inputs["Roughness"].default_value = np.random.uniform(0,0.19)
    shader.inputs["Metallic"].default_value = np.random.uniform(0,0.6)
    links.new(shader.outputs["BSDF"], outputSurface)

def lightsCamera():
    ensureMode('OBJECT')
    # Main Camera
    dict["cameraName"]  = "mainCamera"
    dict["cameraDataName"]  = f"{dict['cameraName']}_data"

    camera = newObject(name=dict["cameraName"],
                      data=bata.cameras.new(
                        name=dict["cameraDataName"]))

    camera.rotation_euler = (radians(90), 0, radians(180))
    camera.location[1] = float(12/6)
    # ['PERSP','PANO','ORTHO']
    cameraType = cameraTypes[1]
    if cameraType=='PERSP':
        camera.data.type = cameraType
        camera.data.dof.use_dof = True
        camera.data.dof.focus_object = bata.objects[planeName]
        # lens_unit
        camera.data.lens = 40

    elif cameraType=='PANO':
        camera.data.type = cameraType
        camera.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
        camera.data.cycles.fisheye_fov = radians(200)
        camera.data.cycles.fisheye_lens = 15
        if squareImg:
            camera.data.sensor_width = 22
        else:
            camera.data.sensor_width = 22
    else:
        camera.data.type = 'PANO'
        camera.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
        camera.data.cycles.fisheye_fov = radians(200)
        camera.data.cycles.fisheye_lens = 15
        if squareImg:
            camera.data.sensor_width = 33
        else:
            camera.data.sensor_width = 41

    #Backlit
    dict["backlitName"] = "backlit" 
    dict["backlitDataName"] = f"{dict['backlitName']}_data"

    backlit = newObject(name=dict["backlitName"],
                        data=bata.lights.new(
                            name=dict["backlitDataName"], 
                            type='POINT')
                        )
    backlit.data.energy = int(1000/2)
    backlit.data.color =  randomColor() #(252, 228, 226)
    backlit.location = (0, float(-8 / 2 - 10), float(8+10))
    # World Lighting 
    world = bata.worlds['World'].node_tree  
    nodes = world.nodes
    links = world.links
    nodes.clear()
    # Add Background node
    node_bg = addNode(nodes, 'ShaderNodeBackground')
    node_bg.inputs['Strength'].default_value = 1.5

    # Add Environment Texture node
    node_env = addNode(nodes, 'ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_env.image = bata.images.load(f"{repo}/hdri/museumplein_4k.exr")
    # Add Output node
    node_output = addNode(nodes, 'ShaderNodeOutputWorld') 
    # Link all nodes
    links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
    links.new(node_bg.outputs["Background"], node_output.inputs["Surface"])

def action():
    render(isVideo=isVideo)

def composite():
    pass

def blend():
    cleanSlate()
    cyclesSettings(squareRender=squareImg)
    # Objects
    createImgMesh()
    # Materials
    # addPlaneMat()
    # Adding materials to objects
    # addMaterialToObjects([planeName], planeMatName)
    # Lights & Camera
    lightsCamera()
    # Action (Animate +Render )
    # action()

time_start = time()
blend()
print(f"\n{strftime('%I:%M:%S %p',localtime())}")
print("Script execution time: [%.7f] seconds" % (time() - time_start))


