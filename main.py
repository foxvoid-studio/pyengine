import glm
from sdl2 import SDL_SetRelativeMouseMode, SDL_TRUE
from pyengine.core.app import App
from pyengine.gl_utils.mesh import Cylinder, Plane, Rectangle, Cube, Sphere
from pyengine.graphics.camera import Camera2D, Camera3D, MainCamera
from pyengine.graphics.light import DirectionalLight, PointLight
from pyengine.graphics.material import Material
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.graphics.sprite import Animation, Animator, SpriteSheet
from pyengine.gui.text_renderer import TextRenderer
from pyengine.gui.ui_box import UIBox
from pyengine.physics.transform import Transform


# =============================================================================
# CLASS: Game2D
# Example of a 2D Top-Down
# =============================================================================
class Game2D(App):
    def startup(self):
        """
        Called once when the application starts.
        Sets up the 2D scene, player, and camera.
        """
        super().startup()

        # 1. Load the Standard Shader
        # We reuse the same shader for both 2D and 3D in this engine (it supports lighting and sprites).
        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")

        # 2. Setup the 2D Camera
        # Create an entity to hold the camera components.
        self.camera_entity = self.entity_manager.create_entity()
        
        # Position the camera at Z=1 to ensure it sees objects at Z=0.
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 0, 1)))
        
        # Add the Camera2D component (Orthographic projection).
        # ortho_size=5.0 means the screen shows 5 world units vertically.
        self.entity_manager.add_component(self.camera_entity, Camera2D(self.width, self.height, ortho_size=5.0))
        
        # Tag this camera as the Main Camera so the RenderSystem uses it.
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        # 3. Create the Player Entity
        # Load the sprite sheet texture.
        player_base = self.resources.get_texture("assets/player_base.png")
        
        # Create a material using the shader and the texture.
        mat_player = Material(shader, texture=player_base)
        
        # Create a simple Rectangle geometry for the sprite.
        rect_geo = Rectangle(shader)

        player = self.entity_manager.create_entity()
        
        # Add Transform (position, rotation, scale).
        self.entity_manager.add_component(player, Transform())
        
        # Add MeshRenderer to draw the rectangle with the player texture.
        self.entity_manager.add_component(player, MeshRenderer(rect_geo, mat_player))
        
        # Add SpriteSheet component to handle UV mapping for animation frames.
        # This specific asset has 56 rows and 9 columns.
        self.entity_manager.add_component(player, SpriteSheet(rows=56, cols=9))

        # 4. Setup Animation
        # Animator component manages the state of animations.
        player_animator = Animator()
        
        # Register an animation named "idle_down".
        # Frames 0 to 5, playing at 0.1 seconds per frame.
        player_animator.add("idle_down", Animation(0, 5, 0.1))
        
        # Start playing the animation immediately.
        player_animator.play("idle_down")
        
        self.entity_manager.add_component(player, player_animator)


