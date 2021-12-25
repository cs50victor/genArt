import os, sys, bpy, bmesh, mathutils
from math import radians
from addon_utils import modules
from time import time, strftime,localtime
sys.path.append('C:/Users/Admin/Desktop/genArt/utils')
from tools import *

blendData = bpy.data       # Bdata
blendContext = bpy.context # Bcontext
blendOperators = bpy.ops   # Bops
blendUtils = bpy.utils
blendPath = bpy.path
studioThickness, setThickness = 2, 2
isVideo, squareImg = False,True 

def addStudio(size=120, scaleX=1.5, scaleY=1.5, studioName=None):
    if not studioName or type(studioName) != str:
        raise Exception("Studio has no name or name is not a string.")
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_plane_add(size=size,
                                            enter_editmode=True,
                                            align='WORLD',
                                            location=(0, 0, 0),
                                            scale=(1, 1, 1))
    blendOperators.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(blendContext.object.data)
    for edge in bm.edges:
        if edge.index in [0, 1, 2]:
            edge.select = True
    bmesh.update_edit_mesh(blendContext.object.data)
    blendOperators.mesh.extrude_context_move(
        TRANSFORM_OT_translate={
            "value": (0, 0, size * 1.3),
            "orient_axis_ortho": 'X',
            "orient_type": 'LOCAL',
            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        })

    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False,
                                          rotation=True,
                                          scale=True)
    ensureMode('EDIT')
    blendOperators.mesh.select_all(action='SELECT')
    blendOperators.mesh.extrude_region_shrink_fatten(
        TRANSFORM_OT_shrink_fatten={
            "value": studioThickness,
            "use_even_offset": True
        })
    ensureMode('OBJECT')
    blendOperators.transform.resize(value=(scaleX, scaleY, 1))
    blendContext.object.name = studioName
    #blendContext.object.hide_set(True)

