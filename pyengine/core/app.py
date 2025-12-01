import sys
import ctypes
from sdl2 import *
from OpenGL.GL import *
from pyengine.core.logger import Logger
from pyengine.gl_utils.mesh import Triangle, Rectangle
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.ecs.entity_manager import EntityManager
from pyengine.graphics.render_system import RenderSystem
from pyengine.core.input_manager import InputManager
from pyengine.core.time_manager import TimeManager
from pyengine.core.resource_manager import ResourceManager
from pyengine.graphics.material import Material
from pyengine.graphics.camera import Camera2D, MainCamera
from pyengine.graphics.sprite import SpriteSheet, Animator, Animation
from pyengine.graphics.animation_system import AnimationSystem


# =============================================================================
# CLASS: App
# Main application class handling SDL2 windowing and the game loop.
# =============================================================================
class App:
    def __init__(self, width: int, height: int, title: str):
        """
        Initializes SDL2, creates a window and an OpenGL context.
        """
        Logger.init(name="GameApp", debug_mode=True)
        Logger.info(f"Starting Engine: {width}x{height} - {title}")
        
        self.title = title.encode("utf-8")
        self.width = width
        self.height = height
        self.running = False
        self._init_sdl()
        
        self.input = InputManager()
        self.time = TimeManager()
        self.resources = ResourceManager()
        self.entity_manager = EntityManager()

        self.animation_system = AnimationSystem()
        self.render_system = RenderSystem()

        self.camera_entity = None
        
        self.startup()

    def _init_sdl(self) -> None:
        """
        Sets up the SDL2 video subsystem and window parameters.
        """
        # Initialize the video subsystem
        if SDL_Init(SDL_INIT_VIDEO) != 0:
            Logger.critical(f"Failed to initialize SDL: {SDL_GetError()}")
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
            Logger.critical(f"Failed to create window: {SDL_GetError()}")
            sys.exit(-1)

        # Create the OpenGL Context and attach it to the window
        self.context = SDL_GL_CreateContext(self.window)

        # Enable V-Sync (1 = on, 0 = off) to prevent screen tearing
        SDL_GL_SetSwapInterval(1)

        # Initialize the viewport to match window dimensions
        glViewport(0, 0, self.width, self.height)

    def startup(self) -> None:
        # Enable blending for transparent PNGs (Important for sprites!)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
                    new_w, new_h = event.window.data1, event.window.data2

                    # Update viewport when window is resized
                    glViewport(0, 0, new_w, new_h)

                    # Retrieve Camera component to update aspect ratio
                    cam_comp = self.entity_manager.get_component(self.camera_entity, Camera2D)
                    if cam_comp:
                        cam_comp.resize(new_w, new_h)

    def set_title(self, title: str) -> None:
        SDL_SetWindowTitle(self.window, title.encode())

    def run(self) -> None:
        """
        The main application loop.
        """
        self.running = True
        
        while self.running:
            # 1. Update Time (Must be first)
            self.time.update()

            # 2. Prepare Input Manager for the new frame (clear "just pressed" flags)
            self.input.update()

            # 3. Handle input/events (fills Input Manager with new data)
            self.process_events()

            self.temp_game_logic()
            
            # (Optional but here for debug) Update window title with FPS
            self.set_title(f"{self.title.decode()} - FPS: {self.time.fps}")

            # Update Animations BEFORE Rendering
            self.animation_system.update(self.entity_manager, self.time)

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
        # Destroy SDL context and window
        SDL_GL_DeleteContext(self.context)
        SDL_DestroyWindow(self.window)
        SDL_Quit()

    def temp_game_logic(self):
        if self.input.is_key_pressed(SDLK_ESCAPE):
            self.running = False

        # Retrieve components for the camera entity
        cam_transform = self.entity_manager.get_component(self.camera_entity, Transform)
        cam_comp = self.entity_manager.get_component(self.camera_entity, Camera2D)

        if cam_transform and cam_comp:
            dt = self.time.delta_time
            scroll = self.input.get_mouse_wheel()

            if scroll != 0:
                zoom_amount = scroll * 0.5
                cam_comp.zoom += zoom_amount

                # SÉCURITÉ : Empêcher le zoom d'être négatif ou nul
                if cam_comp.zoom < 0.1:
                    cam_comp.zoom = 0.1

            cam_speed = 5.0 * dt

            # WASD to move Camera
            if self.input.is_key_down(SDLK_w):
                cam_transform.position.y += cam_speed
            if self.input.is_key_down(SDLK_s):
                cam_transform.position.y -= cam_speed
            if self.input.is_key_down(SDLK_a):
                cam_transform.position.x -= cam_speed
            if self.input.is_key_down(SDLK_d):
                cam_transform.position.x += cam_speed
