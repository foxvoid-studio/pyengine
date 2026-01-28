import os
import numpy as np
import pywavefront
from pyengine.core.logger import Logger

def load_obj_model(file_path: str):
    """
    Loads an OBJ file and robustly standardizes geometry data.
    Returns a list of dictionaries: [{'vertices': np.array, 'texture_path': str|None}, ...]
    
    Output Format guarantees:
    - 8 floats per vertex: Position (3) | Normal (3) | UV (2)
    - Layout: X, Y, Z, NX, NY, NZ, U, V
    """
    if not os.path.exists(file_path):
        Logger.error(f"OBJ File not found: {file_path}")
        return []

    try:
        # Load the OBJ. strict=False allows ignoring unknown tags like 'g'
        scene = pywavefront.Wavefront(file_path, collect_faces=True, create_materials=True, strict=False)
        model_parts = []

        for name, material in scene.materials.items():
            texture_path = None
            if material.texture:
                texture_path = material.texture.path

            # Get raw vertex data and the format string (e.g., "T2F_N3F_V3F")
            raw_data = np.array(material.vertices, dtype=np.float32)
            fmt_str = material.vertex_format
            
            # If the format is empty or data is empty, skip
            if not fmt_str or len(raw_data) == 0:
                continue

            # Parse the format string to find offsets dynamically
            # Example fmt_str: "T2F_N3F_V3F" -> tokens: ["T2F", "N3F", "V3F"]
            tokens = fmt_str.split('_')
            
            # Track where each component starts in the source buffer
            offset = 0
            pos_idx, norm_idx, uv_idx = -1, -1, -1
            stride = 0

            for token in tokens:
                if 'V3F' in token:
                    pos_idx = offset
                    offset += 3
                elif 'N3F' in token:
                    norm_idx = offset
                    offset += 3
                elif 'T2F' in token:
                    uv_idx = offset
                    offset += 2
                else:
                    # Handle other potential formats cleanly (e.g. C3F for color)
                    # We just assume float components based on the digit in the token
                    # This is a heuristic fallback
                    size = int(''.join(filter(str.isdigit, token)) or 0)
                    offset += size
            
            stride = offset
            vertex_count = len(raw_data) // stride
            
            # Reshape raw data into (N, stride) to access columns easily
            reshaped = raw_data.reshape((vertex_count, stride))

            # --- Extract Positions (Mandatory) ---
            if pos_idx != -1:
                positions = reshaped[:, pos_idx : pos_idx + 3]
            else:
                Logger.error(f"Material {name} has no vertices (V3F). Skipping.")
                continue

            # --- Extract Normals (Optional - Default to Up vector 0,1,0 or Zero) ---
            if norm_idx != -1:
                normals = reshaped[:, norm_idx : norm_idx + 3]
            else:
                # Generate dummy normals (0, 0, 0) if missing
                normals = np.zeros((vertex_count, 3), dtype=np.float32)

            # --- Extract UVs (Optional - Default to 0,0) ---
            if uv_idx != -1:
                uvs = reshaped[:, uv_idx : uv_idx + 2]
            else:
                uvs = np.zeros((vertex_count, 2), dtype=np.float32)

            # --- Combine into standardized format: Pos(3), Norm(3), UV(2) ---
            # Order: X, Y, Z, NX, NY, NZ, U, V
            combined = np.hstack((positions, normals, uvs))
            vertices_flat = combined.flatten()

            model_parts.append({
                "name": name,
                "vertices": vertices_flat,
                "texture_path": texture_path
            })
                
        return model_parts

    except Exception as e:
        Logger.error(f"Loader Error: {e}")
        return [] # Return empty list on failure, don't crash
    