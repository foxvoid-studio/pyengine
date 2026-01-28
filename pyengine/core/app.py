import sys
import ctypes
import sdl2.sdlttf
from sdl2 import *
from OpenGL.GL import *
from pyengine.core.logger import Logger
from pyengine.physics.transform import Transform
from pyengine.ecs.entity_manager import EntityManager
from pyengine.graphics.render_system import RenderSystem
from pyengine.core.input_manager import InputManager
from pyengine.core.time_manager import TimeManager
from pyengine.core.asset_manager import AssetManager
from pyengine.graphics.camera import Camera2D, Camera3D
from pyengine.graphics.animation_system import AnimationSystem
from pyengine.ecs.scheduler import SystemScheduler, SchedulerType
from pyengine.ecs.resource import ResourceManager


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
        self.assets = AssetManager()
        self.entity_manager = EntityManager()

        self.resources = ResourceManager()
        self.resources.add(self.input)
        self.resources.add(self.time)
        self.resources.add(self.assets)
        self.resources.add(self.entity_manager)

        self.scheduler = SystemScheduler()

        self.scheduler.add(SchedulerType.Update, AnimationSystem())
        self.scheduler.add(SchedulerType.Render, RenderSystem())

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

        # Initialize SDL_ttf
        if sdl2.sdlttf.TTF_Init() == -1:
            Logger.critical("Failed to initialize SDL_ttf")
            sys.exit(-1)

        # Set OpenGL attributes *before* creating the window.
        # Request an OpenGL 3.3 Core profile (Standard for modern Desktop GL).
        # On mobile, Buildozer/SDL2 will handle the GLES context creation automatically.
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)

        SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)

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

                    cam_comp = self.entity_manager.get_component(self.camera_entity, Camera3D)
                    if cam_comp:
                        cam_comp.resize(new_w, new_h)

    def set_title(self, title: str) -> None:
        SDL_SetWindowTitle(self.window, title.encode())

    def run(self) -> None:
        """
        The main application loop.
        """
        self.running = True

        self.scheduler.execute(SchedulerType.StartUp, self.resources)
        
        while self.running:
            # 1. Update Time (Must be first)
            self.time.update()

            # 2. Prepare Input Manager for the new frame (clear "just pressed" flags)
            self.input.update()

            # 3. Handle input/events (fills Input Manager with new data)
            self.process_events()

            self.temp_game_logic()

            # Update Animations BEFORE Rendering
            self.scheduler.execute(SchedulerType.Update, self.resources)

            # Render
            self.scheduler.execute(SchedulerType.Render, self.resources)

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
        sdl2.sdlttf.TTF_Quit()
        SDL_GL_DeleteContext(self.context)
        SDL_DestroyWindow(self.window)
        SDL_Quit()

    def temp_game_logic(self):
        if self.input.is_key_pressed(SDLK_ESCAPE):
            self.running = False

        dt = self.time.delta_time
        cam_transform = self.entity_manager.get_component(self.camera_entity, Transform)

        # Essayons de récupérer les deux types de caméra
        cam_2d = self.entity_manager.get_component(self.camera_entity, Camera2D)
        cam_3d = self.entity_manager.get_component(self.camera_entity, Camera3D)

        # --- LOGIQUE 2D ---
        if cam_transform and cam_2d:
            # Zoom Molette
            scroll = self.input.get_mouse_wheel()
            if scroll != 0:
                cam_2d.zoom += scroll * 0.5
                if cam_2d.zoom < 0.1: cam_2d.zoom = 0.1
            
            # Mouvements Plan (X, Y)
            cam_speed = 5.0 * dt
            if self.input.is_key_down(SDLK_z): cam_transform.position.y += cam_speed
            if self.input.is_key_down(SDLK_s): cam_transform.position.y -= cam_speed
            if self.input.is_key_down(SDLK_q): cam_transform.position.x -= cam_speed
            if self.input.is_key_down(SDLK_d): cam_transform.position.x += cam_speed

        # --- LOGIQUE 3D ---
        elif cam_transform and cam_3d:
            # Mode FPS : La souris contrôle le regard
            # Nécessite: SDL_SetRelativeMouseMode(SDL_TRUE) dans le startup de Game3D
            
            # 1. Gestion de la souris (Look)
            x_rel, y_rel = ctypes.c_int(0), ctypes.c_int(0)
            SDL_GetRelativeMouseState(ctypes.byref(x_rel), ctypes.byref(y_rel))
            cam_3d.process_mouse_movement(x_rel.value, -y_rel.value)

            # 2. Gestion du Clavier (Move)
            # On bouge par rapport à la direction de la caméra (front/right)
            move_speed = 5.0 * dt
            
            if self.input.is_key_down(SDLK_z):
                cam_transform.position += cam_3d.front * move_speed
            if self.input.is_key_down(SDLK_s):
                cam_transform.position -= cam_3d.front * move_speed
            if self.input.is_key_down(SDLK_q):
                cam_transform.position -= cam_3d.right * move_speed
            if self.input.is_key_down(SDLK_d):
                cam_transform.position += cam_3d.right * move_speed
            
            # Optionnel : Monter/Descendre avec Space/Shift
            if self.input.is_key_down(SDLK_SPACE):
                cam_transform.position.y += move_speed
            if self.input.is_key_down(SDLK_LSHIFT):
                cam_transform.position.y -= move_speed
