import bpy
import numpy as np
from math import sin, pi, cos
from mathutils import Euler
import colorsys
tau = 2*pi

''' ----------- Scripts cointaining all the general Utils and Functions----------------- '''


def RemoveObject(obj):
    if obj.type == 'MESH':
        if obj.data.name in bpy.data.meshes:
            bpy.data.meshes.remove(obj.data)
        if obj.name in bpy.context.scene.objects:
            bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    else:
        raise NotImplementedError(
            'Other types not implemented yet besides \'MESH\'')


def RemoveAll(type=None):

    if type:
        bpy.ops.object.select_all(action='TOGGLE')
        bpy.ops.object.select_by_type(type=type)
        bpy.ops.object.delete()
    else:
        # Remove all elements in scene except the selected ones
        override = bpy.context.copy()
        override['selected_objects'] = list(bpy.context.scene.objects)
        bpy.ops.object.delete(override)


def SetTheCamera(cam_loc, cam_rot):
    '''
        INPUT : - camera position
        - camera location
        '''
    bpy.ops.object.add(type='CAMERA', location=cam_loc)
    cam = bpy.context.object
    cam.rotation_euler = Euler(cam_rot, 'XYZ')
    bpy.context.scene.camera = cam


def SetTheLight(sun_loc, energy=10, type='POINT', color=(1, 1, 1)):
    '''
        INPUT : - light position
        - light location
        - font type
        - intensity
        - light color (RGB)
        '''
    bpy.ops.object.add(type='LIGHT', location=sun_loc)
    obj = bpy.context.object
    obj = bpy.context.object
    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color


def CreateTorus(nameString, pos, rot, smooth):
    '''
        This create the doughnut base.
        '''
    bpy.ops.mesh.primitive_torus_add(align='WORLD', location=pos, rotation=rot, major_segments=50, minor_segments=20,
                                     mode='MAJOR_MINOR', major_radius=0.25, minor_radius=0.11, abso_major_rad=0.5, abso_minor_rad=0.15, generate_uvs=True)
    obj = bpy.context.object
    if smooth == True:
        # Smooth the mesh
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = 2
        modifier.render_levels = 2
        mesh = obj.data
        for p in mesh.polygons:
            p.use_smooth = True
        bpy.context.active_object.name = nameString


def CreatePlane(plane_loc, nameString):
    bpy.ops.mesh.primitive_plane_add(
        size=10, enter_editmode=False, location=plane_loc)
    obj = bpy.context.object
    bpy.context.active_object.name = nameString


def SmoothTheMesh(obj):
    # Smooth the mesh
    #obj = bpy.context.object
    modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
    modifier.levels = 2
    modifier.render_levels = 2
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = True


def IcingDrops(dropsPercentage):
    '''
    dropsPercentage = percentage of drops in the icing    
    '''

    bpy.ops.mesh.select_random(ratio=dropsPercentage, seed=0, action='SELECT')
    bpy.ops.transform.translate(value=(-0.004, -0.0071, -0.034), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True,
                                use_proportional_edit=True, proportional_edit_falloff='SMOOTH', proportional_size=0.118522, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.mode_set(mode='OBJECT')
