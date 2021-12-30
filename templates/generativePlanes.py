import os, sys, bpy, bmesh, mathutils
import numpy as np
from math import radians
from addon_utils import modules
from time import time, strftime, localtime

sys.path.append('C:/Users/Admin/Desktop/genArt/utils')
from tools import *

blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
studioThickness, setThickness = 2, 2
isVideo, squareImg = False, True
# Use global variables to easily access any object
studioName, studioSize, setStudioX, setStudioY,setStudioZ = "Studio", 100, 2, 2,2
setName, setSize, setScaleX, setScaleY,setScaleZ = "Set", 32, 2, 2, 1
planeName, planeMatName, planeSize = "AbstractPlane", "PlaneMat", 8
pSubsurfName, pMarbleTextureName, pSolidifyMod, pSmoothMod = "PlaneSubsurf", 'PlaneMarble', "PlaneThickness", "PlaneSmoothness"
bezierCurveName, displaceAxesName, displaceModName = "Bezier", "DisplacementAxes", "PlaneDisplaceMod"
displacePathName = "DisplacementPath"
cameraName, backlitName = "MainCamera", "Backlit"
cameraTypes =['PERSP','PANO','ORTHO']
glassMatName = "GlassMat"

def addStudio():
    ensureMode('OBJECT')
    mesh = blendOperators.mesh
    # Add plane
    mesh.primitive_plane_add(size=studioSize,
                             enter_editmode=True,
                             align='WORLD',
                             location=(0, 0, 0),
                             scale=(1, 1, 1))
    studio = blendContext.object
    studio.name = studioName
    # Extrude plane to make walls
    mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(studio.data)
    for edge in bm.edges:
        if edge.index in [0, 1, 2]:
            edge.select = True
    bmesh.update_edit_mesh(studio.data)
    mesh.extrude_context_move(
        TRANSFORM_OT_translate={
            "value": (0, 0, studioSize * 1.3),
            "orient_axis_ortho": 'X',
            "orient_type": 'LOCAL',
            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        })
    # Add studio ceiling
    for edge in bm.edges:
            edge.select = False
    bm.edges.ensure_lookup_table()
    bm.edges[5].select = True
    bmesh.update_edit_mesh(studio.data)
    mesh.extrude_context_move(
        TRANSFORM_OT_translate={
            "value": (0,studioSize^2,0),
            "orient_axis_ortho": 'X',
            "orient_type": 'LOCAL',
        })
    bmesh.update_edit_mesh(studio.data)

    # Extrude Studio (add thickness)
    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False,
                                          rotation=True,
                                          scale=True)
    ensureMode('EDIT')
    mesh.select_all(action='SELECT')
    mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={
        "value": studioThickness,
        "use_even_offset": True
    })
    # Resize and rename Studio
    ensureMode('OBJECT')
    blendOperators.transform.resize(value=(setStudioX, setStudioY, setStudioZ))
    
    #studio.hide_set(True)


def addSet(infiniteBackground=False):
    ensureMode('OBJECT')
    mesh = blendOperators.mesh
    # Add plane
    mesh.primitive_plane_add(size=setSize,
                             enter_editmode=True,
                             align='WORLD',
                             location=(0, 0, studioThickness),
                             scale=(1, 1, 1))
    set = blendContext.object
    set.name = setName
    # Extrude plane to make walls
    mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(set.data)
    for edge in bm.edges:
        if edge.index in [0, 1, 2]:
            edge.select = True
    bmesh.update_edit_mesh(set.data)
    mesh.extrude_context_move(
        TRANSFORM_OT_translate={
            "value": (0, 0, setSize * 1.3),
            "orient_axis_ortho": 'X',
            "orient_type": 'LOCAL',
            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        })
    if infiniteBackground:
        for edge in bm.edges:
            if edge.index in [0, 1, 2]:
                edge.select = True
            else:
                edge.select = False
        bmesh.update_edit_mesh(set.data)
        mesh.bevel(offset=float(setSize / 5),
                   offset_pct=0,
                   segments=5,
                   release_confirm=True)

    # Extrude set (add thickness)
    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False,
                                          rotation=True,
                                          scale=True)
    ensureMode('EDIT')
    mesh.select_all(action='SELECT')
    mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={
        "value": setThickness,
        "use_even_offset": True
    })
    mesh.faces_shade_smooth()
    # Resize and rename Studio
    ensureMode('OBJECT')
    blendOperators.transform.resize(value=(setScaleX, setScaleY, setScaleZ))


