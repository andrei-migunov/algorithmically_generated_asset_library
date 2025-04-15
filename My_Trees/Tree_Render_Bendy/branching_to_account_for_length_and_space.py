#texture files were found at https://polyhaven.com/textures/wood/natural

import bpy
import math
import os
import random
from pathlib import Path

# Get the path to the current script's directory
script_dir = Path(__file__).parent

# Define the folder for saving the generated blend files
blend_folder_path = script_dir / "Bendy_Trees_Space"

# Ensure the folder exists (create it if it doesn't)
blend_folder_path.mkdir(parents=True, exist_ok=True)

# Define the name of the blend file base (without the extension)
base_blend_name = "generated_tree3d_bendy_wleavesTest"

# Build the full path to the .blend file
blend_name = f"{base_blend_name}.blend"
full_path = blend_folder_path / blend_name

# Check if the file already exists, and if so, modify the filename to avoid overwriting
i = 0
while os.path.exists(full_path):
    # Generate the next numbered filename
    blend_name = f"{base_blend_name}{i}.blend"
    full_path = blend_folder_path / blend_name
    i += 1


def create_connected_low_poly_tree(branches_per_level=4, max_depth=6, max_height=6, trunk_thickness=0.2, thickness_reduction=0.7, branch_length=1.0, branch_length_reduction=0.8, add_leaves=False):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Create a new curve data block for the tree
    tree_curve = bpy.data.curves.new(name='TreeCurve', type='CURVE')
    tree_curve.dimensions = '3D'
    tree_curve.resolution_u = 0 #will effect how rigid the tree looks
    tree_curve.use_fill_caps = True  # Enable fill caps to close the ends
    
    # Create a new object with the curve
    tree_obj = bpy.data.objects.new('Tree', tree_curve)
    bpy.context.collection.objects.link(tree_obj)
    
    # Parameters
    initial_thickness = trunk_thickness
    
    # Recursive function to create branches
    def create_branch(start_point, direction, thickness, depth, branch_length):
        if depth == 0:
            return
        
        # Vary branch length based on the passed branch_length and depth
        actual_branch_length = branch_length * (max_height / max_depth)
        actual_branch_length *= (branch_length_reduction ** (max_depth - depth))  # Reduce length with depth
        
        # Slight bend in the branch
        bend_factor = random.uniform(-0.3, 0.3)
        bend_axis = random.choice([[1,0,0], [0,1,0]])
        direction_bent = rotate_vector(direction, bend_axis, bend_factor)
        direction_bent = normalize(direction_bent)
        
        # Calculate end point
        end_point = [start_point[i] + actual_branch_length * direction_bent[i] for i in range(3)]
        
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
            [branches_per_level - 1, branches_per_level], weights=[0.7, 0.3], k=1
        )[0]
        
        for _ in range(actual_branch_count):
            spread_factor = (max_depth - depth + 4) / max_depth  # Higher depth => larger spread
            max_angle = math.radians(60)  # Max outward angle for the highest branches
            angle = random.uniform(-max_angle * spread_factor, max_angle * spread_factor)
            axis = random.choice([[0,0,1], [0,1,0], [1,0,0]])
            new_direction = rotate_vector(direction_bent, axis, angle)
            new_direction = normalize(new_direction)
            create_branch(end_point, new_direction, new_thickness, next_depth, branch_length)
    
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
    create_branch(start_point, initial_direction, initial_thickness, max_depth, branch_length)
    
    # Set the bevel depth to give the curve thickness
    tree_curve.bevel_depth = 0.02
    tree_curve.bevel_resolution = 5
    tree_curve.fill_mode = 'FULL'

    # Convert all curves to meshes
    for obj in bpy.context.scene.objects:
        if obj.type == 'CURVE':
            # Ensure the object is active and selected
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.convert(target='MESH')
            print(f"Converted curve {obj.name} to mesh.")
    
    # Applying the texture
    applyTexture("Tree")

    if add_leaves:
        #Weight paint the tree
        weightPaint("Tree")

        #get leaf image as plane
        getLeafImage("Tree Branch.png")

        #create geometry nodes
        generateGeometryNode("Tree", "ImagePlane")

    # Change file to material preview mode
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
    
    # Save the file and print completion confirmation
    bpy.ops.wm.save_as_mainfile(filepath=str(full_path))
    print(f"Tree successfully generated and saved to {blend_folder_path}")

