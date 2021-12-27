import os, sys, bpy, bmesh
import numpy as np
from time import strftime, localtime

repo = "C:/Users/Admin/Desktop/genArt"
blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
blendUtils = bpy.utils
blendPath = bpy.path
scene = blendContext.scene


# TOOLs
def newMaterial(name=None):
    if not name or type(name) != str:
        raise Exception(
            "New Material has no name or material name is not a string.")
    name = str(name).strip()
    nameTest1 = blendData.materials.get(name.capitalize())
    nameTest2 = blendData.materials.get(name.lower())

    if nameTest1 != None or nameTest2 != None:
        raise Exception("Material already exist")

    mat = blendData.materials.new(name=name)
    mat.use_nodes = True
    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat


def cursorToLocation(location):
    if not location:
        raise Exception("No location provided")
    ensureMode('OBJECT')
    scene.cursor.location = location


def ensureMode(expectedMode='OBJECT'):
    if blendOperators.object.mode_set.poll():
        blendOperators.object.mode_set(mode=expectedMode)


def addNode(nodes, nodeName):
    if nodes == None:
        raise Exception("Nodes object wasn't passed into function.")
    if nodeName == None or type(nodeName) != str:
        raise Exception(
            "Node instance has no name or node name is not a string.")

    nodeName = nodeName.strip()
    if blendOperators.node.add_node.poll():
        blendOperators.node.add_node(type=nodeName, use_transform=True)
    try:
        return nodes.new(type=nodeName)
    except Exception as e:
        print(f'Error with nodes parameter :\n{e}')


def addMaterialToObjects(objects=[], material=None):
    ensureMode('OBJECT')
    if not objects:
        raise Exception("Empty object array")
    if not material or type(material) != str:
        raise Exception("No material name or material name is not a string")
    material = material.strip()
    if material not in [mat.name for mat in blendData.materials]:
        raise Exception(
            "material name doesn't exist. Check capitalization/spelling")

    for obj in objects:
        if obj not in [x.name for x in blendData.objects]:
            raise Exception(
                "Object in list doesn't exist. Check capitalization/spelling")
        mesh = blendData.objects[obj].data
        mesh.materials.append(blendData.materials[material])


def addMaterialsToObject(object=None, materials=[]):
    ensureMode('OBJECT')
    if not materials:
        raise Exception("Empty materials array")
    if not object or type(object) != str:
        raise Exception("No object name or object name is not a string")
    object = object.strip()
    if object not in [obj.name for obj in blendData.objects]:
        raise Exception(
            "object name doesn't exist. Check capitalization/spelling")

    for material in materials:
        if material not in [mat.name for mat in blendData.materials]:
            raise Exception(
                "material in list doesn't exist. Check capitalization/spelling"
            )
        mesh = blendData.objects[object].data
        mesh.materials.append(blendData.materials[material])

def randomColor():
    return list(np.random.choice(range(256), size=3))

# SETUP
def cyclesSettings(frameTimeLimit=None, squareRender=True):

    # Changes default material view to Eevee
    area = next(area for area in blendContext.screen.areas
                if area.type == 'VIEW_3D')
    space = next(space for space in area.spaces if space.type == 'VIEW_3D')
    space.shading.type = 'RENDERED'  # set the viewport shading
    space.shading.use_scene_lights = True
    space.shading.use_scene_world = True
    #
    scene.render.resolution_x = 1080
    if squareRender:
        scene.render.resolution_y = 1080
    else:
        scene.render.resolution_y = 1350
    scene.render.engine = 'CYCLES'
    scene.cycles.feature_set = 'SUPPORTED'
    scene.cycles.device = 'GPU'
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPTIX'
    scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.samples = int(4096 / 2)
    scene.cycles.adaptive_min_samples = 0
    scene.cycles.adaptive_threshold = 0.005  #0.01
    scene.render.film_transparent = True
    scene.cycles.glossy_bounces = 15
    scene.cycles.denoising_prefilter = 'ACCURATE'
    scene.cycles.use_preview_denoising = True

    if frameTimeLimit:
        scene.cycles.time_limit = int(frameTimeLimit)
    #** test later
    scene.view_settings.look = 'High Contrast'


def removeAllMaterials():
    for material in blendData.materials:
        blendData.materials.remove(material)


def removeAllObjects():
    ensureMode('OBJECT')
    for obj in blendData.objects:
        blendData.objects.remove(obj)


def clearEverythingelse():
    for scene in blendData.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (blendData.objects, blendData.meshes,
                          blendData.lights, blendData.cameras,
                          blendData.textures, blendData.images):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)


def clearCollections():
    # Delete All Collections
    for collection in blendData.collections:
        for obj in collection.objects:
            blendData.objects.remove(obj, do_unlink=True)
        blendData.collections.remove(collection)


def createCollection():
    # Create Collections
    defaultCollection = blendData.collections.new("Collection")
    scene.collection.children.link(defaultCollection)


def setUnits(location="us"):
    if (location.lower() == "us"):
        scene.unit_settings.system = 'IMPERIAL'
    else:
        scene.unit_settings.system = 'METRIC'


def render(isVideo=False):
    print("\nRendering....")
    render = scene.render
    render.use_file_extension = False
    if isVideo:
        FILE_NAME = f"img_{strftime('%I_%M_%S_%p',localtime())}.mp4"
        render.ffmpeg.format = 'MPEG4'
        render.ffmpeg.constant_rate_factor = 'HIGH'
        render.image_settings.file_format = 'FFMPEG'
        blendOperators.render.render('INVOKE_DEFAULT',
                                     animation=True,
                                     use_viewport=True,
                                     write_still=True)
        render.filepath = f'{repo}/output/vid/{FILE_NAME}'
    else:
        FILE_NAME = f"img_{strftime('%I_%M_%S_%p',localtime())}.png"
        render.image_settings.file_format = 'PNG'
        render.image_settings.color_depth = '16'
        render.image_settings.color_mode = 'RGBA'
        blendOperators.render.render('INVOKE_DEFAULT', write_still=True)
        render.filepath = f'{repo}/output/img/{FILE_NAME}'


def cleanSlate():
    removeAllObjects()
    clearCollections()
    createCollection()
    removeAllMaterials()
    clearEverythingelse()
    setUnits()