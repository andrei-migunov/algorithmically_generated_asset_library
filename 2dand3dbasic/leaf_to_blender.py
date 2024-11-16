import bpy
import bmesh
import cv2
import numpy as np
import os

# Path to your image and output Blender file
image_path = r'C:\Users\andre\Dropbox\Code\Tree_Render\images\japanese_maple_1.jpg'
output_blend_file = r'C:\Users\andre\Dropbox\Code\Tree_Render\images\japanese_maple_1.blend'

# Remove the existing Blender file if it exists
if os.path.exists(output_blend_file):
    os.remove(output_blend_file)

# Step 1: Load and process the scanned leaf image
leaf_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
leaf_gray = cv2.cvtColor(leaf_image, cv2.COLOR_BGR2GRAY)
_, leaf_mask = cv2.threshold(leaf_gray, 235, 255, cv2.THRESH_BINARY_INV)

# Step 2: Find contours of the leaf
contours, _ = cv2.findContours(leaf_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Select the largest contour assuming it's the leaf
leaf_contour = max(contours, key=cv2.contourArea)

# Scale the contour to fit Blender's scale
scale_factor = 0.01  # Adjust based on the size of the image and desired size in Blender
scaled_contour = leaf_contour * scale_factor

# Step 3: Create the leaf mesh in Blender
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.add(type='MESH', enter_editmode=True)
leaf_mesh = bpy.context.object
bm = bmesh.from_edit_mesh(leaf_mesh.data)

# Convert contour points to Blender vertices
vertices = [bm.verts.new((point[0][0], point[0][1], 0)) for point in scaled_contour]

# Create the face from the vertices using a new approach
if len(vertices) > 2:
    try:
        bm.faces.new(vertices)
    except ValueError:
        # Handle cases where creating a face fails
        print("Failed to create a face with the given vertices.")

# Update the bmesh again to finalize the mesh
bmesh.update_edit_mesh(leaf_mesh.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Step 4: UV unwrap the mesh
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.unwrap(method='ANGLE_BASED')
bpy.ops.object.mode_set(mode='OBJECT')

# Step 5: Apply the leaf texture
# Load the image as a texture
img = bpy.data.images.load(image_path)

# Create a material and set it to use the texture
mat = bpy.data.materials.new(name="LeafMaterial")
mat.use_nodes = True

# Clear all default nodes
nodes = mat.node_tree.nodes
nodes.clear()

# Add texture image node
tex_image = nodes.new(type='ShaderNodeTexImage')
tex_image.image = img

# Add BSDF node
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')

# Add material output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')

# Connect nodes
links = mat.node_tree.links
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

# Assign the material to the mesh
if leaf_mesh.data.materials:
    leaf_mesh.data.materials[0] = mat
else:
    leaf_mesh.data.materials.append(mat)

# Ensure the object uses UV mapping
if not leaf_mesh.data.uv_layers:
    leaf_mesh.data.uv_layers.new(name='UVMap', do_init=True)

# Save the Blender file
bpy.ops.wm.save_as_mainfile(filepath=output_blend_file)

print("Leaf object created and textured successfully. File saved to:", output_blend_file)
