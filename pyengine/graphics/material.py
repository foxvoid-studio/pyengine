from typing import Optional, Tuple
from pyengine.gl_utils.shader import ShaderProgram
from pyengine.gl_utils.texture import Texture


class Material:
    def __init__(self, shader: ShaderProgram, texture: Optional[Texture] = None, color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)):
        self.shader = shader
        self.texture = texture
        self.color = color
        