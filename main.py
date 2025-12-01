from sdl2 import SDL_SetRelativeMouseMode, SDL_TRUE
from pyengine.core.app import App
from pyengine.gl_utils.mesh import Rectangle, Cube
from pyengine.graphics.camera import Camera2D, Camera3D, MainCamera
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

        # 1. Load Shader
        shader = self.resources.get_shader("shaders/mesh.vert", "shaders/mesh.frag")

        self.camera_entity = self.entity_manager.create_entity()
        self.entity_manager.add_component(self.camera_entity, Transform(position=(0, 0, 3)))
        self.entity_manager.add_component(self.camera_entity, Camera3D(self.width, self.height, fov=90.0))
        self.entity_manager.add_component(self.camera_entity, MainCamera())

        logo_texture = self.resources.get_texture("assets/logo.png")
        logo_mat = Material(shader, logo_texture)

        cube_geo = Cube(shader)
        cube_entity = self.entity_manager.create_entity()

        # Rotate it a bit so we see it's 3D
        self.entity_manager.add_component(cube_entity, Transform(position=(0, 0, 0)))
        self.entity_manager.add_component(cube_entity, MeshRenderer(cube_geo, logo_mat))


if __name__ == "__main__":
    app = Game3D(800, 600, "Pyengine")
    app.run()
    