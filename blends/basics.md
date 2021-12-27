# Basics for catching up

reset - bpy.ops.wm.read_factory_settings()
**Hot Keys**
- G (move), S(scale), R(rotate)
  - + direction[x,y,z] / hold middle clicker (move along axis) 
    - x - left,right
    - y - back,fort
    - z - up,down

- Right Click (escape action)
- Middle mouse button (Orbit Selected Object)

- Shift + Middle mouse (Pan around the scene)

- Zoom (Ctrl + Middle mouse button)

- "`" + 1-9 (Quick View Snap on Selected Object)

- Ctrl+Alt+0 - snap camera to main object/mesh location

- Press 'N',go to view, lock camera to view

- Alt+G , snap any object to center of grid

# Main Ideas
- Scene
  - Light
  - Camera
  - Object(Mesh)
    - AFAIK there can be only one mesh per object. 
    - However there can be multiple objects sharing the same mesh data block.
    - obj.name gives you the object name. 
    - obj.data.name gives you mesh name. 


light_data = bpy.data.lights.new('light', type='POINT')
light = bpy.data.objects.new('light', light_data)
bpy.context.collections.objects.link(light)
light.location = (3, 4, -5)