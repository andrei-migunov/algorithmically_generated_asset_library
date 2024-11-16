import bpy
import math

# Full path to the lsystem.txt file (using raw string or forward slashes)
file_path = r"C:\Users\andre\Dropbox\Code\Tree_Render\lsystem.txt"  # Update this to the correct path

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

# Stack for storing positions and directions
stack = []
pos = [0, 0, 0]
dir = [0, 0, 1]
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

def add_branch(start, end, radius):
    """Add a cylindrical branch from start to end with the given radius"""
    # Calculate the direction and length of the branch
    direction = [end[i] - start[i] for i in range(3)]
    height = math.sqrt(sum(d ** 2 for d in direction))
    mid = [(start[i] + end[i]) / 2 for i in range(3)]
    
    # Add a cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=mid)
    branch = bpy.context.object

    # Align the cylinder with the branch direction
    direction = [end[i] - start[i] for i in range(3)]
    rot_z = math.atan2(direction[1], direction[0])
    rot_y = math.acos(direction[2] / height)
    branch.rotation_euler = (0, rot_y, rot_z)
    tree_collection.objects.link(branch)
    bpy.context.collection.objects.unlink(branch)

# Process the L-system string
for index, char in enumerate(lsystem_string):
    if char == "F":
        new_pos = [pos[0] + dir[0] * length, pos[1] + dir[1] * length, pos[2] + dir[2] * length]
        add_branch(pos, new_pos, branch_thickness)
        pos = new_pos
    elif char == "+":
        dir = rotate_vector(dir, up, angle)
    elif char == "-":
        dir = rotate_vector(dir, up, -angle)
    elif char == "&":
        dir = rotate_vector(dir, [1, 0, 0], angle)
    elif char == "^":
        dir = rotate_vector(dir, [1, 0, 0], -angle)
    elif char == "\\":
        dir = rotate_vector(dir, [0, 0, 1], angle)
    elif char == "/":
        dir = rotate_vector(dir, [0, 0, 1], -angle)
    elif char == "[":
        stack.append((pos[:], dir[:], up[:]))
    elif char == "]":
        if stack:
            pos, dir, up = stack.pop()

# Save the Blender file
bpy.ops.wm.save_as_mainfile(filepath="generated_tree_2d.blend")