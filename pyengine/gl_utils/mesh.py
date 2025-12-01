import math
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


class Cube(Mesh):
    """
    Specialized Mesh representing a 3D Cube.
    Contains 36 vertices (6 faces * 2 triangles * 3 vertices).
    """
    def __init__(self, shader: ShaderProgram):
        # Format: x, y, z, u, v
        vertices = np.array([
            # Back face
            -0.5, -0.5, -0.5,  0.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 1.0,
             0.5,  0.5, -0.5,  1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 0.0,

            # Front face
            -0.5, -0.5,  0.5,  0.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 1.0,
             0.5,  0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,

            # Left face
            -0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5, -0.5,  1.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,
            -0.5,  0.5,  0.5,  1.0, 0.0,

            # Right face
             0.5,  0.5,  0.5,  1.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 1.0,
             0.5, -0.5, -0.5,  0.0, 1.0,
             0.5, -0.5, -0.5,  0.0, 1.0,
             0.5, -0.5,  0.5,  0.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 0.0,

            # Bottom face
            -0.5, -0.5, -0.5,  0.0, 1.0,
             0.5, -0.5, -0.5,  1.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,

            # Top face
            -0.5,  0.5, -0.5,  0.0, 1.0,
             0.5,  0.5, -0.5,  1.0, 1.0,
             0.5,  0.5,  0.5,  1.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 0.0,
            -0.5,  0.5, -0.5,  0.0, 1.0
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Plane(Mesh):
    """
    A flat plane on the XZ axis (Ground).
    Useful for floors.
    """
    def __init__(self, shader: ShaderProgram, width: float = 10.0, depth: float = 10.0, tile_u: float = 1.0, tile_v: float = 1.0):
        w = width / 2.0
        d = depth / 2.0
        
        # Vertices (X, Y, Z, U, V)
        # Y is 0.0 because it's a ground plane
        vertices = np.array([
            # First Triangle
            -w, 0.0,  d,  0.0,    0.0,
             w, 0.0,  d,  tile_u, 0.0,
            -w, 0.0, -d,  0.0,    tile_v,

            # Second Triangle
             w, 0.0,  d,  tile_u, 0.0,
             w, 0.0, -d,  tile_u, tile_v,
            -w, 0.0, -d,  0.0,    tile_v
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Sphere(Mesh):
    """
    A procedural Sphere generated using spherical coordinates.
    """
    def __init__(self, shader: ShaderProgram, radius: float = 0.5, sectors: int = 36, stacks: int = 18):
        vertices = []
        
        # Helper to get position on sphere surface
        def get_pos(stack_idx, sector_idx):
            # Math logic:
            # stack angle goes from -pi/2 to pi/2 (bottom to top)
            # sector angle goes from 0 to 2pi (around the circle)
            stack_angle = math.pi / 2 - stack_idx * math.pi / stacks
            sector_angle = sector_idx * 2 * math.pi / sectors
            
            x = radius * math.cos(stack_angle) * math.cos(sector_angle)
            y = radius * math.sin(stack_angle)
            z = radius * math.cos(stack_angle) * math.sin(sector_angle)
            
            u = sector_idx / sectors
            v = stack_idx / stacks
            return x, y, z, u, v

        # Generate triangles
        for i in range(stacks):
            for j in range(sectors):
                # 4 corners of the current sector "quad"
                # P1 -- P2
                # |      |
                # P3 -- P4
                
                x1, y1, z1, u1, v1 = get_pos(i, j)          # Top Left
                x2, y2, z2, u2, v2 = get_pos(i, j+1)        # Top Right
                x3, y3, z3, u3, v3 = get_pos(i+1, j)        # Bottom Left
                x4, y4, z4, u4, v4 = get_pos(i+1, j+1)      # Bottom Right
                
                # Triangle 1 (Top Left, Top Right, Bottom Left)
                vertices.extend([x1, y1, z1, u1, v1])
                vertices.extend([x2, y2, z2, u2, v2])
                vertices.extend([x3, y3, z3, u3, v3])
                
                # Triangle 2 (Top Right, Bottom Right, Bottom Left)
                vertices.extend([x2, y2, z2, u2, v2])
                vertices.extend([x4, y4, z4, u4, v4])
                vertices.extend([x3, y3, z3, u3, v3])

        super().__init__(shader, np.array(vertices, dtype=np.float32))


class Cylinder(Mesh):
    """
    A procedural Cylinder with top and bottom caps.
    """
    def __init__(self, shader: ShaderProgram, radius: float = 0.5, height: float = 1.0, segments: int = 32):
        vertices = []
        half_h = height / 2.0
        
        for i in range(segments):
            # Calculate angles
            theta = 2.0 * math.pi * i / segments
            next_theta = 2.0 * math.pi * (i + 1) / segments
            
            # Precompute sin/cos for current and next segment
            c, s = math.cos(theta), math.sin(theta)
            nc, ns = math.cos(next_theta), math.sin(next_theta)
            
            # --- SIDE WALLS ---
            # UV mapping wraps around the cylinder
            u = i / segments
            nu = (i + 1) / segments
            
            # Top-Left, Top-Right, Bot-Left, Bot-Right logic
            p1 = (radius * c,  half_h, radius * s,  u, 1.0)
            p2 = (radius * nc, half_h, radius * ns, nu, 1.0)
            p3 = (radius * c, -half_h, radius * s,  u, 0.0)
            p4 = (radius * nc,-half_h, radius * ns, nu, 0.0)
            
            # Add two triangles for the side face
            vertices.extend(p1 + p2 + p3)
            vertices.extend(p2 + p4 + p3)
            
            # --- TOP CAP ---
            # Center point, Current Rim, Next Rim
            # UVs for caps are mapped like a circle in a square
            
            # Center Top
            tc = (0.0, half_h, 0.0, 0.5, 0.5) 
            # Rim points with UVs adjusted to be centered
            tr1 = (radius * c,  half_h, radius * s,  0.5 + 0.5*c, 0.5 + 0.5*s)
            tr2 = (radius * nc, half_h, radius * ns, 0.5 + 0.5*nc, 0.5 + 0.5*ns)
            
            vertices.extend(tc + tr2 + tr1) # Winding order matters!
            
            # --- BOTTOM CAP ---
            bc = (0.0, -half_h, 0.0, 0.5, 0.5)
            br1 = (radius * c,  -half_h, radius * s,  0.5 + 0.5*c, 0.5 + 0.5*s)
            br2 = (radius * nc, -half_h, radius * ns, 0.5 + 0.5*nc, 0.5 + 0.5*ns)
            
            vertices.extend(bc + br1 + br2)

        super().__init__(shader, np.array(vertices, dtype=np.float32))