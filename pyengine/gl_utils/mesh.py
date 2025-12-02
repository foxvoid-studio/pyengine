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
        :param vertices: A numpy array of float32 containing vertex data.
                         Format: [x, y, z, nx, ny, nz, u, v] (8 floats)
        """
        self.count = len(vertices) // 8

        # Create the VBO (Data)
        self.vbo = VertexBuffer(vertices)

        # Create the VAO (Configuration)
        self.vao = VertexArray()

        # Calculate stride: 8 floats * 4 bytes/float = 32 bytes
        stride = 8 * 4 

        # 1. Position (Offset 0)
        pos_loc = shader.get_attrib_location("a_position")
        if pos_loc != -1:
            self.vao.add_attribute(self.vbo, pos_loc, 3, stride, 0)

        # 2. Normal (Offset 3 floats * 4 = 12 bytes)
        norm_loc = shader.get_attrib_location("a_normal")
        if norm_loc != -1:
            self.vao.add_attribute(self.vbo, norm_loc, 3, stride, 12)
            
        # 3. TexCoord (Offset 6 floats * 4 = 24 bytes)
        tex_loc = shader.get_attrib_location("a_texcoord")
        if tex_loc != -1:
            self.vao.add_attribute(self.vbo, tex_loc, 2, stride, 24)

    def bind(self) -> None:
        self.vao.bind()

    def unbind(self) -> None:
        self.vao.unbind()

    def destroy(self) -> None:
        self.vao.destroy()
        self.vbo.destroy()


class Triangle(Mesh):
    def __init__(self, shader: ShaderProgram):
        # Normal points towards +Z (0, 0, 1)
        vertices = np.array([
            -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,  # Bottom Left
             0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   1.0, 0.0,  # Bottom Right
             0.0,  0.5, 0.0,   0.0, 0.0, 1.0,   0.5, 1.0   # Top Center
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Rectangle(Mesh):
    def __init__(self, shader: ShaderProgram):
        # Normal points towards +Z (0, 0, 1)
        vertices = np.array([
            # First Triangle
            -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,
             0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   1.0, 0.0,
            -0.5,  0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 1.0,

            # Second Triangle
             0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   1.0, 0.0,
             0.5,  0.5, 0.0,   0.0, 0.0, 1.0,   1.0, 1.0,
            -0.5,  0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 1.0
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Cube(Mesh):
    def __init__(self, shader: ShaderProgram):
        vertices = np.array([
            # Back face (Normal: 0, 0, -1)
            -0.5, -0.5, -0.5,  0.0, 0.0, -1.0,  0.0, 0.0,
             0.5, -0.5, -0.5,  0.0, 0.0, -1.0,  1.0, 0.0,
             0.5,  0.5, -0.5,  0.0, 0.0, -1.0,  1.0, 1.0,
             0.5,  0.5, -0.5,  0.0, 0.0, -1.0,  1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 0.0, -1.0,  0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 0.0, -1.0,  0.0, 0.0,

            # Front face (Normal: 0, 0, 1)
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,   0.0, 0.0,
             0.5, -0.5,  0.5,  0.0, 0.0, 1.0,   1.0, 0.0,
             0.5,  0.5,  0.5,  0.0, 0.0, 1.0,   1.0, 1.0,
             0.5,  0.5,  0.5,  0.0, 0.0, 1.0,   1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,   0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,   0.0, 0.0,

            # Left face (Normal: -1, 0, 0)
            -0.5,  0.5,  0.5, -1.0, 0.0, 0.0,   1.0, 0.0,
            -0.5,  0.5, -0.5, -1.0, 0.0, 0.0,   1.0, 1.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0,   0.0, 1.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0,   0.0, 1.0,
            -0.5, -0.5,  0.5, -1.0, 0.0, 0.0,   0.0, 0.0,
            -0.5,  0.5,  0.5, -1.0, 0.0, 0.0,   1.0, 0.0,

            # Right face (Normal: 1, 0, 0)
             0.5,  0.5,  0.5,  1.0, 0.0, 0.0,   1.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 0.0, 0.0,   1.0, 1.0,
             0.5, -0.5, -0.5,  1.0, 0.0, 0.0,   0.0, 1.0,
             0.5, -0.5, -0.5,  1.0, 0.0, 0.0,   0.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 0.0, 0.0,   0.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 0.0, 0.0,   1.0, 0.0,

            # Bottom face (Normal: 0, -1, 0)
            -0.5, -0.5, -0.5,  0.0, -1.0, 0.0,  0.0, 1.0,
             0.5, -0.5, -0.5,  0.0, -1.0, 0.0,  1.0, 1.0,
             0.5, -0.5,  0.5,  0.0, -1.0, 0.0,  1.0, 0.0,
             0.5, -0.5,  0.5,  0.0, -1.0, 0.0,  1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0, 0.0,  0.0, 0.0,
            -0.5, -0.5, -0.5,  0.0, -1.0, 0.0,  0.0, 1.0,

            # Top face (Normal: 0, 1, 0)
            -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,   0.0, 1.0,
             0.5,  0.5, -0.5,  0.0, 1.0, 0.0,   1.0, 1.0,
             0.5,  0.5,  0.5,  0.0, 1.0, 0.0,   1.0, 0.0,
             0.5,  0.5,  0.5,  0.0, 1.0, 0.0,   1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 1.0, 0.0,   0.0, 0.0,
            -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,   0.0, 1.0
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Plane(Mesh):
    """
    A flat plane on the XZ axis (Ground).
    Normal points UP (0, 1, 0).
    """
    def __init__(self, shader: ShaderProgram, width: float = 10.0, depth: float = 10.0, tile_u: float = 1.0, tile_v: float = 1.0):
        w = width / 2.0
        d = depth / 2.0
        
        # Vertices (X, Y, Z, NX, NY, NZ, U, V)
        vertices = np.array([
            # First Triangle
            -w, 0.0,  d,   0.0, 1.0, 0.0,   0.0,    0.0,
             w, 0.0,  d,   0.0, 1.0, 0.0,   tile_u, 0.0,
            -w, 0.0, -d,   0.0, 1.0, 0.0,   0.0,    tile_v,

            # Second Triangle
             w, 0.0,  d,   0.0, 1.0, 0.0,   tile_u, 0.0,
             w, 0.0, -d,   0.0, 1.0, 0.0,   tile_u, tile_v,
            -w, 0.0, -d,   0.0, 1.0, 0.0,   0.0,    tile_v
        ], dtype=np.float32)

        super().__init__(shader, vertices)


class Sphere(Mesh):
    def __init__(self, shader: ShaderProgram, radius: float = 0.5, sectors: int = 36, stacks: int = 18):
        vertices = []
        
        def get_data(stack_idx, sector_idx):
            stack_angle = math.pi / 2 - stack_idx * math.pi / stacks
            sector_angle = sector_idx * 2 * math.pi / sectors
            
            # Position
            x = radius * math.cos(stack_angle) * math.cos(sector_angle)
            y = radius * math.sin(stack_angle)
            z = radius * math.cos(stack_angle) * math.sin(sector_angle)
            
            # Normal (Normalized position for a sphere at origin)
            nx = x / radius
            ny = y / radius
            nz = z / radius
            
            # UV
            u = sector_idx / sectors
            v = stack_idx / stacks
            
            return x, y, z, nx, ny, nz, u, v

        for i in range(stacks):
            for j in range(sectors):
                # Quad corners
                d1 = get_data(i, j)         # TL
                d2 = get_data(i, j+1)       # TR
                d3 = get_data(i+1, j)       # BL
                d4 = get_data(i+1, j+1)     # BR
                
                # Triangle 1
                vertices.extend(d1 + d2 + d3)
                # Triangle 2
                vertices.extend(d2 + d4 + d3)

        super().__init__(shader, np.array(vertices, dtype=np.float32))


class Cylinder(Mesh):
    def __init__(self, shader: ShaderProgram, radius: float = 0.5, height: float = 1.0, segments: int = 32):
        vertices = []
        half_h = height / 2.0
        
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            next_theta = 2.0 * math.pi * (i + 1) / segments
            
            c, s = math.cos(theta), math.sin(theta)
            nc, ns = math.cos(next_theta), math.sin(next_theta)
            
            u = i / segments
            nu = (i + 1) / segments
            
            # --- SIDE WALLS ---
            # Normals for side point horizontally outwards (c, 0, s)
            
            # Top-Left (x, y, z, nx, ny, nz, u, v)
            p1 = (radius * c,  half_h, radius * s,   c, 0.0, s,   u, 1.0)
            # Top-Right
            p2 = (radius * nc, half_h, radius * ns,  nc, 0.0, ns, nu, 1.0)
            # Bot-Left
            p3 = (radius * c, -half_h, radius * s,   c, 0.0, s,   u, 0.0)
            # Bot-Right
            p4 = (radius * nc,-half_h, radius * ns,  nc, 0.0, ns, nu, 0.0)
            
            vertices.extend(p1 + p2 + p3)
            vertices.extend(p2 + p4 + p3)
            
            # --- TOP CAP ---
            # Normal: (0, 1, 0)
            tc = (0.0, half_h, 0.0,             0.0, 1.0, 0.0,  0.5, 0.5) 
            tr1 = (radius * c,  half_h, radius * s,  0.0, 1.0, 0.0,  0.5 + 0.5*c, 0.5 + 0.5*s)
            tr2 = (radius * nc, half_h, radius * ns, 0.0, 1.0, 0.0,  0.5 + 0.5*nc, 0.5 + 0.5*ns)
            vertices.extend(tc + tr2 + tr1)
            
            # --- BOTTOM CAP ---
            # Normal: (0, -1, 0)
            bc = (0.0, -half_h, 0.0,              0.0, -1.0, 0.0,  0.5, 0.5)
            br1 = (radius * c,  -half_h, radius * s,  0.0, -1.0, 0.0,  0.5 + 0.5*c, 0.5 + 0.5*s)
            br2 = (radius * nc, -half_h, radius * ns, 0.0, -1.0, 0.0,  0.5 + 0.5*nc, 0.5 + 0.5*ns)
            vertices.extend(bc + br1 + br2)

        super().__init__(shader, np.array(vertices, dtype=np.float32))
        