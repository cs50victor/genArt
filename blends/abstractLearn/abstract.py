import os
import bpy
import time
import mathutils 
from math import radians

time_start = time.time()

blendData = bpy.data
blendContext = bpy.context
blendOperators = bpy.ops
blendUtils = bpy.utils
blendPaths = bpy.path

def deleteAllObjects():
    objs = [ob for ob in blendContext.scene.objects if ob.type in ('CAMERA', 'MESH')]
    blendOperators.object.delete({"selected_objects": objs})

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
    torus.data.polygons.foreach_set('use_smooth',  [True] * len(bpy.context.object.data.polygons))
    torus.data.update()

def start():
    deleteAllObjects()
    clearCollections()
    createCollection()
    addPrimitiveShape()




start()
print("My Script Finished: %.4f sec" % (time.time() - time_start))