# Use in a Python SOP instead of a Point Wrangle
import json
import hou

# Get the node and geometry
geo = hou.pwd().geometry()

# Path to your JSON file
json_file_path = "F:tiles_metadata.json"

# Read the JSON file
try:
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Remove all existing points
    geo.clear()
    
    # Access the tiles list
    tiles = data.get("tiles", [])
    
    # Create attributes
    geo.addAttrib(hou.attribType.Point, "tile_index", 0)
    geo.addAttrib(hou.attribType.Point, "url", "")
    geo.addAttrib(hou.attribType.Point, "local_name", "")
    geo.addAttrib(hou.attribType.Point, "local_path", "")
    geo.addAttrib(hou.attribType.Point, "minx", 0.0)
    geo.addAttrib(hou.attribType.Point, "miny", 0.0)
    geo.addAttrib(hou.attribType.Point, "maxx", 0.0)
    geo.addAttrib(hou.attribType.Point, "maxy", 0.0)
    geo.addAttrib(hou.attribType.Point, "width_m", 0.0)
    geo.addAttrib(hou.attribType.Point, "height_m", 0.0)
    geo.addAttrib(hou.attribType.Point, "width_px", 0)
    geo.addAttrib(hou.attribType.Point, "height_px", 0)
    geo.addAttrib(hou.attribType.Point, "crs", "")
    
    # For each tile, create a point with the average position
    for i, tile in enumerate(tiles):
        # Calculate the average position between min and max
        center_x = (tile["minx"] + tile["maxx"]) / 2.0
        center_z = (tile["miny"] + tile["maxy"]) / 2.0  # Y becomes Z in Houdini
        
        # Create a new point
        pt = geo.createPoint()
        
        # Set the point position (X, Y=0, Z)
        pt.setPosition([center_x, 0.0, center_z])
        
        # Add attributes to store tile information
        pt.setAttribValue("tile_index", i)
        pt.setAttribValue("url", tile["url"])
        pt.setAttribValue("local_name", tile["local_name"])
        pt.setAttribValue("local_path", tile["local_path"])
        pt.setAttribValue("minx", tile["minx"])
        pt.setAttribValue("miny", tile["miny"])
        pt.setAttribValue("maxx", tile["maxx"])
        pt.setAttribValue("maxy", tile["maxy"])
        pt.setAttribValue("width_m", tile["w_m"])
        pt.setAttribValue("height_m", tile["h_m"])
        pt.setAttribValue("width_px", tile["width_px"])
        pt.setAttribValue("height_px", tile["height_px"])
        pt.setAttribValue("crs", tile["crs"])

except Exception as e:
    print(f"Error reading JSON file: {e}")