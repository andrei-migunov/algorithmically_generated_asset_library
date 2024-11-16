import bpy
import math
import os

blend_file_path = "generated_tree3d_wleaves.blend"

if os.path.exists(blend_file_path):
    os.remove(blend_file_path)

# Full path to the lsystem.txt file
file_path = r"C:\Users\andre\Dropbox\Code\Tree_Render\lsystem3d.txt"

# Read the L-system string
with open(file_path, "r") as file:
    lsystem_string = file.read().strip()

# Parameters
angle = math.radians(25.7)
length = 1.0
branch_thickness = 0.05

# Create a new collection for the tree
tree_collection = bpy.data.collections.new("LSystemTree")
bpy.context.scene.collection.children.link(tree_collection)

# Stack for storing positions and orientations
stack = []
pos = [0, 0, 0]
dir = [0, 0, 1]
right = [1, 0, 0]
up = [0, 1, 0]

def rotate_vector(vector, axis, angle):
    """Rotate vector around given axis by angle."""
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    u, v, w = axis
    x, y, z = vector
    return [
        (cos_theta + (1 - cos_theta) * u * u) * x + ((1 - cos_theta) * u * v - w * sin_theta) * y + ((1 - cos_theta) * u * w + v * sin_theta) * z,
        ((1 - cos_theta) * u * v + w * sin_theta) * x + (cos_theta + (1 - cos_theta) * v * v) * y + ((1 - cos_theta) * v * w - u * sin_theta) * z,
        ((1 - cos_theta) * u * w - v * sin_theta) * x + ((1 - cos_theta) * v * w + u * sin_theta) * y + (cos_theta + (1 - cos_theta) * w * w) * z
    ]

def create_cylinder(start, end, radius):
    """Create a cylinder from start to end"""
    # Calculate the midpoint
    mid = [(start[i] + end[i]) / 2 for i in range(3)]
    
    # Calculate the length of the cylinder
    length = math.sqrt(sum((end[i] - start[i]) ** 2 for i in range(3)))
    
    # Calculate the direction of the cylinder
    direction = [end[i] - start[i] for i in range(3)]
    direction_length = math.sqrt(sum(d ** 2 for d in direction))
    direction = [d / direction_length for d in direction]

    # Create the cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    cylinder = bpy.context.object
    
    # Align the cylinder to the direction
    rot_quat = direction_to_quaternion(direction)
    cylinder.rotation_mode = 'QUATERNION'
    cylinder.rotation_quaternion = rot_quat

    tree_collection.objects.link(cylinder)
    bpy.context.collection.objects.unlink(cylinder)

def direction_to_quaternion(direction):
    """Convert a direction vector to a quaternion"""
    up = [0, 0, 1]
    if direction == up:
        return [1, 0, 0, 0]
    if direction == [-up[0], -up[1], -up[2]]:
        return [0, 0, 0, 1]

    rot_axis = [up[1] * direction[2] - up[2] * direction[1],
                up[2] * direction[0] - up[0] * direction[2],
                up[0] * direction[1] - up[1] * direction[0]]
    rot_angle = math.acos(sum(up[i] * direction[i] for i in range(3)))

    norm = math.sqrt(sum(a ** 2 for a in rot_axis))
    rot_axis = [a / norm for a in rot_axis]

    w = math.cos(rot_angle / 2)
    x = rot_axis[0] * math.sin(rot_angle / 2)
    y = rot_axis[1] * math.sin(rot_angle / 2)
    z = rot_axis[2] * math.sin(rot_angle / 2)

    return [w, x, y, z]

# Process the L-system string
for index, char in enumerate(lsystem_string):
    if char == "F":
        new_pos = [pos[i] + dir[i] for i in range(3)]
        create_cylinder(pos, new_pos, branch_thickness)
        pos = new_pos
    elif char == "+":
        dir = rotate_vector(dir, [0, 0, 1], angle)
    elif char == "-":
        dir = rotate_vector(dir, [0, 0, 1], -angle)
    elif char == "&":
        dir = rotate_vector(dir, [1, 0, 0], angle)
    elif char == "^":
        dir = rotate_vector(dir, [1, 0, 0], -angle)
    elif char == "\\":
        dir = rotate_vector(dir, [0, 1, 0], angle)
    elif char == "/":
        dir = rotate_vector(dir, [0, 1, 0], -angle)
    elif char == "[":
        stack.append((pos[:], dir[:], right[:], up[:]))
    elif char == "]":
        if stack:
            pos, dir, right, up = stack.pop()

print("L-system generation completed")

# Save the Blender file
bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)
