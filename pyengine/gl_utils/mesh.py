import numpy as np
from OpenGL.GL import *
from pyengine.gl_utils.shader import ShaderProgram
from pyengine.gl_utils.vertex_buffer import VertexBuffer
from pyengine.gl_utils.vertex_array import VertexArray

# =============================================================================
# HIGH-LEVEL ABSTRACTION: MESH
# This class encapsulates the geometry logic.
# =============================================================================
class Mesh:
    def __init__(self, shader: ShaderProgram, vertices: np.ndarray):
        """
        Creates a Mesh object.
        
        :param shader: The ShaderProgram used to determine attribute locations.
        :param vertices: A numpy array of float32 containing vertex positions (x, y, z).
        """
        # Calculate vertex count based on array size (assuming 3 floats per vertex: x, y, z)
        self.count = len(vertices) // 3

        # Create the VBO (Data)
        self.vbo = VertexBuffer(vertices)

        # Create the VAO (Configuration)
        self.vao = VertexArray()

        # Automatically configure the VAO based on the Shader's 'a_position' input
        pos_loc = shader.get_attrib_location("a_position")

        if pos_loc == -1:
            print("Warning: 'a_position' not found in shader. Mesh might not draw correctly.")

        # Link VBO to VAO
        self.vao.add_attribute(self.vbo, pos_loc, count=3)

    def bind(self) -> None:
        self.vao.bind()

    def unbind(self) -> None:
        self.vao.unbind()

    def destroy(self) -> None:
        """
        Clean up VBO and VAO resources.
        """
        self.vao.destroy()
        self.vbo.destroy()


class Triangle(Mesh):
    """
    A specialized Mesh representing a specific Triangle.
    Calculates its own vertices based on position and size.
    """
    def __init__(self, shader: ShaderProgram):
        """
        :param x: X coordinate of the triangle center (from -1.0 to 1.0)
        :param y: Y coordinate of the triangle center (from -1.0 to 1.0)
        :param size: The radius/size of the triangle
        """
        # Calculate vertices relative to the center (x, y)
        # Using numpy float32 directly for performance and OpenGL compatibility
        vertices = np.array([
            -0.5, -0.5, 0.0,  # Bottom Left
             0.5, -0.5, 0.0,  # Bottom Right
             0.0, 0.5, 0.0    # Top Center
        ], dtype=np.float32)

        # Call the parent constructor (Mesh) with the generated data
        super().__init__(shader, vertices)


class Rectangle(Mesh):
    """
    Specialized Mesh representing a Rectangle.
    Constructed using 2 Triangles (6 vertices).
    """
    def __init__(self, shader: ShaderProgram):
        """
        :param x: Center X
        :param y: Center Y
        :param width: Total width
        :param height: Total height
        """
        # We define 2 triangles to make a rectangle (quads are deprecated in modern core GL)
        # Triangle 1: Bottom-Left, Bottom-Right, Top-Left
        # Triangle 2: Bottom-Right, Top-Right, Top-Left
        vertices = np.array([
            # First Triangle
            -0.5, -0.5, 0.0,  # Bottom Left  
             0.5, -0.5, 0.0,  # Bottom Right
            -0.5, 0.5, 0.0,   # Top Left

            # Second Triangle
             0.5, -0.5, 0.0,  # Bottom Right
             0.5,  0.5, 0.0,  # Top Right
            -0.5, 0.5, 0.0    # Top Left
        ], dtype=np.float32)

        super().__init__(shader, vertices)
