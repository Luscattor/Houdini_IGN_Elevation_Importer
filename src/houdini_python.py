# À utiliser dans un Python SOP au lieu d'un Point Wrangle
import json
import hou

# Récupérer le nœud et la géométrie
geo = hou.pwd().geometry()

# Chemin vers votre fichier JSON
json_file_path = "F:tiles_metadata.json"

# Lire le fichier JSON
try:
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Supprimer tous les points existants
    geo.clear()
    
    # Accéder à la liste des tiles
    tiles = data.get("tiles", [])
    
    # Créer les attributs
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
    
    # Pour chaque tile, créer un point avec la position moyenne
    for i, tile in enumerate(tiles):
        # Calculer la position moyenne entre min et max
        center_x = (tile["minx"] + tile["maxx"]) / 2.0
        center_z = (tile["miny"] + tile["maxy"]) / 2.0  # Y devient Z dans Houdini
        
        # Créer un nouveau point
        pt = geo.createPoint()
        
        # Définir la position du point (X, Y=0, Z)
        pt.setPosition([center_x, 0.0, center_z])
        
        # Ajouter des attributs pour stocker les informations de la tile
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
    print(f"Erreur lors de la lecture du fichier JSON: {e}")