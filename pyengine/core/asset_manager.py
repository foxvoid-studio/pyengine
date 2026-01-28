import os
from typing import Dict, List, Tuple
from pyengine.core.logger import Logger
from pyengine.gl_utils.texture import Texture
from pyengine.gl_utils.shader import ShaderProgram
from pyengine.gl_utils.mesh import Mesh
from pyengine.gl_utils.obj_loader import load_obj_model
from pyengine.graphics.material import Material
from pyengine.gui.font import Font


class AssetManager:
    """
    Centralized manager to load and store assets.
    Prevents loading the same asset multiple times (Caching).
    """
    def __init__(self):
        # Cache for textures: Path -> Texture Object
        self._textures: Dict[str, Texture] = {}
        
        # Cache for shaders: (VertPath, FragPath) -> Shader Object
        self._shaders: Dict[Tuple[str, str], ShaderProgram] = {}

        # Cache for Mesh Data
        # Key: file_path, Value: Mesh Object
        self._meshes: Dict[str, Mesh] = {}

        # Cache for fonts
        self._fonts: Dict[Tuple[str, int], Font] = {}

    def get_texture(self, path: str) -> Texture:
        """
        Returns a Texture. Loads it from disk if not already cached.
        """
        if path not in self._textures:
            Logger.info(f"[ResourceManager] Loading new texture: {path}")
            self._textures[path] = Texture(path)
        
        return self._textures[path]
    
    def get_shader(self, vert_path: str, frag_path: str) -> ShaderProgram:
        """
        Returns a ShaderProgram. Loads it if not already cached.
        The key is a tuple of both file paths.
        """
        key = (vert_path, frag_path)
        
        if key not in self._shaders:
            Logger.info(f"[ResourceManager] Loading new shader: {vert_path} | {frag_path}")
            self._shaders[key] = ShaderProgram.from_files(vert_path, frag_path)
            
        return self._shaders[key]
    
    def load_model(self, obj_path: str, shader: ShaderProgram) -> List[Tuple[Mesh, Material]]:
        """
        Loads a complex model (OBJ + MTL).
        Returns a list of tuples: (Mesh, Material)
        You should create one Entity per tuple.
        """
        parts = load_obj_model(obj_path)
        results = []
        
        # Determine the base directory of the OBJ file
        # If obj is "assets/models/car.obj", base_dir is "assets/models/"
        base_dir = os.path.dirname(obj_path)

        for part in parts:
            # 1. Create Mesh
            mesh = Mesh(shader, part['vertices'])
            
            # 2. Determine Material
            texture = None
            tex_path_raw = part['texture_path']
            
            if tex_path_raw:
                # Construct full path: assets/models/ + wood.png
                file_name = os.path.basename(tex_path_raw)
                full_tex_path = os.path.join(base_dir, file_name)
                
                # Load texture (Cached automatically by get_texture)
                texture = self.get_texture(full_tex_path)
            
            # Create Material
            # If no texture found, it will be white (default color)
            material = Material(shader, texture=texture)
            
            results.append((mesh, material))
            
        return results
    
    def get_mesh(self, path: str, shader: ShaderProgram) -> Mesh:
        """
        Loads an OBJ file into a Mesh object.
        """
        if path not in self._meshes:
            Logger.debug(f"Loading mesh from disk: {path}")
            
            # 1. Parse Data
            vertices = load_obj_model(path)
            
            # 2. Create Mesh Object
            # We use the base Mesh class since it takes raw vertices
            mesh = Mesh(shader, vertices)
            
            self._meshes[path] = mesh
        
        return self._meshes[path]
    
    def get_font(self, path: str, size: int) -> Font:
        key = (path, size)
        if key not in self._fonts:
            self._fonts[key] = Font(path, size)
        return self._fonts[key]
    
    def clear(self) -> None:
        """
        Destroys all stored OpenGL resources.
        Call this before shutting down the application.
        """
        for texture in self._textures.values():
            texture.destroy()
        self._textures.clear()

        for shader in self._shaders.values():
            shader.destroy()
        self._shaders.clear()

        # Clear meshes
        for mesh in self._meshes.values():
            mesh.destroy()
        self._meshes.clear()
        
        Logger.info("[ResourceManager] All resources cleared.")
        