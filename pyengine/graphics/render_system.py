import glm
from OpenGL.GL import *
from pyengine.core.logger import Logger
from pyengine.ecs.entity_manager import EntityManager
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.graphics.camera import Camera2D, MainCamera
from pyengine.graphics.material import Material


class RenderSystem:
    def _bind_material(self, material: Material):
        # Helper to keep update() clean
        loc_color = glGetUniformLocation(material.shader.id, "u_color")
        loc_use_tex = glGetUniformLocation(material.shader.id, "u_use_texture")
        loc_tex = glGetUniformLocation(material.shader.id, "u_texture")

        glUniform4f(loc_color, *material.color)

        if material.texture:
            glUniform1i(loc_use_tex, 1)
            material.texture.bind(0)
            glUniform1i(loc_tex, 0)
        else:
            glUniform1i(loc_use_tex, 0)
            glBindTexture(GL_TEXTURE_2D, 0)

    def update(self, entity_manager: EntityManager):
        # 1. Find the Main Camera entity
        camera_component = None
        camera_transform = None

        # We look for entities having ALL three components
        for _, (cam, trans, _) in entity_manager.get_entities_with(Camera2D, Transform, MainCamera):
            camera_component = cam
            camera_transform = trans
            break # We only need one main camera
        
        # If no main camera is found, we can't render properly (or render default)
        if not camera_component:
            Logger.warning("No MainCamera found in scene!")
            return

        # Pre-calculate Camera Matrices once per frame
        view_matrix = camera_component.get_view_matrix(camera_transform)
        proj_matrix = camera_component.get_projection_matrix()

        glClearColor(0.1, 0.1, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        for _, (transform, renderer) in entity_manager.get_entities_with(Transform, MeshRenderer):
            
            # Accès via le material
            material: Material = renderer.material
            mesh = renderer.mesh
            
            material.shader.use()

            # --- 1. Material Properties (Texture & Color) ---
            self._bind_material(material)

            # --- 2. Camera Matrices ---
            material.shader.set_uniform_matrix("u_view", view_matrix)
            material.shader.set_uniform_matrix("u_projection", proj_matrix)

            # --- 3. Model Matrix ---
            model = glm.mat4(1.0)
            model = glm.translate(model, transform.position)
            model = glm.rotate(model, transform.rotation.z, glm.vec3(0, 0, 1))
            model = glm.scale(model, transform.scale)

            material.shader.set_uniform_matrix("u_model",model)

            # --- 3. Draw ---
            mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, mesh.count)
            mesh.unbind()
            
            material.shader.unuse()
