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
    

class Camera3D(Component):
    """
    A 3D Camera component using Perspective Projection.
    Follows Euler angles (Yaw/Pitch) for rotation.
    """
    def __init__(self, width: int, height: int, fov: float = 45.0):
        self.width = width
        self.height = height
        self.fov = fov # Field of View in degrees
        
        # Orientation vectors
        # Front is initialized pointing towards negative Z (into the screen)
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)

        # Euler Angles (in degrees)
        self.yaw = -90.0
        self.pitch = 0.0
        
        self._update_vectors()

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def process_mouse_movement(self, x_offset: float, y_offset: float, sensitivity: float = 0.1):
        """
        Updates Yaw and Pitch based on mouse movement delta.
        """
        self.yaw += x_offset * sensitivity
        self.pitch += y_offset * sensitivity

        # Constrain pitch so screen doesn't flip
        if self.pitch > 89.0: self.pitch = 89.0
        if self.pitch < -89.0: self.pitch = -89.0

        self._update_vectors()

    def _update_vectors(self):
        """
        Calculates the new Front, Right, and Up vectors based on Yaw/Pitch.
        """
        # Calculate the new Front vector using trigonometry
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        
        self.front = glm.normalize(front)
        
        # Recalculate Right and Up vectors
        # Normalize the vectors, because their length gets closer to 0 
        # the more you look up or down which results in slower movement.
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def get_projection_matrix(self) -> glm.mat4:
        """
        Returns Perspective Matrix.
        """
        aspect_ratio = self.width / self.height
        return glm.perspective(glm.radians(self.fov), aspect_ratio, 0.1, 100.0)

    def get_view_matrix(self, transform: Transform) -> glm.mat4:
        """
        Returns View Matrix using glm.lookAt.
        """
        # position, target, up
        return glm.lookAt(transform.position, transform.position + self.front, self.up)
