import bpy
import math
import os
import random

# File path where the tree will be saved
blend_file_path = "connected_low_poly_tree.blend"

def create_connected_low_poly_tree(branch_count=3, max_height=6, trunk_thickness=0.2, thickness_reduction=0.7):
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Parameters for tree height, trunk thickness, and branching angle
    base_height = max_height / branch_count
    initial_thickness = trunk_thickness
    
    # Recursive function to create a branch
    def create_branch(start_location, direction, thickness, depth):
        if depth == 0:
            return

        # Calculate the end point of the current branch
        end_location = [
            start_location[i] + base_height * direction[i] for i in range(3)
        ]

        # Create a cylinder for this branch segment
        bpy.ops.mesh.primitive_cylinder_add(
            radius=thickness,
            depth=base_height,
            location=[(start_location[i] + end_location[i]) / 2 for i in range(3)]
        )
        branch = bpy.context.object
        branch.name = f"Branch_depth_{depth}"

        # Align the branch to the direction vector
        rot_quat = direction_to_quaternion(direction)
        branch.rotation_mode = 'QUATERNION'
        branch.rotation_quaternion = rot_quat

        # Set up new parameters for child branches
        new_thickness = thickness * thickness_reduction
        next_depth = depth - 1

        # Randomly determine the number of branches at this level
        actual_branch_count = random.choices(
            [branch_count - 1, branch_count], weights=[0.7, 0.3], k=1
        )[0]

        # Set angles between branches based on actual branch count
        angle_offsets = get_angle_offsets(actual_branch_count)

        # Generate child branches around this branch
        for angle_offset in angle_offsets:
            new_direction = [
                math.cos(angle_offset),
                math.sin(angle_offset),
                1
            ]
            new_direction = normalize(new_direction)
            create_branch(end_location, new_direction, new_thickness, next_depth)

    # Helper function to get angle offsets with a lower bound to prevent overlap
    def get_angle_offsets(num_branches, min_separation=math.radians(15)):
        angle_step = math.radians(360 / num_branches)
        if num_branches == 2:
            # Ensure minimum separation between two branches
            offset = random.uniform(min_separation, angle_step - min_separation)
            return [offset, angle_step + offset]
        elif num_branches == 3:
            # For three branches, ensure they are spaced out reasonably
            offsets = [0, random.uniform(1.2, 1.5) * angle_step, random.uniform(2.5, 3) * angle_step]
            offsets = [max(min_separation, off) for off in offsets]
            random.shuffle(offsets)
            return offsets
        else:
            # Standard equal angle distribution with a minimum separation
            return [(angle_step * b + random.uniform(-min_separation, min_separation)) for b in range(num_branches)]

    # Convert direction vector to a quaternion for rotation alignment
    def direction_to_quaternion(direction):
        up = [0, 0, 1]
        axis = cross_product(up, direction)
        angle = math.acos(dot_product(up, direction))
        return quaternion_from_axis_angle(axis, angle)

    # Helper functions for vector calculations
    def normalize(vec):
        length = math.sqrt(sum(v ** 2 for v in vec))
        return [v / length for v in vec]

    def dot_product(v1, v2):
        return sum(v1[i] * v2[i] for i in range(3))

    def cross_product(v1, v2):
        return [
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        ]

    def quaternion_from_axis_angle(axis, angle):
        half_angle = angle / 2.0
        sin_half_angle = math.sin(half_angle)
        return [
            math.cos(half_angle),
            axis[0] * sin_half_angle,
            axis[1] * sin_half_angle,
            axis[2] * sin_half_angle
        ]

    # Create the initial trunk
    start_location = (0, 0, base_height / 2)
    initial_direction = (0, 0, 1)
    create_branch(start_location, initial_direction, initial_thickness, branch_count)

# Set parameters
branch_count = 4          # Number of recursive branching levels
max_height = 6            # Maximum tree height
trunk_thickness = 0.2     # Initial thickness of the trunk
thickness_reduction = 0.7 # Rate at which thickness decreases with each level

# Run the function to create the tree
create_connected_low_poly_tree(branch_count, max_height, trunk_thickness, thickness_reduction)

# Save the tree to a .blend file
if os.path.exists(blend_file_path):
    os.remove(blend_file_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

print("Connected low-poly tree generated with controlled branch angles and saved to", blend_file_path)
