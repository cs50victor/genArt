import os, sys, bpy, bmesh, time, mathutils
from math import radians
from addon_utils import modules

time_start = time.time()

blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
blendUtils = bpy.utils
blendPath = bpy.path
studioThickness, setThickness = 2, 2

def ensureMode(expectedMode='OBJECT'):
    if blendOperators.object.mode_set.poll():
        blendOperators.object.mode_set(mode=expectedMode)

# del this function 
def addNode(nodes,nodeName):
    if nodes==None:
        raise Exception("Nodes object wasn't passed into function.")
    if nodeName==None or type(nodeName) != str:
        raise Exception("Node instance has no name or node name is not a string.")
    
    nodeName=nodeName.strip()
    if blendOperators.node.add_node.poll():
        blendOperators.node.add_node(type=nodeName,use_transform=True)
    try:
        return nodes.new(type=nodeName)
    except Exception as e:
        print(f'Error with nodes parameter :\n{e}')

def cyclesSettings(frameTimeLimit=None):
    # Changes default material view to Eevee
    area = next(area for area in blendContext.screen.areas if area.type == 'VIEW_3D')
    space = next(space for space in area.spaces if space.type == 'VIEW_3D')
    space.shading.type = 'RENDERED'  # set the viewport shading
    space.shading.use_scene_lights = True
    space.shading.use_scene_world = True
    #
    blendContext.scene.render.engine = 'CYCLES'
    blendContext.scene.cycles.feature_set = 'SUPPORTED'
    blendContext.scene.cycles.device = 'GPU'
    blendContext.scene.cycles.use_denoising = True
    blendContext.scene.cycles.denoiser = 'OPTIX'
    blendContext.scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    blendContext.scene.cycles.use_adaptive_sampling = True
    blendContext.scene.cycles.samples = 4096
    blendContext.scene.cycles.adaptive_min_samples = 0
    blendContext.scene.cycles.adaptive_threshold = 0.005  #0.01
    blendContext.scene.render.film_transparent = True
    blendContext.scene.cycles.glossy_bounces = 15
    blendContext.scene.cycles.denoising_prefilter = 'ACCURATE'

    if frameTimeLimit:
        blendContext.scene.cycles.time_limit = int(frameTimeLimit)
    #** test later
    blendContext.scene.view_settings.look = 'High Contrast'

def removeAllMaterials():
    for material in blendData.materials:
        blendData.materials.remove(material)

def deleteAllObjects():
    ensureMode('OBJECT')
    override = blendContext.copy()
    override['selected_objects'] = list(blendContext.scene.objects)
    blendOperators.object.delete(override)

def clearCollections():
    # Delete All Collections
    for collection in blendData.collections:
        for obj in collection.objects:
            blendData.objects.remove(obj, do_unlink=True)
        blendData.collections.remove(collection)

def createCollection():
    # Create Collections
    defaultCollection = blendData.collections.new("Collection")
    blendContext.scene.collection.children.link(defaultCollection)

def setUnits(location="us"):
    if (location.lower() == "us"):
        blendContext.scene.unit_settings.system = 'IMPERIAL'
    else:
        blendContext.scene.unit_settings.system = 'METRIC'

def addPrimitiveShape():
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

def createSet(size=60, scaleX=1.5, scaleY=1.5, setName=None):
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
            "value": setThickness,
            "use_even_offset": True
        })
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

def newMaterial(name=None):
    if not name or type(name) != str:
        raise Exception("New Material has no name or material name is not a string.")
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

def addMaterialToObjects(objects=[],material=None):
    ensureMode('OBJECT')
    if not objects:
        raise Exception("Empty object array")
    if not material or type(material) != str:
        raise Exception("No material name or material name is not a string")
    material=material.strip()
    if material not in [mat.name for mat in blendData.materials]:
        raise Exception("material name doesn't exist. Check capitalization/spelling")

    for obj in objects:
        if obj not in [x.name for x in blendData.objects]:
            raise Exception("Object in list doesn't exist. Check capitalization/spelling")
        mesh = blendData.objects[obj].data
        mesh.materials.append(blendData.materials[material])

def addMaterialsToObject(object=None,materials=[]):
    ensureMode('OBJECT')
    if not materials:
        raise Exception("Empty materials array")
    if not object or type(object) != str:
        raise Exception("No object name or object name is not a string")
    object=object.strip()
    if object not in [obj.name for obj in blendData.objects]:
        raise Exception("object name doesn't exist. Check capitalization/spelling")

    for material in materials:
        if material not in [mat.name for mat in blendData.materials]:
            raise Exception("material in list doesn't exist. Check capitalization/spelling")
        mesh = blendData.objects[object].data
        mesh.materials.append(blendData.materials[material])

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

def blend():
    deleteAllObjects()
    clearCollections()
    createCollection()
    removeAllMaterials()
    setUnits()
    cyclesSettings()
    #-------------------------
    studioName, setName, cubeName = "Studio","Set","MandleBulb"
    createStudio(size=200,studioName=studioName)
    createSet(size=80, scaleX=1,setName=setName)
    createCube(size=40,cubeName=cubeName)

    mandleBubMatName = "mandlebmat"
    mandleBulbMaterial(mandleBubMatName,"glossy")
    addMaterialToObjects([cubeName],mandleBubMatName)
    
    #addPrimitiveShape()


blend()
print("\nScript execution time: [%.7f] seconds" % (time.time() - time_start))

"""


"""