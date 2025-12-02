from sdl2 import *
from pyengine.gui.font import Font
from pyengine.ecs.component import Component


class TextRenderer(Component):
    """
    Component to render 2D text.
    """
    def __init__(self, font: Font, text: str = "Text", color=(255, 255, 255)):
        self.font = font
        self.color = color
        self._text = text
        self.texture = None
        self.is_dirty = True # Flag to update texture only when text changes
        
        # We need a mesh to draw the text quad
        # Ideally, we reuse a global Rectangle mesh, but for now let's keep it simple.
        # We will assign the mesh later or assume the RenderSystem has a default quad.
        self.mesh = None 
        self.material = None

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self.is_dirty = True