def addSet(size=60, scaleX=1.8, scaleY=1.8, infiniteBackground=False, setName=None):
    if not setName or type(setName) != str:
        raise Exception("Set has no name or name is not a string.")
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_plane_add(size=size,
                                            enter_editmode=True,
                                            align='WORLD',
                                            location=(0, 0, studioThickness),
                                            scale=(1, 1, 1))
    blendOperators.mesh.select_all(action='DESELECT')
    bm = bmesh.from_edit_mesh(blendContext.object.data)
    for edge in bm.edges:
        if edge.index in [0,1,2]:
            edge.select = True
    bmesh.update_edit_mesh(blendContext.object.data)
    blendOperators.mesh.extrude_context_move(
        TRANSFORM_OT_translate={
            "value": (0, 0, size * 1.3),
            "orient_axis_ortho": 'X',
            "orient_type": 'LOCAL',
            "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        })
    if infiniteBackground:
        for edge in bm.edges:
            if edge.index in [0,1,2]:
                edge.select = True
            else:
                edge.select = False
        bmesh.update_edit_mesh(blendContext.object.data)
        blendOperators.mesh.bevel(offset=float(size/5), offset_pct=0, segments=5, release_confirm=True)


    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False,
                                          rotation=True,
                                          scale=True)
    ensureMode('EDIT')
    blendOperators.mesh.select_all(action='SELECT')
    blendOperators.mesh.extrude_region_shrink_fatten(
        TRANSFORM_OT_shrink_fatten={
            "value": setThickness,
            "use_even_offset": True
        })
    blendOperators.mesh.faces_shade_smooth()
    ensureMode('OBJECT')
    blendOperators.transform.resize(value=(scaleX, scaleY, 1))
    blendContext.object.name = setName

def addPlane(size=10, planeName=None):
    if not planeName or type(planeName) != str:
        raise Exception("Plane has no name or name is not a string.")

    z=2*(setThickness+studioThickness)^2 +size
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_plane_add(size=size,enter_editmode=False,align="WORLD",
                                    location=(0, 0, z),
                                    scale=(1, 1, 1))
    blendContext.object.name = planeName
    ensureMode('EDIT')
    blendOperators.mesh.subdivide(number_cuts=50)
    ensureMode('OBJECT')
    plane = blendContext.active_object
    plane.rotation_euler[0] += radians(90)
    cursorToLocation(plane.location)
    subSurf = plane.modifiers.new(name="planeSubsurf",type='SUBSURF')
    subSurf.show_only_control_edges = False
    subSurf.boundary_smooth = 'PRESERVE_CORNERS'

    displace = plane.modifiers.new(name="planeDisplaceMod",type='DISPLACE')
    displace.strength = 0.1
    displaceTexture = blendData.textures.new('planeMarble', type = 'MARBLE')
    displaceTexture.noise_scale = float(0.8)
    displaceTexture.turbulence = float(4.2)
    displaceTexture.noise_depth = int(0)
    displace.texture = displaceTexture
    ensureMode('EDIT')
    ensureMode('OBJECT')
    solidify = plane.modifiers.new(name="planeThickness",type='SOLIDIFY')
    solidify.thickness = 4.4
    smoothness = plane.modifiers.new(name="planeSmoothness",type='SMOOTH')
    smoothness.iterations = 11
    plane.data.polygons.foreach_set('use_smooth', [True] * len(blendContext.object.data.polygons))
    plane.modifiers.update()
    plane.data.update()

def addPlaneMat(materialName=None):
    if not materialName or type(materialName) != str:
        raise Exception("MandleBulb material has no name or material name is not a string.")

    mat = newMaterial(name=materialName)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    outputSurface,outputVolume,outputDisplacement = addNode(nodes,'ShaderNodeOutputMaterial').inputs
    r,g,b = 0,0,0

    shader = addNode(nodes,'ShaderNodeBsdfPrincipled')
    shader.inputs["Base Color"].default_value = (r, g, b, 1)
    shader.inputs["Roughness"].default_value = float(0.11)
    shader.inputs["Metallic"].default_value = float(0.12)
    links.new(shader.outputs["BSDF"], outputSurface)

def lightsCamera(setSize,setScaleX,setScaleY):
    blendContext.scene.world.cycles.volume_step_size = 0.1
    ensureMode('OBJECT')
    # Main Camera
    blendOperators.object.camera_add(align='VIEW', rotation=(radians(90), 0, radians(180)), scale=(1, 1, 1))
    blendContext.object.name = "MainCamera"
    blendContext.object.location[1] = float(12) 
    blendContext.object.data.type = 'PANO'
    blendContext.object.data.cycles.panorama_type = 'FISHEYE_EQUISOLID'
    blendContext.object.data.cycles.fisheye_fov = radians(200)
    if squareImg:
        blendContext.object.data.sensor_width = 33
    else:
        blendContext.object.data.sensor_width = 41
    #Backlit
    blendOperators.object.light_add(type='POINT', align='WORLD',scale=(1, 1, 1))
    blendContext.object.name = "Backlit"
    blendContext.object.data.energy = 100000
    blendContext.object.data.color = (1, 0.777483, 0.0875242)
    blendContext.object.location = (0,float(-setSize/setScaleY -10),float(setSize))

def animate(planeName,planeSize):
    if not planeName:
        raise Exception("Please include the plane name.")
    ensureMode('OBJECT')

    blendOperators.curve.primitive_bezier_circle_add(radius=float(planeSize/4),
        enter_editmode=False, rotation=(0.0, 0.0, float(radians(90))), scale=(1, 1, 1))
    blendContext.object.name = "Bezier"
    blendOperators.object.empty_add(type='PLAIN_AXES', align='WORLD', scale=(1, 1, 1))
    blendContext.object.name = "DisplacementAxes"
    blendContext.object.location=(0.0,0.0,0.0)
    followPath = blendContext.object.constraints.new(type='FOLLOW_PATH')
    followPath.target = blendData.objects["Bezier"]
    followPath.offset = 1
    followPath.keyframe_insert(data_path="offset", frame=0)
    followPath.offset = 100
    followPath.keyframe_insert(data_path="offset", frame=250)

    displace = blendData.objects[planeName].modifiers["planeDisplaceMod"]
    displace.texture_coords = 'OBJECT'
    displace.texture_coords_object = blendData.objects["DisplacementAxes"]

def action():
    render(isVideo=isVideo)

def composite():
    pass 

def blend():
    cleanSlate()
    cyclesSettings(squareRender=squareImg)
    studioName,studioSize,setScaleX,setScaleY = "Studio",320,2,5
    setName,setSize = "Set", 64
    planeName,planeMatName, planeSize = "AbstractPlane","planeMat",16
    # Studio and Set
    addStudio(size=studioSize,studioName=studioName)
    addSet(size=setSize,scaleX=setScaleX, scaleY=setScaleY,
             setName=setName)
    # Objects
    addPlane(size=planeSize,planeName=planeName)
    
    # Materials
    addPlaneMat(planeMatName)

    # Adding materials to objects
    addMaterialToObjects([planeName],planeMatName)

    # Animate
    animate(planeName,planeSize)
    
    # Lights & Camera
    lightsCamera(setSize,setScaleX,setScaleY)

    # Render / Action
    action()

time_start = time()
blend()
print(f"\n{strftime('%I:%M:%S %p',localtime())}")
print("Script execution time: [%.7f] seconds" % (time() - time_start))
