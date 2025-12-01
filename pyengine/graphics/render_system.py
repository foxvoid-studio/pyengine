import glm
from OpenGL.GL import *
from pyengine.ecs.entity_manager import EntityManager
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer

class RenderSystem:
    def __init__(self):
        pass

    def update(self, entity_manager: EntityManager):
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        for _, (transform, renderer) in entity_manager.get_entities_with(Transform, MeshRenderer):
            renderer.shader.use()

            # 1. Texture Binding
            if renderer.texture:
                renderer.texture.bind(0) # Bind to slot 0
                # Tell shader that 'u_texture' is at slot 0
                # (You only strictly need to do this once per shader, but safe here)
                loc = glGetUniformLocation(renderer.shader.id, "u_texture")
                glUniform1i(loc, 0)

            # 2. Identity Matrix
            model = glm.mat4(1.0) 
            
            # 3. Translation
            model = glm.translate(model, transform.position)
            
            # 4. Rotation
            # We rotate around Z axis for 2D. 
            # (Note: GLM uses Radians. If you input degrees, use glm.radians(deg))
            model = glm.rotate(model, transform.rotation.z, glm.vec3(0, 0, 1))
            
            # 5. Scale
            model = glm.scale(model, transform.scale)
            
            # --- SEND TO GPU ---
            renderer.shader.set_uniform_matrix("u_model", model)

            # Draw
            renderer.mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, renderer.mesh.count)
            renderer.mesh.unbind()
            renderer.shader.unuse()
            