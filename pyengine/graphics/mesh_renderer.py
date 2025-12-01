from pyengine.gl_utils.mesh import Mesh
from pyengine.gl_utils.shader import ShaderProgram
from pyengine.gl_utils.texture import Texture
from typing import Optional

class MeshRenderer:
    def __init__(self, mesh: Mesh, shader: ShaderProgram, texture: Optional[Texture] = None):
        self.mesh = mesh
        self.shader = shader
        self.texture = texture
