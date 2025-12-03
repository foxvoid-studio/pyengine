from pyengine.ecs.component import Component
from pyengine.graphics.material import Material
from typing import Optional


class UIBox(Component):
    """
    Component representing a background panel with rounded corners.
    """
    def __init__(self, width: float, height: float, color: tuple = (0.2, 0.2, 0.2, 0.8), border_radius: float = 10.0):
        """
        :param width: Width in pixels.
        :param height: Height in pixels.
        :param color: RGBA tuple (0.0 to 1.0). Default is dark gray semi-transparent.
        :param border_radius: Radius of the corners in pixels.
        """
        self.width = width
        self.height = height
        self.color = color
        self.border_radius = border_radius
        
        # We need a material to hold the shader
        self.material: Optional[Material] = None
        