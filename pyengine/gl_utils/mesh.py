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
        # We assume vertices are [x, y, z, u, v] -> 5 floats per vertex
        self.count = len(vertices) // 5

        # Create the VBO (Data)
        self.vbo = VertexBuffer(vertices)

        # Create the VAO (Configuration)
        self.vao = VertexArray()

        # Calculate stride: 5 floats * 4 bytes/float = 20 bytes
        stride = 5 * 4 

        # Position attribute (3 floats, offset 0)
        pos_loc = shader.get_attrib_location("a_position")
        if pos_loc != -1:
            self.vao.add_attribute(self.vbo, pos_loc, 3, stride, 0)
            
        # Texture Coordinate attribute (2 floats, offset 3 * 4 = 12 bytes)
        tex_loc = shader.get_attrib_location("a_texcoord")
        if tex_loc != -1:
            self.vao.add_attribute(self.vbo, tex_loc, 2, stride, 12)

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
            -0.5, -0.5, 0.0,   0.0, 0.0,  # Bottom Left
             0.5, -0.5, 0.0,   1.0, 0.0,  # Bottom Right
             0.0, 0.5, 0.0,    0.5, 1.0   # Top Center
        ], dtype=np.float32)

        # Call the parent constructor (Mesh) with the generated data
        super().__init__(shader, vertices)


class Rectangle(Mesh):
    """
    Specialized Mesh representing a Rectangle.
    Constructed using 2 Triangles (6 vertices).
    """
    def __init__(self, shader: ShaderProgram):
        # We define 2 triangles to make a rectangle (quads are deprecated in modern core GL)
        # Triangle 1: Bottom-Left, Bottom-Right, Top-Left
        # Triangle 2: Bottom-Right, Top-Right, Top-Left
        vertices = np.array([
            # First Triangle
            -0.5, -0.5, 0.0,   0.0, 0.0,  # Bottom Left  
             0.5, -0.5, 0.0,   1.0, 0.0,  # Bottom Right
            -0.5, 0.5, 0.0,    0.0, 1.0,  # Top Left

            # Second Triangle
             0.5, -0.5, 0.0,   1.0, 0.0,  # Bottom Right
             0.5,  0.5, 0.0,   1.0, 1.0,  # Top Right
            -0.5, 0.5, 0.0,    0.0, 1.0  # Top Left
        ], dtype=np.float32)

        super().__init__(shader, vertices)
