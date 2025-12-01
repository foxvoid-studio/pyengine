import os
import numpy as np
import pywavefront
from pyengine.core.logger import Logger


def load_obj_file(file_path: str) -> np.ndarray:
    """
    Loads an OBJ file using PyWavefront library.
    Returns a flat numpy array of vertices suitable for glDrawArrays.
    Format depends on the file, but we request T2F_V3F (Texture 2 floats, Position 3 floats).
    """
    if not os.path.exists(file_path):
        Logger.error(f"OBJ File not found: {file_path}")
        return np.array([], dtype=np.float32)
    
    try:
        # Load the scene.
        # strict=True raises errors for bad parsing
        # encoding='iso-8859-1' is often safer for OBJs than utf-8
        scene = pywavefront.Wavefront(
            file_path, 
            collect_faces=True, 
            create_materials=True,
            strict=False 
        )
        
        all_vertices = []

        # PyWavefront groups geometry by Material. 
        # We need to iterate over materials to get all parts of the mesh.
        for name, material in scene.materials.items():
            
            # This is the magic part: visualization.format_material forces the data
            # into a format OpenGL understands directly.
            # 'T2F_V3F' means: Texture (2 floats) then Vertex (3 floats) -> [u, v, x, y, z]
            # WAIT: Your engine expects [x, y, z, u, v].
            # PyWavefront usually outputs T2F_V3F (u, v, x, y, z) or C3F_V3F.
            
            # Let's get the raw format and verify. 
            # PyWavefront's default interleaved format is usually T2F_V3F.
            
            # We enforce a specific format using this helper:
            # This aligns the vertices to be compatible with standard GL pipelines.
            # format_material returns indices too, but since you use glDrawArrays, 
            # we might just want the raw flattened vertex data (unindexed).
            
            # However, simpler approach for your specific Mesh class:
            # Accessing material.vertices gives a flat list of floats.
            # The format is defined in material.vertex_format.
            
            # Check format
            format_str = material.vertex_format
            data = material.vertices
            
            # PyWavefront is a bit tricky: it often outputs [u, v, x, y, z].
            # Your engine wants [x, y, z, u, v].
            # We need to detect and swap if necessary, or change your Mesh class stride.
            
            # Let's convert to numpy to manipulate easily
            data_np = np.array(data, dtype=np.float32)
            
            if format_str == 'T2F_V3F':
                # Data is: u, v, x, y, z, u, v, x, y, z...
                # Reshape to (N, 5)
                count = len(data_np) // 5
                reshaped = data_np.reshape((count, 5))
                
                # Swap columns to get [x, y, z, u, v]
                # Current: 0=u, 1=v, 2=x, 3=y, 4=z
                # Target:  x, y, z, u, v
                
                # Create a new array with correct order
                # columns: 2,3,4 (xyz) then 0,1 (uv)
                corrected = reshaped[:, [2, 3, 4, 0, 1]]
                
                all_vertices.extend(corrected.flatten())
                
            elif format_str == 'V3F':
                # Just position, no texture. 
                # We need to pad with dummy UVs [x, y, z, 0, 0]
                count = len(data_np) // 3
                reshaped = data_np.reshape((count, 3))
                
                # Add two columns of zeros
                zeros = np.zeros((count, 2), dtype=np.float32)
                combined = np.hstack((reshaped, zeros))
                
                all_vertices.extend(combined.flatten())
                
            else:
                # Fallback or other formats (N3F_V3F etc)
                # For now, let's assume standard textured OBJ
                Logger.warning(f"Unknown vertex format from PyWavefront: {format_str}")
                pass

        Logger.info(f"Loaded OBJ (PyWavefront): {file_path} - Vertices: {len(all_vertices)//5}")
        return np.array(all_vertices, dtype=np.float32)

    except Exception as e:
        Logger.error(f"Failed to load OBJ {file_path}: {e}")
        return np.array([], dtype=np.float32)
    