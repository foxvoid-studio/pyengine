from pyengine.gl_utils.mesh import Mesh
from pyengine.graphics.material import Material
from typing import Optional, Tuple


class MeshRenderer:
    def __init__(self, mesh: Mesh, material: Material):
        self.mesh = mesh
        self.material = material
        