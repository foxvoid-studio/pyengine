import ctypes
from sdl2 import *
from OpenGL.GL import *
import numpy as np

# =============================================================================
# CLASS: VertexBuffer (VBO)
# Manages raw memory buffers on the GPU (vertices, colors, etc.).
# =============================================================================
class VertexBuffer:
    def __init__(self, data_array: np.ndarray):
        # Generate 1 buffer ID
        self.id = glGenBuffers(1)
        self.bind()

        # Convert numpy array to a C-style void pointer for OpenGL
        data_ptr = data_array.ctypes.data_as(ctypes.c_void_p)
        data_size = data_array.nbytes

        # Upload data to the GPU. 
        # GL_STATIC_DRAW indicates that data will be modified once and used many times.
        glBufferData(GL_ARRAY_BUFFER, data_size, data_ptr, GL_STATIC_DRAW)
        
        # Unbind to prevent accidental modification
        self.unbind()

    def bind(self) -> None:
        """Binds this buffer as the current GL_ARRAY_BUFFER."""
        glBindBuffer(GL_ARRAY_BUFFER, self.id)

    def unbind(self) -> None:
        """Unbinds the current GL_ARRAY_BUFFER."""
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def destroy(self) -> None:
        """
        Explicitly delete the buffer.
        Replaces __del__ to avoid interpreter shutdown race conditions.
        """
        if self.id:
            try:
                glDeleteBuffers(1, [self.id])
                self.id = None
            except:
                pass
            