#creates a mesh plane of the given image file
def getLeafImage(nameOfFile):
    #adding the tree branch as a mesh plane
    # Get the directory of the currently running script
    script_dir = os.path.dirname(bpy.data.filepath)
    if not script_dir:
        script_dir = os.path.dirname(__file__)

    image_path = os.path.join(script_dir, nameOfFile)

    if os.path.exists(image_path):
        image = bpy.data.images.load(image_path)
        print(f"Loaded image: {image.name}")

        width = image.size[0]
        height = image.size[1]

        # Define how to scale pixels to Blender units
        scale_factor = 0.01  # 100 pixels = 1 unit

        # Create the plane and scale it to match the image dimensions
        bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0))
        plane = bpy.context.object
        plane.name = "ImagePlane"
        plane.scale.x = (width * scale_factor) / 2  # Blender's default plane is 2x2
        plane.scale.y = (height * scale_factor) / 2

        # Create material with texture
        material = bpy.data.materials.new(name="ImageMaterial")
        plane.data.materials.append(material)
        material.use_nodes = True
        nodes = material.node_tree.nodes

        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.location = (0, 0)
        texture_node.image = image
        texture_node.image.colorspace_settings.is_data = True

        transparent_shader = nodes.new(type='ShaderNodeBsdfTransparent')
        transparent_shader.location = (200, -200)

        bsdf_node = nodes.get('Principled BSDF')
        bsdf_node.location = (400, 0)

        mix_shader = nodes.new(type='ShaderNodeMixShader')
        mix_shader.location = (600, 0)

        material_output_node = nodes.get('Material Output')

        # Link shader nodes
        material.node_tree.links.new(texture_node.outputs["Color"], bsdf_node.inputs["Base Color"])
        material.node_tree.links.new(texture_node.outputs["Alpha"], mix_shader.inputs["Fac"])
        material.node_tree.links.new(transparent_shader.outputs["BSDF"], mix_shader.inputs[1])
        material.node_tree.links.new(bsdf_node.outputs["BSDF"], mix_shader.inputs[2])
        material.node_tree.links.new(mix_shader.outputs["Shader"], material_output_node.inputs["Surface"])

        # Reset UV to fill the texture correctly
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.reset()
        bpy.ops.object.mode_set(mode='OBJECT')

        # Scale down to 2% of its current size
        plane.scale *= 0.02

        # Apply the scale so it's treated as the new default (good for Geometry Nodes)
        bpy.ops.object.transform_apply(scale=True)

        print("Image loaded, textured, scaled down, and ready for Geometry Nodes.")
    else:
        print(f"Image file not found at {image_path}. Please check the file path.")

#weight paints the top half of the specified mesh
def weightPaint(meshName):
    # Look up the object by name
    obj = bpy.data.objects.get(meshName)

    if obj and obj.type == 'MESH':
        # Ensure the object is in Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add a new vertex group
        vgroup = obj.vertex_groups.new(name="TopWeight")

        # Get the mesh data
        mesh = obj.data
        z_values = [v.co.z for v in mesh.vertices]
        z_threshold = min(z_values) + (max(z_values) - min(z_values)) * 0.5  # Midpoint on Z-axis

        # Assign weights
        for v in mesh.vertices:
            weight = 1.0 if v.co.z >= z_threshold else 0.0
            vgroup.add([v.index], weight, 'REPLACE')

        print(f"Weight painting applied to vertices above {z_threshold} on the Z-axis.")

        # Switch to Weight Paint mode (optional)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    else:
        print("No active mesh object selected.")

#creates nodes on the mesh given and places the nodeMesh at each of those points
def generateGeometryNode(meshName, nodeMesh):
    # Get tree mesh
    tree = bpy.data.objects[meshName]

    # Add Geometry Nodes modifier
    modifier = tree.modifiers.new(name="GeometryNodes", type='NODES')

    # Create a new node group and assign it
    new_group = bpy.data.node_groups.new("TreeGeometryNodes", 'GeometryNodeTree')
    modifier.node_group = new_group

    # Add Group Input and Output nodes
    input_node = new_group.nodes.new("NodeGroupInput")
    input_node.location = (-500, 0)

    output_node = new_group.nodes.new("NodeGroupOutput")
    output_node.location = (400, 0)

    new_group.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    new_group.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # Add the Distribute Points on Faces node
    distribute_node = new_group.nodes.new("GeometryNodeDistributePointsOnFaces")
    distribute_node.location = (-150, 0)
    bpy.data.node_groups["TreeGeometryNodes"].nodes["Distribute Points on Faces"].distribute_method = 'POISSON' #sets the distribution method to poisson disk which stops points from being too close to eachother
    bpy.data.node_groups["TreeGeometryNodes"].nodes["Distribute Points on Faces"].inputs[3].default_value = 30 #sets the leaf branch density to 30

    # Add Join Geometry node
    join_node = new_group.nodes.new("GeometryNodeJoinGeometry")
    join_node.location = (150, 0)

    # Add Instance on Points node
    instance_on_points_node = new_group.nodes.new("GeometryNodeInstanceOnPoints")
    instance_on_points_node.location = (300, 0)

    # Add Object Info node for the "ImagePlane" object
    object_info_node = new_group.nodes.new("GeometryNodeObjectInfo")
    object_info_node.location = (450, 0)

    # Set the Object Info node to reference the "ImagePlane" object
    object_info_node.inputs["Object"].default_value = bpy.data.objects[nodeMesh]

    # Add Named Attribute node to read the existing vertex group
    named_attr_node = new_group.nodes.new("GeometryNodeInputNamedAttribute")
    named_attr_node.location = (-300, -200)
    named_attr_node.data_type = 'FLOAT'  # Because vertex groups are float-based
    named_attr_node.inputs["Name"].default_value = "TopWeight"  # This is what tells the node to read the vertex group

    # Wire up the nodes
    links = new_group.links
    links.new(input_node.outputs[0], distribute_node.inputs["Mesh"])
    links.new(input_node.outputs[0], join_node.inputs[0])
    links.new(distribute_node.outputs["Points"], instance_on_points_node.inputs["Points"])
    links.new(instance_on_points_node.outputs["Instances"], join_node.inputs[0])
    links.new(object_info_node.outputs["Geometry"], instance_on_points_node.inputs["Instance"])
    links.new(named_attr_node.outputs["Attribute"], distribute_node.inputs["Density Factor"])
    links.new(distribute_node.outputs["Rotation"], instance_on_points_node.inputs["Rotation"])
    links.new(join_node.outputs[0], output_node.inputs[0])

