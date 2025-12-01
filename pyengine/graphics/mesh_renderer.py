from pyengine.gl_utils.mesh import Mesh
from pyengine.gl_utils.shader import ShaderProgram

class MeshRenderer:
    def __init__(self, mesh: Mesh, shader: ShaderProgram):
        self.mesh = mesh
        self.shader = shader