# =============================================================================
# CLASS: Game3D
# Example of a 3D Scene with lighting, primitives, loaded models, and UI.
# =============================================================================
class Game3D(App):
    def startup(self):
        """
        Called once when the application starts.
        Sets up the 3D environment.
        """
        super().startup()
        
        # Lock the mouse cursor to the window and hide it.
        # This is essential for FPS-style camera controls using mouse delta.
        SDL_SetRelativeMouseMode(SDL_TRUE)

        # 1. Load Resources (Assets)
        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")
        ui_shader = self.resources.get_shader("shaders/ui.vert", "shaders/ui.frag") # <--- NEW: Load UI Shader
        
        # Load textures
        tex_logo = self.resources.get_texture("assets/logo.png")
        
        # Create a shared material for basic objects
        mat_object = Material(shader, tex_logo)

        # 2. Setup the 3D Camera
        self.camera_entity = self.entity_manager.create_entity()
        
        # Position the camera slightly up and back (0, 1, 3).
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 1, 3)))
        
        # Add Camera3D component (Perspective projection). FOV is 70 degrees.
        self.entity_manager.add_component(self.camera_entity, Camera3D(self.width, self.height, fov=70.0))
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        # 3. Create Scene Objects (Primitives)
        
        # --- FLOOR (Plane) ---
        # A large flat plane (20x20 units), texture repeats 5 times (tile_u/v).
        plane_geo = Plane(shader, width=20, depth=20, tile_u=5, tile_v=5)
        floor = self.entity_manager.create_entity()
        self.entity_manager.add_component(floor, Transform(position=(0, 0, 0)))
        self.entity_manager.add_component(floor, MeshRenderer(plane_geo, mat_object))

        # --- SPHERE (Left) ---
        sphere_geo = Sphere(shader, radius=0.5, sectors=32, stacks=16)
        sphere = self.entity_manager.create_entity()
        self.entity_manager.add_component(sphere, Transform(position=(-1.5, 0.5, 0))) # Lift y by radius (0.5)
        self.entity_manager.add_component(sphere, MeshRenderer(sphere_geo, mat_object))

        # --- CYLINDER (Right) ---
        cyl_geo = Cylinder(shader, radius=0.5, height=1.5)
        cylinder = self.entity_manager.create_entity()
        self.entity_manager.add_component(cylinder, Transform(position=(1.5, 0.75, 0))) # Lift y by half height
        self.entity_manager.add_component(cylinder, MeshRenderer(cyl_geo, mat_object))

        # --- CUBE (Center) ---
        cube_geo = Cube(shader)
        cube = self.entity_manager.create_entity()
        self.entity_manager.add_component(cube, Transform(position=(0, 0.5, 0)))
        self.entity_manager.add_component(cube, MeshRenderer(cube_geo, mat_object))

        # 4. Load External Model (OBJ)
        # --- Pyramid from obj file ---
        # load_model returns a list of (Mesh, Material) tuples because an OBJ can contain multiple parts.
        mesh_pyramid_part = self.resources.load_model("assets/pyramid.obj", shader)
        
        for mesh, material in mesh_pyramid_part:
            part_entity = self.entity_manager.create_entity()
            # Position it to the right
            self.entity_manager.add_component(part_entity, Transform(position=(3.0, 0.5, 0.0)))
            self.entity_manager.add_component(part_entity, MeshRenderer(mesh, material))

        # 5. Setup Lighting
        # Lighting is handled by adding specific components to entities.

        # --- Directional Light (Sun/Moon) ---
        sun_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(sun_entity, DirectionalLight(
            color=(0.5, 0.5, 0.8), # Bluish tint (Moonlight/Night)
            intensity=0.5,
            direction=(0.5, -1.0, 0.0) # Light coming from above-right
        ))

        # --- Point Light (Lamp/Fire) ---
        lamp_entity = self.entity_manager.create_entity()
        # Position the light near the pyramid
        self.entity_manager.add_component(lamp_entity, Transform(position=(2.5, 0.5, 1.0)))
        self.entity_manager.add_component(lamp_entity, PointLight(
            color=(1.0, 0.2, 0.0), # Orange/Red color
            intensity=2.0,
            radius=5.0
        ))
        
        # (Optional) Visual Debug: Add a small white cube to visualize the light source position
        mesh_cube = Cube(shader)
        mat_white = Material(shader, color=(1, 1, 1, 1)) # Pure white, no texture
        self.entity_manager.add_component(lamp_entity, MeshRenderer(mesh_cube, mat_white))
        # Scale it down so it looks like a small bulb
        self.entity_manager.get_component(lamp_entity, Transform).scale = glm.vec3(0.2)

        # 6. UI Setup (Text & Box)
        
        # Load TrueType Font (Roboto)
        font_roboto = self.resources.get_font("assets/roboto.ttf", 32) # Size 32pt

        # --- UI Box (Background Panel) ---
        self.panel_entity = self.entity_manager.create_entity()
        
        # Center Position for the box (Screen Coordinates)
        # Assuming window is 800x600, top-left area. 
        # X=90, Y=575 (near top)
        box_pos = (90, 575, 0)
        self.entity_manager.add_component(self.panel_entity, Transform(position=box_pos))
        
        # Create the UIBox component
        # width=160px, height=50px, Dark gray semi-transparent, Rounded corners
        ui_box = UIBox(width=160, height=50, color=(0.1, 0.1, 0.1, 0.7), border_radius=10.0)
        
        # Assign the UI Shader (Critical for the rounded rect logic)
        ui_box.material = Material(ui_shader)
        
        self.entity_manager.add_component(self.panel_entity, ui_box)

        # --- FPS Text ---
        self.text_entity = self.entity_manager.create_entity()
        
        # Position is in Screen Coordinates (Pixels).
        # We put the text at the same position (center of the box) because 
        # RenderSystem centers the quad geometry.
        # Note: If text looks off-center, you might need to adjust offsets manually
        # since text alignment depends on the generated texture size.
        self.entity_manager.add_component(self.text_entity, Transform(position=box_pos))
        
        # Create TextRenderer component
        text_comp = TextRenderer(font_roboto, "FPS: 0", color=(255, 255, 0)) # Yellow Text
        
        # Manually attach a material so RenderSystem can use the shader for the text quad.
        # The texture is initially None; TextRenderer will generate it from the font.
        text_comp.material = Material(shader, texture=None)
        
        self.entity_manager.add_component(self.text_entity, text_comp)

    def temp_game_logic(self):
        """
        Called every frame. Used for simple logic before we have a full Scripting system.
        """
        super().temp_game_logic()

        # Update FPS Text
        # Retrieve the TextRenderer component and update its string.
        text_comp = self.entity_manager.get_component(self.text_entity, TextRenderer)
        if text_comp:
            text_comp.text = f"FPS: {self.time.fps}"


class KenneyGame(App):
    def startup(self):
        super().startup()

        SDL_SetRelativeMouseMode(SDL_TRUE)

        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")

        self.camera_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 1, 3)))
        self.entity_manager.add_component(self.camera_entity, Camera3D(self.width, self.height, fov=70.0))
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        block_grass_model = self.resources.load_model("assets/kenney/block-grass.obj", shader)

        for mesh, material in block_grass_model:
            part_entity = self.entity_manager.create_entity()
            self.entity_manager.add_component(part_entity, Transform(position=(3.0, 0.5, 0.0)))
            self.entity_manager.add_component(part_entity, MeshRenderer(mesh, material))

        sun_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(sun_entity, DirectionalLight(
            color=(0.5, 0.5, 0.8), # Bluish tint (Moonlight/Night)
            intensity=0.5,
            direction=(0.5, -1.0, 0.0) # Light coming from above-right
        ))

        font_roboto = self.resources.get_font("assets/roboto.ttf", 32) # Size 32pt

        self.text_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.text_entity, Transform(position=(90, 575, 0)))
        text_comp = TextRenderer(font_roboto, "FPS: 0", color=(255, 255, 0))
        text_comp.material = Material(shader, texture=None)

        self.entity_manager.add_component(self.text_entity, text_comp)

    def temp_game_logic(self):
        super().temp_game_logic()

        text_comp = self.entity_manager.get_component(self.text_entity, TextRenderer)
        if text_comp:
            text_comp.text = f"FPS: {self.time.fps}"

if __name__ == "__main__":
    # Create and run the 3D Game
    app = KenneyGame(800, 600, "Pyengine")
    app.run()
