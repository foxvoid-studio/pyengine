import glm
from sdl2 import SDL_SetRelativeMouseMode, SDL_TRUE
from pyengine.core.app import App
from pyengine.gl_utils.mesh import Cylinder, Plane, Rectangle, Cube, Sphere
from pyengine.graphics.camera import Camera2D, Camera3D, MainCamera
from pyengine.graphics.light import DirectionalLight, PointLight
from pyengine.graphics.material import Material
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.graphics.sprite import Animation, Animator, SpriteSheet
from pyengine.physics.transform import Transform


class Game2D(App):
    def startup(self):
        super().startup()

        # 1. Load Shader
        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")

        self.camera_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 0, 1)))
        self.entity_manager.add_component(self.camera_entity, Camera2D(self.width, self.height, ortho_size=5.0))
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        # Create player
        player_base = self.resources.get_texture("assets/player_base.png")
        mat_player = Material(self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag"), texture=player_base)
        rect_geo = Rectangle(shader)

        player = self.entity_manager.create_entity()
        self.entity_manager.add_component(player, Transform())
        self.entity_manager.add_component(player, MeshRenderer(rect_geo, mat_player))
        self.entity_manager.add_component(player, SpriteSheet(rows=56, cols=9))

        player_animator = Animator()
        player_animator.add("idle_down", Animation(0, 5, 0.1))
        player_animator.play("idle_down")
        self.entity_manager.add_component(player, player_animator)


class Game3D(App):
    def startup(self):
        super().startup()
        
        SDL_SetRelativeMouseMode(SDL_TRUE)

        # 1. Load Resources
        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")
        
        # Load textures
        tex_logo = self.resources.get_texture("assets/logo.png")
        
        mat_object = Material(shader, tex_logo)

        # 2. Camera
        self.camera_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 1, 3)))
        self.entity_manager.add_component(self.camera_entity, Camera3D(self.width, self.height, fov=70.0))
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        # 3. Create Scene
        
        # --- FLOOR ---
        plane_geo = Plane(shader, width=20, depth=20, tile_u=5, tile_v=5)
        floor = self.entity_manager.create_entity()
        self.entity_manager.add_component(floor, Transform(position=(0, 0, 0)))
        self.entity_manager.add_component(floor, MeshRenderer(plane_geo, mat_object))

        # --- SPHERE ---
        sphere_geo = Sphere(shader, radius=0.5, sectors=32, stacks=16)
        sphere = self.entity_manager.create_entity()
        self.entity_manager.add_component(sphere, Transform(position=(-1.5, 0.5, 0))) # Lift y by 0.5 (radius) to sit on floor
        self.entity_manager.add_component(sphere, MeshRenderer(sphere_geo, mat_object))

        # --- CYLINDER ---
        cyl_geo = Cylinder(shader, radius=0.5, height=1.5)
        cylinder = self.entity_manager.create_entity()
        self.entity_manager.add_component(cylinder, Transform(position=(1.5, 0.75, 0))) # Lift y by half height
        self.entity_manager.add_component(cylinder, MeshRenderer(cyl_geo, mat_object))

        # --- CUBE (Middle) ---
        cube_geo = Cube(shader)
        cube = self.entity_manager.create_entity()
        self.entity_manager.add_component(cube, Transform(position=(0, 0.5, 0)))
        self.entity_manager.add_component(cube, MeshRenderer(cube_geo, mat_object))

        # --- Pyramid from obj file ---
        # mesh_pyramid = self.resources.get_mesh("assets/pyramid.obj", shader)
        # pyramid = self.entity_manager.create_entity()
        # self.entity_manager.add_component(pyramid, Transform(position=(2.0, 0.5, 0.0)))
        # self.entity_manager.add_component(pyramid, MeshRenderer(mesh_pyramid, mat_object))

        # --- Pyramid from obj file ---
        mesh_pyramid_part = self.resources.load_model("assets/pyramid.obj", shader)
        for mesh, material in mesh_pyramid_part:
            part_entity = self.entity_manager.create_entity()
            self.entity_manager.add_component(part_entity, Transform(position=(3.0, 0.5, 0.0)))
            self.entity_manager.add_component(part_entity, MeshRenderer(mesh, material))

        # --- LIGHTS ---

        # 1. Directional Light (Soleil / Lune)
        sun_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(sun_entity, DirectionalLight(
            color=(0.5, 0.5, 0.8), # Bleuté (Nuit/Lune)
            intensity=0.5,
            direction=(0.5, -1.0, 0.0) # Vient du haut
        ))

        # 2. Point Light (Feu de camp / Lampe Rouge)
        lamp_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(lamp_entity, Transform(position=(2.5, 0.5, 1.0))) # Proche de la pyramide
        self.entity_manager.add_component(lamp_entity, PointLight(
            color=(1.0, 0.2, 0.0), # Rouge/Orange
            intensity=2.0,
            radius=5.0
        ))
        
        # Optionnel: Ajoute un petit Cube Blanc à la position de la lampe pour voir où elle est !
        mesh_cube = Cube(shader)
        mat_white = Material(shader, color=(1, 1, 1, 1)) # Pas de texture, juste blanc
        self.entity_manager.add_component(lamp_entity, MeshRenderer(mesh_cube, mat_white))
        # Tu devras réduire l'échelle du cube de la lampe dans le transform (ex: scale=(0.2, 0.2, 0.2))
        self.entity_manager.get_component(lamp_entity, Transform).scale = glm.vec3(0.2)


if __name__ == "__main__":
    app = Game3D(800, 600, "Pyengine")
    app.run()
    