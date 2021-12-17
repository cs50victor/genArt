import bpy
import random
from math import radians
from mathutils import *

main = bpy.data
contxt = bpy.context

def clearCollections():
    # Delete All Collections
    for collection in bpy.data.collections:
        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)


def createCollections():
    # Create Collections
    defaultCollection = bpy.data.collections.new("Collection")
    cubesCollection = bpy.data.collections.new("Cubes")
    bpy.context.scene.collection.children.link(defaultCollection)
    defaultCollection.children.link(cubesCollection)


def createCubesInCollection():
    spacing = 1
    for x in range(10):
        for y in range(10):
            location = (x * spacing, y * spacing, 0)
            bpy.ops.mesh.primitive_cube_add(size=1,
                                            enter_editmode=False,
                                            align="WORLD",
                                            location=location,
                                            scale=(1, 1, 1))
            cube = bpy.context.active_object
            bpy.data.collections['Cubes'].objects.link(cube)
            bpy.context.scene.collection.objects.unlink(cube)


def addCubeKeyFrames():
    cubes = bpy.data.collections["Cubes"].objects
    timeOffset = 0
    for cube in cubes:
        cube.scale = [0, 0, 0]
        cube.keyframe_insert(data_path="scale", frame=1 + timeOffset)
        cube.scale = [1, 1, 5]
        cube.rotation_euler[0] += radians(45)
        cube.keyframe_insert(data_path="scale", frame=50 + timeOffset)
        cube.scale = [1, 1, 0.5]
        cube.rotation_euler[0] += radians(45)
        cube.keyframe_insert(data_path="scale", frame=70 + timeOffset)
        cube.scale = [1, 1, 1]
        cube.rotation_euler[0] += radians(45)
        cube.keyframe_insert(data_path="scale", frame=80 + timeOffset)
        timeOffset += random.randint(0, 1)

def addModifier():
    cubes = bpy.data.collections["Cubes"].objects
    for cube in cubes:
        cube.modifiers.new["My Modifier","SUBSURF"]
        cube.modifiers["My Modifier"].levels = 3

addModifier()