#applies the tree texture to the given mesh
def applyTexture(meshName):
    # Name of the mesh object to select
    mesh_name = meshName

    # Define the relative path from the script file to the texture file
    base_color_relative_path = os.path.join("Textures", "bark_willow_02_4k.blend", "textures", "bark_willow_02_diff_4k.jpg")
    roughness_relative_path = os.path.join("Textures", "bark_willow_02_4k.blend", "textures", "bark_willow_02_rough_4k.exr")
    normal_relative_path = os.path.join("Textures", "bark_willow_02_4k.blend", "textures", "bark_willow_02_nor_gl_4k.exr")
    displacement_relative_path = os.path.join("Textures", "bark_willow_02_4k.blend", "textures", "bark_willow_02_disp_4k.png")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the image
    base_color_path = os.path.join(script_dir, base_color_relative_path)
    roughness_path = os.path.join(script_dir, roughness_relative_path)
    normal_path = os.path.join(script_dir, normal_relative_path)
    displacement_path = os.path.join(script_dir, displacement_relative_path)

    # Ensure the path is valid
    if not os.path.exists(base_color_path):
        print(f"Warning: Base Color not found at {base_color_path}")
    else:
        print(f"Base Color found: {base_color_path}")
    
    if not os.path.exists(roughness_path):
        print(f"Warning: Roughness not found at {roughness_path}")
    else:
        print(f"Roughness found: {roughness_path}")

    if not os.path.exists(normal_path):
        print(f"Warning: Normals not found at {normal_path}")
    else:
        print(f"Normals found: {normal_path}")

    if not os.path.exists(displacement_path):
        print(f"Warning: Displacement not found at {displacement_path}")
    else:
        print(f"Displacement found: {displacement_path}")

    # Select the mesh object
    obj = bpy.data.objects.get(mesh_name)
    if obj and obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Create a new material
        mat = bpy.data.materials.new(name="BarkMaterial")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    
        # Get the Principled BSDF node
        nodes = mat.node_tree.nodes
        bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')

        # Get the Material Output node
        output_node = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    
        # Create the texture nodes, normal map node, and displacement node
        tex_base_color = nodes.new(type='ShaderNodeTexImage')
        tex_base_color.image = bpy.data.images.load(base_color_path)

        tex_roughness = nodes.new(type='ShaderNodeTexImage')
        tex_roughness.image = bpy.data.images.load(roughness_path)

        tex_normal = nodes.new(type='ShaderNodeTexImage')
        tex_normal.image = bpy.data.images.load(normal_path)

        tex_displacement = nodes.new(type='ShaderNodeTexImage')
        tex_displacement.image = bpy.data.images.load(displacement_path)

        normal_map = nodes.new(type='ShaderNodeNormalMap')

        displacement = nodes.new(type='ShaderNodeDisplacement')
    
        # Link the texture nodes to their proper output locations
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_base_color.outputs['Color'])
        mat.node_tree.links.new(bsdf.inputs['Roughness'], tex_roughness.outputs['Color'])
        mat.node_tree.links.new(normal_map.inputs['Color'], tex_normal.outputs['Color'])
        mat.node_tree.links.new(bsdf.inputs['Normal'], normal_map.outputs['Normal'])
        mat.node_tree.links.new(displacement.inputs['Height'], tex_displacement.outputs['Color'])
        mat.node_tree.links.new(output_node.inputs['Displacement'], displacement.outputs['Displacement'])
    
        print("Material with texture applied successfully.")
    else:
        print(f"Object '{mesh_name}' not found or is not a mesh.")
    
# Set parameters
branches_per_level = 5     # determines how many branches there are at each level
max_depth = 5               # determines how many levels of branches there are (WARNING: this is an exponential function)
max_height = 10            # acts as a final target height scaling factor
trunk_thickness = 5       # Initial thickness of the trunk
thickness_reduction = 0.6 # Rate at which thickness decreases with each level
branch_length = 1.0      # Acts as the starting point for how long each segment of the tree is at the trunk level
branch_length_reduction = 0.8 #reduction of branch length with depth
add_leaves = True #should the tree have leaves or not

# Run the function to create the tree
create_connected_low_poly_tree(branches_per_level, max_depth, max_height, trunk_thickness, thickness_reduction, branch_length, branch_length_reduction, add_leaves)