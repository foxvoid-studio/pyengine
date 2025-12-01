import glm
from pyengine.ecs.component import Component

class Transform(Component):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        # glm.vec3 is powerful: supports + - * /, cross product, etc.
        self.position = glm.vec3(position)
        self.rotation = glm.vec3(rotation) # Euler angles (radians)
        self.scale = glm.vec3(scale)
        