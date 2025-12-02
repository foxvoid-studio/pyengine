import sys
import ctypes
from OpenGL.GL import *
from PIL import Image
from pyengine.core.logger import Logger
from typing import Optional


class Texture:
    def __init__(self, filepath: Optional[str] = None):
        # Generate a unique OpenGL texture identifier
        self.id = glGenTextures(1)
        self.width = 0
        self.height = 0

        if filepath:
            self._load_from_file(filepath)

    def _load_from_file(self, filepath: str):
        """
        Loads a standard image file (PNG, JPG) using Pillow.
        """
        # Bind the texture ID as the current active 2D texture
        glBindTexture(GL_TEXTURE_2D, self.id)

        # Set texture wrapping: Repeat the image if UV coordinates are > 1.0
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Set filtering: Linear allows for smooth scaling (anti-aliasing)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            # Load image using Pillow and force RGBA (Red, Green, Blue, Alpha)
            image = Image.open(filepath).convert("RGBA")
            
            # Flip image vertically. 
            # OpenGL expects origin (0,0) at Bottom-Left, but images are stored Top-Left.
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            img_data = image.tobytes()
            self.width, self.height = image.size

            # Upload texture data to the GPU
            glTexImage2D(
                GL_TEXTURE_2D,    # Target
                0,                # Mipmap level (0 = base level)
                GL_RGBA,          # Internal format (how GPU stores it)
                self.width, self.height, 
                0,                # Border (must be 0)
                GL_RGBA,          # Format of the input data
                GL_UNSIGNED_BYTE, # Data type of the pixel data
                img_data          # The actual pixel bytes
            )
            
            # Generate mipmaps (smaller versions of texture for optimization at distance)
            glGenerateMipmap(GL_TEXTURE_2D)
            
        except IOError as e:
            Logger.info(f"Failed to load texture '{filepath}': {e}")
            sys.exit(1)

        # Unbind the texture to prevent accidental modification
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self, slot: int = 0):
        """
        Binds the texture to a specific texture unit slot (e.g., GL_TEXTURE0).
        """
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def destroy(self):
        glDeleteTextures(1, [self.id])

    @staticmethod
    def create_from_surface(surface) -> 'Texture':
        """
        Creates an OpenGL texture from an SDL2 Surface.
        Used primarily for Text Rendering (SDL_ttf).
        
        This method handles:
        1. Vertical flipping (SDL is Top-Left, OpenGL is Bottom-Left).
        2. Memory alignment (Pitch/Padding).
        3. Color format conversion (BGRA to RGBA).
        """
        texture = Texture()
        texture.width = surface.w
        texture.height = surface.h

        # =================================================================
        # STEP 1: IN-MEMORY VERTICAL FLIP
        # =================================================================
        # Since we cannot easily "transpose" a raw C pointer like a Pillow image,
        # we manually swap the rows in memory using ctypes.
        
        pitch = surface.pitch       # Length of one row in bytes (includes padding)
        height = surface.h
        pixels_ptr = surface.pixels # Raw C pointer to the pixel data

        # Create a temporary buffer to hold one row during the swap
        temp_row_buffer = ctypes.create_string_buffer(pitch)

        # Iterate over the top half of the image
        for i in range(height // 2):
            # Pointer to the current top row
            top_row_ptr = pixels_ptr + (i * pitch)
            # Pointer to the corresponding bottom row
            bottom_row_ptr = pixels_ptr + ((height - i - 1) * pitch)

            # Perform the swap:
            # 1. Copy Top row -> Temp buffer
            ctypes.memmove(temp_row_buffer, top_row_ptr, pitch)
            # 2. Copy Bottom row -> Top row location
            ctypes.memmove(top_row_ptr, bottom_row_ptr, pitch)
            # 3. Copy Temp buffer (old Top) -> Bottom row location
            ctypes.memmove(bottom_row_ptr, temp_row_buffer, pitch)
            
        # =================================================================
        # STEP 2: UPLOAD TO GPU
        # =================================================================

        glBindTexture(GL_TEXTURE_2D, texture.id)
        
        # Handle SDL Pitch (Padding):
        # Calculate the exact row length in pixels (including padding).
        bytes_per_pixel = 4 # RGBA/BGRA = 4 bytes
        pixel_row_length = surface.pitch // bytes_per_pixel
        
        # Tell OpenGL how long a row is in memory (to handle padding correctly)
        glPixelStorei(GL_UNPACK_ROW_LENGTH, pixel_row_length)
        # Set alignment to 1 byte to prevent artifacts on odd-width images
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Get the raw bytes from the (now flipped) surface pointer
        data_size = surface.pitch * surface.h
        pixel_data = ctypes.string_at(surface.pixels, data_size)

        # SDL Surfaces usually use BGRA layout on standard architectures
        input_format = GL_BGRA

        glTexImage2D(
            GL_TEXTURE_2D, 
            0, 
            GL_RGBA,            # Store as RGBA in GPU
            texture.width, texture.height, 
            0, 
            input_format,       # Read as BGRA from CPU
            GL_UNSIGNED_BYTE, 
            pixel_data
        )
        
        # Configure Parameters (No mipmaps for text/UI usually)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # IMPORTANT: Reset global state to defaults to avoid breaking other texture loads
        glPixelStorei(GL_UNPACK_ROW_LENGTH, 0)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 4)

        glBindTexture(GL_TEXTURE_2D, 0)
        
        return texture
    