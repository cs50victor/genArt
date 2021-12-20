import os,sys,bpy,bmesh,time,mathutils
from math import radians
from addon_utils import modules

time_start = time.time()

blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
blendUtils = bpy.utils
blendPath = bpy.path
studioThickness,setThickness = 2,1


def ensureMode(expectedMode='OBJECT'):
     if blendOperators.object.mode_set.poll():
         blendOperators.object.mode_set(mode=expectedMode)
              
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
    if (location.lower()=="us"):
        blendContext.scene.unit_settings.system = 'IMPERIAL'
    else:
        blendContext.scene.unit_settings.system = 'METRIC'
        
def addPrimitiveShape():
    # Create primitive and enter edit mode
    blendOperators.mesh.primitive_torus_add(rotation=(0.0,90.0,0.0))
        
    blendOperators.object.mode_set.poll()
    # Subdivide shape 
    blendOperators.object.mode_set(mode="EDIT")
    blendOperators.mesh.subdivide(number_cuts=2, smoothness=1.0)
    blendOperators.object.mode_set(mode="OBJECT")
    # Shade Smooth
    torus = blendContext.active_object
    torus.rotation_euler[0] += radians(90)
    torus.data.polygons.foreach_set('use_smooth',  [True] * len(blendContext.object.data.polygons))
    torus.data.update()
    
def createStudio(size=120,scaleX=1.5,scaleY=1.5):
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_plane_add(size=size, enter_editmode=True, align='WORLD', 
                                    location=(0, 0, 0), scale=(1, 1, 1))
    blendOperators.mesh.select_all(action = 'DESELECT')
    bm = bmesh.from_edit_mesh(blendContext.object.data)
    for edge in bm.edges:
        if edge.index in [0,1,3]:
             edge.select = True 
    bmesh.update_edit_mesh(blendContext.object.data)  
    blendOperators.mesh.extrude_context_move(TRANSFORM_OT_translate={"value":(0, 0, size*1.3),
                                "orient_axis_ortho":'X', "orient_type":'LOCAL', 
                                "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1))})
    
    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False, rotation=True, scale=True)
    ensureMode('EDIT')
    blendOperators.mesh.select_all(action = 'SELECT')
    blendOperators.mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={"value":studioThickness, "use_even_offset":True})
    ensureMode('OBJECT')
    blendContext.object.name = "Studio"
    blendOperators.transform.resize(value=(scaleY,scaleX,1))

def createSet(size=60,scaleX=1.5,scaleY=1.5):
    ensureMode('OBJECT')
    blendOperators.mesh.primitive_plane_add(size=size, enter_editmode=True, align='WORLD', 
                                    location=(0, 0, studioThickness), scale=(1, 1, 1))
    blendOperators.mesh.select_all(action = 'DESELECT')
    bm = bmesh.from_edit_mesh(blendContext.object.data)
    for edge in bm.edges:
        if edge.index in [0,1,3]:
             edge.select = True 
    bmesh.update_edit_mesh(blendContext.object.data)  
    blendOperators.mesh.extrude_context_move(TRANSFORM_OT_translate={"value":(0, 0, size*1.3),
                                "orient_axis_ortho":'X', "orient_type":'LOCAL', 
                                "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1))})
    
    ensureMode('OBJECT')
    blendOperators.object.transform_apply(location=False, rotation=True, scale=True)
    ensureMode('EDIT')
    blendOperators.mesh.select_all(action = 'SELECT')
    blendOperators.mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={"value":setThickness, "use_even_offset":True})
    ensureMode('OBJECT')
    blendOperators.transform.resize(value=(scaleY,scaleX,1))
    blendContext.object.name = "Set"


def blend():
    deleteAllObjects()
    clearCollections()
    createCollection()
    setUnits()
    createStudio(size=200)
    createSet(size=80,scaleY=1.2)
    #addPrimitiveShape()

blend()
print("\nScript execution time: [%.7f] seconds" % (time.time() - time_start))