import glm
from pyengine.physics.transform import Transform
from pyengine.ecs.component import Component


class MainCamera(Component):
    """
    Tag component to identify the primary active camera in the scene.
    """
    pass


class Camera2D(Component):
    def __init__(self, width: int, height: int, ortho_size: float = 5.0):
        # Zoom level (1.0 = Default, 2.0 = Zoomed In, 0.5 = Zoomed Out)
        self.zoom = 1.0
        
        # Screen dimensions to calculate aspect ratio
        self.width = width
        self.height = height
        
        # This defines how many "World Units" fit vertically in the screen.
        # e.g., if set to 10.0, the screen will show 10 units from bottom to top.
        self.ortho_size = ortho_size

    def resize(self, width: int, height: int) -> None:
        """
        Updates the camera dimensions when the window is resized.
        """
        self.width = width
        self.height = height

    def get_view_matrix(self, transform: Transform) -> glm.mat4:
        """
        Calculates view matrix based on the Entity's Transform.
        NOTE: The view matrix is the INVERSE of the camera's transform.
        """
        view = glm.mat4(1.0)
        
        # 1. Inverse Rotation
        view = glm.rotate(view, -transform.rotation.z, glm.vec3(0, 0, 1))
        
        # 2. Inverse Translation (Move the world opposite to the camera)
        view = glm.translate(view, glm.vec3(-transform.position.x, -transform.position.y, 0.0))
        
        return view

    def get_projection_matrix(self) -> glm.mat4:
        """
        Calculates projection based on internal dimensions and zoom.
        """
        aspect_ratio = self.width / self.height
        vertical_size = self.ortho_size / self.zoom
        horizontal_size = vertical_size * aspect_ratio
        
        left = -horizontal_size / 2.0
        right = horizontal_size / 2.0
        bottom = -vertical_size / 2.0
        top = vertical_size / 2.0
        
        return glm.ortho(left, right, bottom, top, -1.0, 100.0)
    