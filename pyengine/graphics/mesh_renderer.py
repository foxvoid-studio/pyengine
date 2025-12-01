from pyengine.gl_utils.mesh import Mesh
from pyengine.graphics.material import Material
from pyengine.ecs.component import Component


class MeshRenderer(Component):
    def __init__(self, mesh: Mesh, material: Material):
        self.mesh = mesh
        self.material = material
