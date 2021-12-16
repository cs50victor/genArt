import bpy
import numpy as np
from math import sin, pi, cos
from mathutils import Euler
import colorsys
import random as rn
import os
import bmesh
tau = 2*pi

'''Importing the module Cora with all the utils '''
# The modules can be added from scripts saved in the folder but using a different editor
# Script cointaining all the Utils
cora = bpy.data.texts["Cora.py"].as_module()

# Directory where the files are
myFilepath = bpy.data.filepath
myDir = os.path.dirname(myFilepath)

'''------------------------------------------ Shortcuts ----------------------------------------------------'''


def Mode(modeString):
    '''
        Function to shift from object mode to edit mode easily.
        modeString = 'edit' for edit mode , 'obj' for objectmode
        '''
    if modeString.capitalize() == 'Edit':
        bpy.ops.object.mode_set(mode='EDIT')
    elif modeString.capitalize() == 'Obj':
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        raise NotImplementedError(
            'Other types not implemented yet besides Edit and Obj')


'''--------------------------------------------------CODE---------------------------------------------------------'''

'''CLEAR THE SCENE'''
cora.RemoveAll()
for material in bpy.data.materials:
    bpy.data.materials.remove(material)
# bpy.ops.object.select_all(action='SELECT') # Another way to clear the scene
# bpy.ops.object.delete()

'''Set the render engine (Cycles)'''
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.caustics_reflective = False

'''Create camera and set its position'''
cam_loc = (-0.07, -3.02, 2)
cam_rot = np.deg2rad([58, 0, 1.2])
cora.SetTheCamera(cam_loc, cam_rot)

'''Instantiate the Light'''
energy = 80
sun_loc = (1.3, -0.9, 1.75)
cora.SetTheLight(sun_loc, energy)

''' Set the plane'''
plane_loc = (0, 0, -0.14)
nameStringPlane = 'plane'
cora.CreatePlane(plane_loc, nameStringPlane)
plane = bpy.data.objects['plane']
# RainbowLights() # This was an experiment

'''Instantiate the torus - this will be the doughnut'''
pos = (0, 0, 0)
rot = (0, 0, 0)
smooth = True  # Put false if you don't want it smooth
nameString = 'doughnut'
cora.CreateTorus(nameString, pos, rot, smooth)

# Shortcut for the mesh and vertices of the doughnut
dou = bpy.data.objects['doughnut']  # shortcut for the doughnut
mesh = dou.data

# Deforming the doughnut
for vert in mesh.vertices:
    i = rn.randint(1, 4)*0.01
    vert.co.x *= (1.2+i)
    vert.co.y *= (1.1+i)
    vert.co.z *= (1.2+i)

'''creating a copy for the icing'''
# newMesh = bpy.data.meshes.new(name='dough') # Better not to use this: better to copy the existing one
newMesh = mesh.copy()

vertCount = 0
newVert = []

for vert in mesh.vertices:
    vertCount += 1
    newVert.append(vert.co.x)
    newVert.append(vert.co.y)
    newVert.append(vert.co.z)

for x in range(len(mesh.vertices) * 3):
    newVert.append(0)

# Set the array lenght
newMesh.vertices.add(vertCount)
newMesh.vertices.foreach_set('co', newVert)

newMesh.update()
newMesh.validate()
ice = bpy.data.objects.new('icing', newMesh)
ice.name = 'icing'

# Put the new mesh inside the collection called Collection
scene = bpy.context.scene
collection = bpy.data.collections['Collection']
ice.instance_collection = collection
collection.objects.link(ice)
cora.SmoothTheMesh(ice)

for obj in scene.objects:
    print("object:", obj)
# there should be 5 objects : light, camera, doughnut,icing, plane

bpy.ops.object.select_all(action='DESELECT')

# select just right object
bpy.context.view_layer.objects.active = ice

# bpy.ops.object.editmode_toggle()
Mode('edit')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0, 0, 0.05), plane_no=(
    0, 0, 1), use_fill=False, clear_inner=True)
# bpy.ops.mesh.delete(type='VERT')
Mode('obj')
bpy.ops.object.modifier_add(type='SOLIDIFY')
bpy.context.object.modifiers["Solidify"].thickness = -0.02
bpy.ops.object.editmode_toggle()  # to switch mode
bpy.context.object.modifiers["Solidify"].show_in_editmode = False
# bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_all(action='INVERT')
bpy.ops.mesh.hide(unselected=False)

''' More realisting icing (like melting icing)'''
dropsPercentage = 10
cora.IcingDrops(dropsPercentage)

