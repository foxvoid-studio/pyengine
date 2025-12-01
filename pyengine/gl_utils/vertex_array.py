import ctypes
from sdl2 import *
from OpenGL.GL import *
from pyengine.gl_utils.vertex_buffer import VertexBuffer

# =============================================================================
# CLASS: VertexArray (VAO)
# Stores the state of how to read data from VBOs (layout, formats, etc.).
# =============================================================================
class VertexArray:
    def __init__(self):
        # Generate 1 Vertex Array Object ID
        self.id = glGenVertexArrays(1)

    def bind(self) -> None:
        """Binds this VAO. All subsequent VBO configs will be stored in this VAO."""
        glBindVertexArray(self.id)

    def unbind(self) -> None:
        """Unbinds the current VAO."""
        glBindVertexArray(0)

    def add_attribute(self, vbo: VertexBuffer, shader_attrib_loc, count, stride=0, offset=0) -> None:
        """
        Configures an attribute (like position or color) for this VAO.
        
        :param vbo: The VertexBuffer containing the data.
        :param shader_attrib_loc: The ID of the attribute in the shader.
        :param count: Number of components per vertex (e.g., 3 for x,y,z).
        :param stride: Byte offset between consecutive attributes (0 = tightly packed).
        :param offset: Offset of the first component in the array.
        """
        self.bind()
        vbo.bind()

        # Define the array of generic vertex attribute data
        glVertexAttribPointer(shader_attrib_loc, count, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
        
        # Enable the generic vertex attribute array
        glEnableVertexAttribArray(shader_attrib_loc)

        # Unbind the VBO and VAO to keep state clean
        vbo.unbind()
        self.unbind()

    def destroy(self) -> None:
        """
        Explicitly delete the VAO.
        """
        if self.id:
            try:
                glDeleteVertexArrays(1, [self.id])
                self.id = None
            except:
                pass
            