def addPlane(object):

    ensureMode('OBJECT')
    plane = object
    plane.name = planeName
    ensureMode('EDIT')
    # int(10 - 100)
    # blendOperators.mesh.subdivide(number_cuts= )
    blendOperators.mesh.subdivide(number_cuts=100)
    # offset=float(-30,30), uniform=float(0,1), normal=float(0,1), seed=int(0,50)
    blendOperators.transform.vertex_random(
        offset=np.random.uniform(-5,5), 
        uniform=np.random.uniform(0,1), 
        normal=np.random.uniform(0,1), 
        seed=np.random.randint(0, 10))
    blendOperators.mesh.tris_convert_to_quads()
    bpy.ops.mesh.relax(iterations=np.random.randint(0, 10))
    
    ensureMode('OBJECT')
    # Rotate plane
    plane = blendContext.active_object
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
    displaceTexture = blendData.textures.new(pMarbleTextureName, type='MARBLE')
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
    
    plane.data.polygons.foreach_set('use_smooth', [True] *
                                    len(plane.data.polygons))
    plane.modifiers.update()
    plane.data.update()
    # create bezierCurve
    blendOperators.curve.primitive_bezier_circle_add(
        radius=float(planeSize / 4),
        enter_editmode=False,
        rotation=(0.0, 0.0, float(radians(90))),
        scale=(1, 1, 1))
    bezierCurve = blendContext.object
    bezierCurve.name = bezierCurveName
    bezierCurve.data.name = f"{bezierCurveName}_data"
    # create axes around bezier
    blendOperators.object.empty_add(type='PLAIN_AXES',
                                    align='WORLD',
                                    scale=(1, 1, 1))
    axes = blendContext.object
    axes.name = displaceAxesName
    axes.location = (0.0, 0.0, 0.0)
    # add constraint - to bezier
    displacePath = axes.constraints.new(type='FOLLOW_PATH')
    displacePath.target = blendData.objects[bezierCurveName]
    displacePath.name = displacePathName
    # add modifier as displacement texture
    displace = blendData.objects[planeName].modifiers[displaceModName]
    displace.texture_coords = 'OBJECT'
    displace.texture_coords_object = blendData.objects[displaceAxesName]

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

def addGlassMat():
    # creating a new material
    mat = newMaterial(name=glassMatName)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    r, g, b = 255, 255, 255

    # adding a output material node
    outputSurface, outputVolume, outputDisplacement = addNode(
        nodes, 'ShaderNodeOutputMaterial').inputs

    # adding a shader node
    shader = addNode(nodes, 'ShaderNodeBsdfPrincipled')
    shader.inputs["Base Color"].default_value = (r, g, b, 1)
    shader.inputs["Roughness"].default_value = 0
    shader.inputs["Metallic"].default_value = 1
    links.new(shader.outputs["BSDF"], outputSurface)

