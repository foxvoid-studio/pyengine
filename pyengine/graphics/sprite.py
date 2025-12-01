from pyengine.ecs.component import Component
from typing import Dict, List, Tuple


class SpriteSheet(Component):
    """
    Defines the grid layout of a texture (rows and columns).
    Used to calculate UV offsets for a specific frame index.
    """
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        
        # Calculate the size of one cell in UV space (0.0 to 1.0)
        self.u_scale = 1.0 / cols
        self.v_scale = 1.0 / rows
        
        # Current frame index to display
        self.current_frame = 0

    def get_uv_transform(self) -> Tuple[float, float, float, float]:
        """
        Calculates the Scale and Offset for the current frame.
        Returns: (scale_x, scale_y, offset_x, offset_y)
        """
        # Calculate grid position (0-indexed)
        col = self.current_frame % self.cols
        row = self.current_frame // self.cols
        
        # Calculate offsets
        # X offset is simple: column * width of cell
        u_offset = col * self.u_scale
        
        # Y offset depends on coordinate system. 
        # In OpenGL, (0,0) is Bottom-Left. Sprite sheets are usually Top-Left.
        # We invert the row index to match OpenGL's coordinate system.
        v_offset = (self.rows - 1 - row) * self.v_scale
        
        return (self.u_scale, self.v_scale, u_offset, v_offset)
    

class Animation:
    def __init__(self, start_frame: int, end_frame: int, frame_duration_in_seconds: float = 0.1):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_duration_in_seconds = frame_duration_in_seconds


class Animator(Component):
    """
    Manages animation states (Start frame, End frame, Speed).
    """
    def __init__(self):
        self.animations: Dict[str, Animation] = {}

        self.current_anim_name = None
        self.timer = 0.0
        self.frame_duration = 0.1
        self.loop = True
        self.is_playing = False

    def add(self, name: str, animation: Animation):
        """Register a new animation sequence."""
        self.animations[name] = animation

    def play(self, name: str, loop: bool = True):
        """Starts playing an animation."""
        if name not in self.animations:
            return
            
        if self.current_anim_name != name:
            self.current_anim_name = name
            self.frame_duration = self.animations[name].frame_duration_in_seconds
            self.timer = 0.0
            self.loop = loop
            self.is_playing = True
