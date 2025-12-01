import sys
from OpenGL.GL import *
from PIL import Image
from pyengine.core.logger import Logger


class Texture:
    def __init__(self, filepath: str):
        self.id = glGenTextures(1)
        self.filepath = filepath
        self._load_texture(filepath)

    def _load_texture(self, filepath: str):
        # Bind the texture as the current 2D texture
        glBindTexture(GL_TEXTURE_2D, self.id)

        # Set texture wrapping parameters (Repeat image if UV > 1.0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Set texture filtering parameters (Nearest for pixel art, Linear for smooth)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            # Load image using Pillow
            # We convert to RGBA to ensure we have an alpha channel
            image = Image.open(filepath).convert("RGBA")
            
            # Flip image vertically because OpenGL expects 0.0 on Y to be at the bottom
            # while images usually have 0.0 at the top
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            img_data = image.tobytes()
            width, height = image.size

            # Upload data to GPU
            glTexImage2D(
                GL_TEXTURE_2D,    # Target
                0,                # Mipmap level
                GL_RGBA,          # Internal format (how GPU stores it)
                width, height,    # Dimensions
                0,                # Border
                GL_RGBA,          # Format of the input data
                GL_UNSIGNED_BYTE, # Type of the input data
                img_data          # The actual pixel data
            )
            
            # Generate mipmaps (smaller versions of texture for far away objects)
            glGenerateMipmap(GL_TEXTURE_2D)
            
        except IOError as e:
            Logger.info(f"Failed to load texture '{filepath}': {e}")
            sys.exit(1)

        # Unbind
        glBindTexture(GL_TEXTURE_2D, 0)
    
    def bind(self, slot: int = 0):
        """
        Binds the texture to a specific texture unit slot (GL_TEXTURE0, GL_TEXTURE1, etc.)
        """
        glActiveTexture(GL_TEXTURE0 + slot)
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def destroy(self):
        glDeleteTextures(1, [self.id])
        