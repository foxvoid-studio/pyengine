import os
import numpy as np
import pywavefront
from pyengine.core.logger import Logger


def load_obj_model(file_path: str):
    """
    Loads an OBJ file and separates geometry by material.
    Returns a list of dictionaries: [{'vertices': np.array, 'texture_path': str|None}, ...]
    """
    if not os.path.exists(file_path):
        Logger.error(f"OBJ File not found: {file_path}")
        return []

    try:
        # Load the scene. PyWavefront automatically parses the associated .mtl file
        scene = pywavefront.Wavefront(
            file_path, 
            collect_faces=True, 
            create_materials=True, 
            strict=False
        )
        
        model_parts = []

        # Iterate over each material found in the OBJ
        for name, material in scene.materials.items():
            
            # --- 1. Extract Texture Path ---
            texture_path = None
            # PyWavefront stores the texture object in material.texture
            # We look for the diffuse texture (map_Kd)
            if material.texture:
                texture_path = material.texture.path
                # Sometimes the path is absolute or relative. We keep it as is for now.

            # --- 2. Extract Vertices (Same logic as before) ---
            format_str = material.vertex_format
            data = material.vertices
            data_np = np.array(data, dtype=np.float32)
            
            vertices_flat = np.array([], dtype=np.float32)

            if format_str == 'T2F_V3F':
                count = len(data_np) // 5
                reshaped = data_np.reshape((count, 5))
                # Swap columns: XYZ (2,3,4) then UV (0,1)
                corrected = reshaped[:, [2, 3, 4, 0, 1]]
                vertices_flat = corrected.flatten()
                
            elif format_str == 'V3F':
                count = len(data_np) // 3
                reshaped = data_np.reshape((count, 3))
                zeros = np.zeros((count, 2), dtype=np.float32)
                vertices_flat = np.hstack((reshaped, zeros)).flatten()

            elif format_str == 'N3F_V3F':
                 count = len(data_np) // 6
                 reshaped = data_np.reshape((count, 6))
                 positions = reshaped[:, 3:6]
                 zeros = np.zeros((count, 2), dtype=np.float32)
                 vertices_flat = np.hstack((positions, zeros)).flatten()
            
            elif 'T2F' in format_str and 'N3F' in format_str and 'V3F' in format_str:
                 # Assuming 8 floats (T2F_N3F_V3F)
                 count = len(data_np) // 8
                 reshaped = data_np.reshape((count, 8))
                 # Indices: 0,1=UV | 2,3,4=Norm | 5,6,7=Pos -> Keep Pos + UV
                 corrected = reshaped[:, [5, 6, 7, 0, 1]]
                 vertices_flat = corrected.flatten()

            # Only add part if it has vertices
            if len(vertices_flat) > 0:
                model_parts.append({
                    "name": name,
                    "vertices": vertices_flat,
                    "texture_path": texture_path
                })

        Logger.info(f"Loaded OBJ: {file_path} with {len(model_parts)} parts.")
        return model_parts

    except Exception as e:
        Logger.error(f"Failed to load OBJ {file_path}: {e}")
        return []
    