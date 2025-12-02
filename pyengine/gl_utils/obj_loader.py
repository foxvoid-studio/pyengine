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
        # Important: create_materials=True ensures PyWavefront parses MTL
        scene = pywavefront.Wavefront(file_path, collect_faces=True, create_materials=True, strict=False)
        model_parts = []

        for name, material in scene.materials.items():
            texture_path = None
            if material.texture:
                texture_path = material.texture.path

            format_str = material.vertex_format
            data = np.array(material.vertices, dtype=np.float32)
            vertices_flat = np.array([], dtype=np.float32)

            # We need standard format: T2F_N3F_V3F (Texture, Normal, Position)
            # This contains 8 floats.
            if 'T2F' in format_str and 'N3F' in format_str and 'V3F' in format_str:
                count = len(data) // 8
                reshaped = data.reshape((count, 8))
                
                # PyWavefront output: U, V (0,1) | NX, NY, NZ (2,3,4) | X, Y, Z (5,6,7)
                # We want: X, Y, Z (5,6,7) | NX, NY, NZ (2,3,4) | U, V (0,1)
                
                corrected = reshaped[:, [5, 6, 7, 2, 3, 4, 0, 1]]
                vertices_flat = corrected.flatten()
            
            # Fallback for models without texture but with normals (N3F_V3F)
            elif 'N3F' in format_str and 'V3F' in format_str:
                count = len(data) // 6
                reshaped = data.reshape((count, 6))
                # Data: NX, NY, NZ, X, Y, Z
                # Want: X, Y, Z, NX, NY, NZ, 0, 0
                
                positions = reshaped[:, 3:6]
                normals = reshaped[:, 0:3]
                uvs = np.zeros((count, 2), dtype=np.float32)
                
                vertices_flat = np.hstack((positions, normals, uvs)).flatten()

            else:
                # If the OBJ has no normals, we should ideally generate them.
                # For now, let's warn and skip or implement a "flat normal" fallback later.
                Logger.warning(f"Skipping material {name}: Format {format_str} not fully supported for lighting (needs Normals).")
                continue

            if len(vertices_flat) > 0:
                model_parts.append({
                    "name": name,
                    "vertices": vertices_flat,
                    "texture_path": texture_path
                })
                
        return model_parts
    except Exception as e:
        Logger.error(f"Loader Error: {e}")
        return []
    