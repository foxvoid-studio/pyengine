import sys
import ctypes
from sdl2 import *
from OpenGL.GL import *
from pyengine.gl_utils.shader import ShaderProgram
from pyengine.gl_utils.mesh import Triangle, Rectangle
from pyengine.gl_utils.texture import Texture
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.ecs.entity_manager import EntityManager
from pyengine.graphics.render_system import RenderSystem
from pyengine.core.input_manager import InputManager


# =============================================================================
# CLASS: App
# Main application class handling SDL2 windowing and the game loop.
# =============================================================================
class App:
    def __init__(self, width: int, height: int, title: str):
        """
        Initializes SDL2, creates a window and an OpenGL context.
        """
        self.title = title.encode("utf-8")
        self.width = width
        self.height = height
        self.running = False
        self._init_sdl()
        
        self.input = InputManager()
        self.entity_manager = EntityManager()
        self.render_system = RenderSystem()
        
        self.shader = None
        self.meshes = [] 
        self._init_scene()

    def _init_sdl(self) -> None:
        """
        Sets up the SDL2 video subsystem and window parameters.
        """
        # Initialize the video subsystem
        if SDL_Init(SDL_INIT_VIDEO) != 0:
            print(f"Failed to initialize SDL: {SDL_GetError()}")
            sys.exit(-1)

        # Set OpenGL attributes *before* creating the window.
        # Request an OpenGL 3.3 Core profile (Standard for modern Desktop GL).
        # On mobile, Buildozer/SDL2 will handle the GLES context creation automatically.
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

        # Create the window with the OpenGL support flag
        self.window = SDL_CreateWindow(
            self.title,
            SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED,
            self.width,
            self.height,
            SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE
        )

        if not self.window:
            print(f"Failed to create window: {SDL_GetError()}")
            sys.exit(-1)

        # Create the OpenGL Context and attach it to the window
        self.context = SDL_GL_CreateContext(self.window)

        # Enable V-Sync (1 = on, 0 = off) to prevent screen tearing
        SDL_GL_SetSwapInterval(1)

        # Initialize the viewport to match window dimensions
        glViewport(0, 0, self.width, self.height)

    def _init_scene(self) -> None:
        # 1. Load Shader
        self.shader = ShaderProgram.from_files("shaders/mesh.vert", "shaders/mesh.frag")

        logo_texture = Texture("assets/logo.png")

        tri_geo = Triangle(self.shader)
        rect_geo = Rectangle(self.shader)
        self.meshes.extend([tri_geo, rect_geo])

        # Entity 1: Rotating Triangle
        e1 = self.entity_manager.create_entity()
        self.entity_manager.add_component(e1, Transform(position=(0,0,0), scale=(0.5, 0.5, 1)))
        self.entity_manager.add_component(e1, MeshRenderer(tri_geo, self.shader, logo_texture))

        # Entity 2: Rectangle
        e2 = self.entity_manager.create_entity()
        self.entity_manager.add_component(e2, Transform(position=(-0.6, 0, 0), scale=(0.7, 0.7, 1)))
        self.entity_manager.add_component(e2, MeshRenderer(rect_geo, self.shader, logo_texture))

        # Entity 3: Ground
        e3 = self.entity_manager.create_entity()
        self.entity_manager.add_component(e3, Transform(position=(0.6, -0.5, 0), scale=(0.8, 0.1, 1)))
        self.entity_manager.add_component(e3, MeshRenderer(rect_geo, self.shader, logo_texture))

    def process_events(self) -> None:
        """
        Handles the SDL event loop (Keyboard, Window events).
        """
        event = SDL_Event()

        # Poll all pending events
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            # Let the InputManager see the event first
            self.input.process_event(event)

            if event.type == SDL_QUIT:
                self.running = False

            elif event.type == SDL_WINDOWEVENT:
                if event.window.event == SDL_WINDOWEVENT_RESIZED:
                    # Update viewport when window is resized
                    glViewport(0, 0, event.window.data1, event.window.data2)

    def run(self) -> None:
        """
        The main application loop.
        """
        self.running = True
        
        while self.running:
            # 1. Prepare Input Manager for the new frame (clear "just pressed" flags)
            self.input.update()

            # 2. Handle input/events (fills Input Manager with new data)
            self.process_events()

            # 3. Game Logic using InputManager
            if self.input.is_key_pressed(SDLK_ESCAPE):
                self.running = False
            
            for entity, (transform,) in self.entity_manager.get_entities_with(Transform):
                if entity == 0:
                    transform.rotation.z += 0.02
            
            # Render
            self.render_system.update(self.entity_manager)

            # Swap the buffers (Display the newly drawn frame)
            SDL_GL_SwapWindow(self.window)

        # Explicit cleanup call before exiting
        self._cleanup()

    def _cleanup(self) -> None:
        """
        Clean up OpenGL resources explicitly before destroying the context.
        This prevents 'sys.meta_path is None' errors during interpreter shutdown.
        """
        # Loop through meshes and destroy them
        for mesh in self.meshes:
            mesh.destroy()

        if self.shader:
            self.shader.destroy()

        # Destroy SDL context and window
        SDL_GL_DeleteContext(self.context)
        SDL_DestroyWindow(self.window)
        SDL_Quit()