'''Icing material'''
activeObject = bpy.context.active_object  # Set active object to variable
# set new material to variable
ice_mat = bpy.data.materials.new(name="icing_mat")
activeObject.data.materials.append(ice_mat)  # add the material to the object
ice_mat.use_nodes = True
#bpy.context.object.active_material_index = 0
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (
    0.8, 0.23, 0.56, 1)
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs['Subsurface Color'].default_value = (
    0.8, 0.23, 0.44, 1)
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs['Subsurface'].default_value = 0.3
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.34
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[0] = 0.3
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[1] = 0.1
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[2] = 0.1
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0.6
# (0.39, 0.006, 0.26, 1)
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[17].default_value = 0.5
bpy.data.materials["icing_mat"].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 2000

''' Doughnut material'''
bpy.context.view_layer.objects.active = dou
activeObject2 = bpy.context.active_object  # Set active object to variable
# set new material to variable
dou_mat = bpy.data.materials.new(name="dou_mat")
activeObject2.data.materials.append(dou_mat)  # add the material to the object
dou_mat.use_nodes = True
# Node properties
principled_dou = bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"]
matOut = bpy.data.materials["dou_mat"].node_tree.nodes["Material Output"]
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
    0.8, 0.58, 0.34, 1)
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs[3].default_value = (
    0.8, 0.47, 0.4, 1)
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs['Subsurface'].default_value = 0.15
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.6
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[0] = 0.1
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[1] = 0.1
bpy.data.materials["dou_mat"].node_tree.nodes["Principled BSDF"].inputs[2].default_value[2] = 0.1


''' Plane material'''
bpy.context.view_layer.objects.active = plane
activeObject3 = bpy.context.active_object  # Set active object to variable
plane_mat = bpy.data.materials.new(
    name="plane_mat")  # set new material to variable
activeObject3.data.materials.append(
    plane_mat)  # add the material to the object
plane_mat.use_nodes = True
principled_plane = bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"]
planeOut = bpy.data.materials["plane_mat"].node_tree.nodes["Material Output"]
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
    0.8, 0.3, 0.7, 1)
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[1].default_value = 0.22
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[3].default_value = (
    0.8, 0.38, 0.74, 1)

''' Doughnut shader'''
bpy.context.view_layer.objects.active = dou
dou_nodes = dou_mat.node_tree.nodes

# Define the shaders and their properties
image_texture = dou_nodes.new(type='ShaderNodeTexImage')
image_texture.image = bpy.data.images.load(myDir+'/cora.png')

overlay = dou_nodes.new(type='ShaderNodeMixRGB')
bpy.data.materials["dou_mat"].node_tree.nodes["Mix"].blend_type = 'OVERLAY'
bpy.data.materials["dou_mat"].node_tree.nodes["Mix"].inputs[2].default_value = (
    0.5, 0.2, 0.045, 1)

add = dou_nodes.new(type='ShaderNodeMixRGB')
bpy.data.materials["dou_mat"].node_tree.nodes["Mix.001"].blend_type = 'ADD'

noise1 = dou_nodes.new(type='ShaderNodeTexNoise')
bpy.data.materials["dou_mat"].node_tree.nodes["Noise Texture"].inputs[2].default_value = 2000

noise2 = dou_nodes.new(type='ShaderNodeTexNoise')
bpy.data.materials["dou_mat"].node_tree.nodes["Noise Texture.001"].inputs[2].default_value = 200

textCoord = dou_nodes.new(type='ShaderNodeTexCoord')

colorRamp = dou_nodes.new(type='ShaderNodeValToRGB')
bpy.data.materials["dou_mat"].node_tree.nodes["ColorRamp"].color_ramp.elements[0].position = 0.5

displ = dou_nodes.new(type='ShaderNodeDisplacement')

# Define node links
links = dou_mat.node_tree.links
link1 = links.new(image_texture.outputs['Color'], overlay.inputs['Color1'])
link2 = links.new(overlay.outputs['Color'],
                  principled_dou.inputs['Base Color'])
link3 = links.new(overlay.inputs['Fac'], add.outputs['Color'])
link4 = links.new(displ.inputs['Height'], add.outputs['Color'])
link5 = links.new(displ.outputs['Displacement'], matOut.inputs['Displacement'])
link6 = links.new(colorRamp.outputs['Color'], add.inputs['Color1'])
link7 = links.new(noise1.outputs['Fac'], add.inputs['Color2'])
link8 = links.new(noise2.outputs['Fac'], colorRamp.inputs['Fac'])
link9 = links.new(noise1.inputs['Vector'], textCoord.outputs['Object'])
link10 = links.new(noise2.inputs['Vector'], textCoord.outputs['Object'])

''' Plane shader'''
bpy.context.view_layer.objects.active = plane
plane_nodes = plane_mat.node_tree.nodes

# Define the shaders and their properties
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[4].default_value = 0.9
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[7].default_value = 0.25
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[14].default_value = 2000
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 1
bpy.data.materials["plane_mat"].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 0.24

