from typing import Dict, Tuple
from pyengine.core.logger import Logger
from pyengine.gl_utils.texture import Texture
from pyengine.gl_utils.shader import ShaderProgram


class ResourceManager:
    """
    Centralized manager to load and store assets.
    Prevents loading the same asset multiple times (Caching).
    """
    def __init__(self):
        # Cache for textures: Path -> Texture Object
        self._textures: Dict[str, Texture] = {}
        
        # Cache for shaders: (VertPath, FragPath) -> Shader Object
        self._shaders: Dict[Tuple[str, str], ShaderProgram] = {}

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
        
        Logger.info("[ResourceManager] All resources cleared.")
        