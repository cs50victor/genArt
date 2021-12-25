import os, sys, bpy, bmesh, mathutils
from math import radians
from addon_utils import modules
from time import time, strftime,localtime
from utils.index import cleanSlate, addNode, ensureMode

blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
blendUtils = bpy.utils
blendPath = bpy.path
studioThickness, setThickness = 2, 2

def createStudio(size=120, scaleX=1.5, scaleY=1.5, studioName=None):
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
    blendContext.object.hide_set(True)

def createSet(size=60, scaleX=1.8, scaleY=1.8, infiniteBackground=False, setName=None):
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

def createCube(size=10, cubeName=None):
    if not cubeName or type(cubeName) != str:
        raise Exception("Cube has no name or name is not a string.")

    z=2*(setThickness+studioThickness)^2 +size
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_cube_add(size=size,enter_editmode=False,align="WORLD",
                                    location=(0, 0, z),
                                    scale=(1, 1, 1))
    blendContext.object.name = cubeName

def addTorus():
    # Create primitive and enter edit mode
    blendOperators.mesh.primitive_torus_add(rotation=(0.0, 90.0, 0.0))

    blendOperators.object.mode_set.poll()
    # Subdivide shape
    blendOperators.object.mode_set(mode="EDIT")
    blendOperators.mesh.subdivide(number_cuts=2, smoothness=1.0)
    blendOperators.object.mode_set(mode="OBJECT")
    # Shade Smooth
    torus = blendContext.active_object
    torus.rotation_euler[0] += radians(90)
    torus.data.polygons.foreach_set('use_smooth', [True] * len(blendContext.object.data.polygons))
    torus.data.update()

def mandleBulbMaterial(materialName=None,nodeType="diffuse"):
    if not materialName or type(materialName) != str:
        raise Exception("MandleBulb material has no name or material name is not a string.")

    mat = newMaterial(name=materialName)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    outputSurface,outputVolume,outputDisplacement = addNode(nodes,'ShaderNodeOutputMaterial').inputs
    r,g,b = 127, 42, 60

    if nodeType == "diffuse":
        shader = addNode(nodes,'ShaderNodeBsdfDiffuse')
        shader.inputs["Color"].default_value = (r, g, b, 1)
        shader.inputs["Roughness"].default_value = 1
        links.new(shader.outputs["BSDF"], outputSurface)

    elif nodeType == "emission":
        shader = addNode(nodes,'ShaderNodeEmission')
        shader.inputs["Color"].default_value = (r, g, b, 1)
        shader.inputs["Strength"].default_value = 0.5
        links.new(shader.outputs["Emission"], outputSurface)

    elif nodeType == "glossy":
        shader = addNode(nodes,'ShaderNodeBsdfGlossy')
        shader.inputs["Color"].default_value = (r, g, b, 1)
        shader.inputs["Roughness"].default_value = 1
        links.new(shader.outputs["BSDF"], outputSurface)

def lightsCamera():
    blendContext.scene.world.cycles.volume_step_size = 0.1
    ensureMode('OBJECT')
    blendOperators.object.light_add(type='SUN', align='WORLD',
                         location=(0, 0, 300), scale=(1, 1, 1))
    blendOperators.object.camera_add(enter_editmode=False, 
                                        align='VIEW', location=(0, 100, 50), 
                                        rotation=(1.50797, 3.02288e-07, 3.14159), 
                                        scale=(30, 30, 30))

def action():
    pass

def blend():
    cleanSlate()
    studioName, setName, cubeName = "Studio","Set","MandleBulb"
    mandleBubMatName = "mandlebmat"
    # Studio and Set
    createStudio(size=200,studioName=studioName)
    createSet(size=80,scaleX=2, scaleY=2,
             setName=setName)
    # Objects
    createCube(size=40,cubeName=cubeName)
    
    # Materials
    mandleBulbMaterial(mandleBubMatName,"glossy")

    # Adding materials to objects
    addMaterialToObjects([cubeName],mandleBubMatName)
    
    # Lights & Camera
    lightsCamera()

    # Render / Action
    #action()

time_start = time()
blend()
print(f"\n{strftime('%I:%M:%S %p',localtime())}")
print("Script execution time: [%.7f] seconds" % (time() - time_start))