noiseTex = plane_nodes.new(type='ShaderNodeTexNoise')

hue1 = plane_nodes.new(type='ShaderNodeHueSaturation')
bpy.data.materials["plane_mat"].node_tree.nodes["Hue Saturation Value"].inputs[1].default_value = 1500

hue2 = plane_nodes.new(type='ShaderNodeHueSaturation')
bpy.data.materials["plane_mat"].node_tree.nodes["Hue Saturation Value.001"].inputs[3].default_value = 0.385
bpy.data.materials["plane_mat"].node_tree.nodes["Hue Saturation Value.001"].inputs[0].default_value = 0.7

mix = plane_nodes.new(type='ShaderNodeMixRGB')
bpy.data.materials["plane_mat"].node_tree.nodes["Mix"].inputs[0].default_value = 0.8

rgb = plane_nodes.new(type='ShaderNodeRGB')
bpy.data.materials["plane_mat"].node_tree.nodes["RGB"].outputs[0].default_value = (
    0.4, 0.04, 1, 1)

layerW = plane_nodes.new(type='ShaderNodeLayerWeight')
bpy.data.materials["plane_mat"].node_tree.nodes["Layer Weight"].inputs[0].default_value = 0.05


emission = plane_nodes.new(type='ShaderNodeEmission')
bpy.data.materials["plane_mat"].node_tree.nodes["Emission"].inputs[1].default_value = 2

mixShader = plane_nodes.new(type='ShaderNodeMixShader')

voronoi = plane_nodes.new(type='ShaderNodeTexVoronoi')
bpy.data.materials["plane_mat"].node_tree.nodes["Voronoi Texture"].inputs[2].default_value = 4

displacement = plane_nodes.new(type='ShaderNodeDisplacement')
bpy.data.materials["plane_mat"].node_tree.nodes["Displacement"].inputs[1].default_value = 1
bpy.data.materials["plane_mat"].node_tree.nodes["Displacement"].inputs[2].default_value = 0.05

textCoord2 = plane_nodes.new(type='ShaderNodeTexCoord')

# Define node links
links2 = plane_mat.node_tree.links
link11 = links2.new(noiseTex.outputs['Color'], hue1.inputs['Color'])
link12 = links2.new(hue1.outputs['Color'], mix.inputs['Color1'])
link13 = links2.new(mix.inputs['Color2'], rgb.outputs['Color'])
link14 = links2.new(
    principled_plane.inputs['Base Color'], mix.outputs['Color'])
link15 = links2.new(mix.outputs['Color'], hue2.inputs['Color'])
link16 = links2.new(hue2.outputs['Color'], emission.inputs['Color'])
link17 = links2.new(principled_plane.outputs['BSDF'], mixShader.inputs[1])
link18 = links2.new(emission.outputs['Emission'], mixShader.inputs[2])
link19 = links2.new(mixShader.inputs['Fac'], layerW.outputs['Facing'])
link20 = links2.new(planeOut.inputs['Surface'], mixShader.outputs['Shader'])
link21 = links2.new(
    planeOut.inputs['Displacement'], displacement.outputs['Displacement'])
link22 = links2.new(displacement.inputs['Height'], voronoi.outputs['Distance'])
link23 = links2.new(voronoi.inputs['Vector'], textCoord2.outputs['Generated'])

'''Denoiser'''
bpy.context.view_layer.cycles.denoising_store_passes = True

bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
nodes = bpy.context.scene.node_tree.nodes
compositorLinks = tree.links

# Check if denoise already exist
nodeDenoise = nodes.get("Denoise", None)
if nodeDenoise is not None:
    print("Denoising already exists")
else:

    denoise = tree.nodes.new('CompositorNodeDenoise')
    renderL = tree.nodes["Render Layers"]
    composite = tree.nodes["Composite"]

    Link01 = compositorLinks.new(
        denoise.inputs['Image'], renderL.outputs["Noisy Image"])
    Link02 = compositorLinks.new(
        denoise.inputs['Normal'], renderL.outputs["Denoising Normal"])
    Link03 = compositorLinks.new(
        denoise.inputs['Albedo'], renderL.outputs["Denoising Albedo"])
    Link04 = compositorLinks.new(
        composite.inputs['Image'], denoise.outputs['Image'])


'''Rendering and saving the image'''
outputImg = myDir + '/alienDoughnut'
bpy.data.scenes['Scene'].render.filepath = outputImg
# bpy.context.scene.render.resolution_x = resX # [pixels]
# bpy.context.scene.render.resolution_y = resY # [pixels]
bpy.context.scene.render.resolution_percentage = 100
bpy.ops.render.render(write_still=True)