def lightsCamera():
    ensureMode('OBJECT')
    # Main Camera
    blendOperators.object.camera_add(align='VIEW',
                                     rotation=(radians(90), 0, radians(180)),
                                     scale=(1, 1, 1))
    camera = blendContext.object
    camera.name = cameraName
    camera.location[1] = float(12/6)
    # ['PERSP','PANO','ORTHO']
    cameraType = cameraTypes[1]
    if cameraType=='PERSP':
        camera.data.type = cameraType
        camera.data.dof.use_dof = True
        camera.data.dof.focus_object = blendData.objects[planeName]
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
    #align='WORLD'
    backlit = newObject(name=backlitName,
                        data=blendData.lights.new(
                            name=f"{backlitName}_data", 
                            type='POINT')
                        )
    backlit.data.energy = int(1000/2)
    backlit.data.color =  randomColor() #(252, 228, 226)
    backlit.location = (0, float(-setSize / setScaleY - 10), float(setSize+10))
    # World Lighting 
    world = blendData.worlds['World'].node_tree  
    nodes = world.nodes
    links = world.links
    nodes.clear()
    # Add Background node
    node_bg = addNode(nodes, 'ShaderNodeBackground')
    node_bg.inputs['Strength'].default_value = 1.5

    # Add Environment Texture node
    node_env = addNode(nodes, 'ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_env.image = blendData.images.load(f"{repo}/hdri/museumplein_8k.exr")
    # Add Output node
    node_output = addNode(nodes, 'ShaderNodeOutputWorld') 
    # Link all nodes
    links.new(node_env.outputs["Color"], node_bg.inputs["Color"])
    links.new(node_bg.outputs["Background"], node_output.inputs["Surface"])

def animate():
    ensureMode('OBJECT')
    # Increase displace path
    displacePath = blendData.objects[displaceAxesName].constraints[displacePathName]
    displacePath.offset = 1
    displacePath.keyframe_insert(data_path="offset", frame=0)
    displacePath.offset = 200
    displacePath.keyframe_insert(data_path="offset", frame=250)
    # Rotate abstract plane
    plane = blendData.objects[planeName]
    plane.rotation_euler[2] += radians(0)
    plane.keyframe_insert(data_path="rotation_euler", frame=0)
    plane.rotation_euler[2] += radians(360)
    plane.keyframe_insert(data_path="rotation_euler", frame=250)
    
    # Rotate, move and scale displacement bezier
    displaceBezier = blendData.objects[bezierCurveName]
    currFrame = 1 
    for frame in range(1,int(250/6)):
        currFrame+=frame
        a = np.random.randint(3)
        displaceBezier.rotation_euler[a] += radians(np.random.randint(-360, 360))
        displaceBezier.keyframe_insert(data_path="rotation_euler", frame=currFrame)
        b = np.random.randint(3)
        displaceBezier.scale[b] += np.random.randint(-5, 5)
        displaceBezier.keyframe_insert(data_path="scale", frame=currFrame)
    
    # Rotate and scale camera
    cam = blendData.objects[cameraName]
    cam.rotation_euler = cam.rotation_euler
    cam.keyframe_insert(data_path="rotation_euler", frame=0)
    cam.rotation_euler[1] += radians(360)
    cam.keyframe_insert(data_path="rotation_euler", frame=250)
    # -----------------
    cam.data.lens = 14
    cam.data.keyframe_insert(data_path="lens", frame=0)
    cam.data.lens = 200
    cam.data.keyframe_insert(data_path="lens", frame=int(250/2))
    cam.data.lens = 14
    cam.data.keyframe_insert(data_path="lens", frame=250)
    
    # Slowly decrease backlit
    backLight = blendData.objects[backlitName].data
    backLight.color = backLight.color
    backLight.energy = 1000
    backLight.keyframe_insert(data_path="color", frame=0)
    backLight.keyframe_insert(data_path="energy", frame=0)
    backLight.color = (166,16,30)
    backLight.energy = 10000
    backLight.keyframe_insert(data_path="color", frame=250)
    backLight.keyframe_insert(data_path="energy", frame=250)

def action():
    if isVideo: animate()
    #render(isVideo=isVideo)

def composite():
    pass

def primitives():
    z = setThickness + studioThickness + setSize/5
    y = -setSize/3
    primitives = []
    mesh = blendOperators.mesh
    # Create and name abstract plane
    ensureMode('OBJECT')
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    mesh.primitive_plane_add(size=planeSize,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=(0, y, z),
                                            scale=(1, 1, 1))
    primitives.append(blendContext.object)
    
    return primitives

def blend():
    shapes = primitives()
    for shape in shapes:
        cleanSlate()
        cyclesSettings(squareRender=squareImg)
        # Studio and Set
        addStudio()
        addSet(infiniteBackground=True)
        # Objects
        addPlane(shape)
        # Materials
        addPlaneMat()
        addGlassMat()
        # Adding materials to objects
        addMaterialToObjects([planeName], planeMatName)
        # Lights & Camera
        lightsCamera()
        # Action (Animate +Render )
        action()

time_start = time()
blend()
print(f"\n{strftime('%I:%M:%S %p',localtime())}")
print("Script execution time: [%.7f] seconds" % (time() - time_start))


