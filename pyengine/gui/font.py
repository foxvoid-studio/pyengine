import sdl2.sdlttf
from sdl2 import *
from pyengine.core.logger import Logger
from pyengine.gl_utils.texture import Texture


class Font:
    """
    Wrapper around SDL_ttf font.
    """
    def __init__(self, path: str, size: int):
        self.font = sdl2.sdlttf.TTF_OpenFont(path.encode(), size)
        if not self.font:
            Logger.error(f"Failed to load font: {path}")

    def render_text(self, text: str, color=(255, 255, 255)) -> Texture:
        """
        Renders a string to an SDL Surface, converts it to OpenGL Texture.
        """
        if not self.font:
            return None

        sdl_color = SDL_Color(color[0], color[1], color[2], 255)
        
        # Render text to Surface (Blended is best quality with alpha)
        surface = sdl2.sdlttf.TTF_RenderText_Blended(self.font, text.encode(), sdl_color)
        
        if not surface:
            return None

        # Create OpenGL Texture from surface
        texture = Texture.create_from_surface(surface.contents)
        
        # Free the SDL surface (we have the texture in GPU now)
        SDL_FreeSurface(surface)
        
        return texture

    def destroy(self):
        if self.font:
            sdl2.sdlttf.TTF_CloseFont(self.font)
            