import glm
from pyengine.ecs.component import Component


class DirectionalLight(Component):
    """
    Simulates a sun-like light source (infinite distance).
    The position doesn't matter, only the direction.
    """
    def __init__(self, color=(1.0, 1.0, 1.0), intensity=1.0, direction=(0.5, -1.0, 0.5)):
        self.color = glm.vec3(color)
        self.intensity = intensity
        self.direction = glm.normalize(glm.vec3(direction))


class PointLight:
    """
    Simulates a light bulb or fire.
    Position is taken from the Entity's Transform component.
    """
    def __init__(self, color=(1.0, 1.0, 1.0), intensity=1.0, radius=10.0):
        self.color = glm.vec3(color)
        self.intensity = intensity
        
        # Attenuation constants based on radius (simplified)
        # Using standard Ogre3D/GL values for nice falloff
        self.constant = 1.0
        self.linear = 0.09
        self.quadratic = 0.032
        