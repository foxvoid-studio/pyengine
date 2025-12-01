import glm
from OpenGL.GL import *
from pyengine.ecs.entity_manager import EntityManager
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer


class RenderSystem:
    def update(self, entity_manager: EntityManager):
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        for _, (transform, renderer) in entity_manager.get_entities_with(Transform, MeshRenderer):
            
            # Accès via le material
            material = renderer.material
            mesh = renderer.mesh
            
            material.shader.use()

            # --- 1. Material Properties (Texture & Color) ---
            
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
                # Bonnes pratiques : binder la texture 0 par sécurité
                glBindTexture(GL_TEXTURE_2D, 0)

            # --- 2. Transform (Model Matrix) ---
            model = glm.mat4(1.0)
            model = glm.translate(model, transform.position)
            model = glm.rotate(model, transform.rotation.z, glm.vec3(0, 0, 1))
            model = glm.scale(model, transform.scale)
            
            loc_model = glGetUniformLocation(material.shader.id, "u_model")
            glUniformMatrix4fv(loc_model, 1, GL_FALSE, glm.value_ptr(model))

            # --- 3. Draw ---
            mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, mesh.count)
            mesh.unbind()
            
            material.shader.unuse()