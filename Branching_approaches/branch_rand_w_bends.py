import bpy
import math
import os
import random

# File path where the tree will be saved
blend_file_path = "connected_low_poly_tree.blend"

def create_connected_low_poly_tree(branch_count=4, max_height=6, trunk_thickness=0.2, thickness_reduction=0.7):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create a new curve data block for the tree
    tree_curve = bpy.data.curves.new(name='TreeCurve', type='CURVE')
    tree_curve.dimensions = '3D'
    tree_curve.resolution_u = 2
    
    # Create a new object with the curve
    tree_obj = bpy.data.objects.new('Tree', tree_curve)
    bpy.context.collection.objects.link(tree_obj)
    
    # Parameters
    initial_thickness = trunk_thickness
    
    # Recursive function to create branches
    def create_branch(start_point, direction, thickness, depth):
        if depth == 0:
            return
        
        # Vary branch length
        branch_length = random.uniform(0.7, 1.0) * (max_height / branch_count)
        
        # Slight bend in the branch
        bend_factor = random.uniform(-0.3, 0.3)
        bend_axis = random.choice([[1,0,0], [0,1,0]])
        direction_bent = rotate_vector(direction, bend_axis, bend_factor)
        direction_bent = normalize(direction_bent)
        
        # Calculate end point
        end_point = [start_point[i] + branch_length * direction_bent[i] for i in range(3)]
        
        # Create a spline for this branch
        spline = tree_curve.splines.new('BEZIER')
        spline.bezier_points.add(count=2)
        
        # Set start point
        spline.bezier_points[0].co = start_point
        spline.bezier_points[0].radius = thickness
        spline.bezier_points[0].handle_left_type = 'AUTO'
        spline.bezier_points[0].handle_right_type = 'AUTO'
        
        # Set middle point (to create bend)
        mid_point = [ (start_point[i] + end_point[i]) / 2 for i in range(3)]
        offset = [random.uniform(-0.2, 0.2) for _ in range(3)]
        mid_point = [mid_point[i] + offset[i] for i in range(3)]
        spline.bezier_points[1].co = mid_point
        spline.bezier_points[1].radius = (thickness + thickness * thickness_reduction) / 2
        spline.bezier_points[1].handle_left_type = 'AUTO'
        spline.bezier_points[1].handle_right_type = 'AUTO'
        
        # Set end point
        spline.bezier_points[2].co = end_point
        spline.bezier_points[2].radius = thickness * thickness_reduction
        spline.bezier_points[2].handle_left_type = 'AUTO'
        spline.bezier_points[2].handle_right_type = 'AUTO'
        
        # Ensure handles for smooth transitions
        for point in spline.bezier_points:
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'
        
        # Create child branches
        new_thickness = thickness * thickness_reduction
        next_depth = depth - 1
        
        actual_branch_count = random.choices(
            [branch_count - 1, branch_count], weights=[0.7, 0.3], k=1
        )[0]
        
        angle_between_branches = math.radians(50)
        
        for _ in range(actual_branch_count):
            angle = random.uniform(-angle_between_branches, angle_between_branches)
            axis = random.choice([[0,0,1], [0,1,0], [1,0,0]])
            new_direction = rotate_vector(direction_bent, axis, angle)
            new_direction = normalize(new_direction)
            create_branch(end_point, new_direction, new_thickness, next_depth)
    
    # Function to rotate a vector around an axis by a given angle
    def rotate_vector(vector, axis, angle):
        ux, uy, uz = axis
        x, y, z = vector
        cos_theta = math.cos(angle)
        sin_theta = math.sin(angle)
        dot = ux*x + uy*y + uz*z
        cross = [
            uy*z - uz*y,
            uz*x - ux*z,
            ux*y - uy*x
        ]
        rotated_vector = [
            cos_theta*x + sin_theta*cross[0] + (1 - cos_theta)*dot*ux,
            cos_theta*y + sin_theta*cross[1] + (1 - cos_theta)*dot*uy,
            cos_theta*z + sin_theta*cross[2] + (1 - cos_theta)*dot*uz
        ]
        return rotated_vector
    
    def normalize(vec):
        length = math.sqrt(sum(v ** 2 for v in vec))
        if length == 0:
            return vec
        return [v / length for v in vec]
    
    # Start with the initial trunk
    start_point = (0, 0, 0)
    initial_direction = (0, 0, 1)
    create_branch(start_point, initial_direction, initial_thickness, branch_count)
    
    # Set the bevel depth to give the curve thickness
    tree_curve.bevel_depth = 0.02
    tree_curve.bevel_resolution = 2
    tree_curve.fill_mode = 'FULL'
    
    print("Tree generated.")
    
# Set parameters
branch_count = 4          # Number of recursive branching levels
max_height = 6            # Maximum tree height
trunk_thickness = 3     # Initial thickness of the trunk
thickness_reduction = 0.7 # Rate at which thickness decreases with each level

# Run the function to create the tree
create_connected_low_poly_tree(branch_count, max_height, trunk_thickness, thickness_reduction)

# Save the tree to a .blend file
if os.path.exists(blend_file_path):
    os.remove(blend_file_path)
bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

print("Connected low-poly tree generated with smooth connections and saved to", blend_file_path)
print("Connected low-poly tree generated with smooth connections and saved to", blend_file_path)