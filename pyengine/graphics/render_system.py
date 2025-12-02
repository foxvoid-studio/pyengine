import glm
from OpenGL.GL import *
from pyengine.core.logger import Logger
from pyengine.ecs.entity_manager import EntityManager
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.graphics.camera import Camera2D, Camera3D, MainCamera
from pyengine.graphics.material import Material
from pyengine.graphics.sprite import SpriteSheet
from pyengine.graphics.light import DirectionalLight, PointLight


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

    def _upload_dir_light(self, shader, light: DirectionalLight):
        # Helper to upload uniform struct
        glUniform3f(glGetUniformLocation(shader.id, "u_dirLight.direction"), *light.direction)
        glUniform3f(glGetUniformLocation(shader.id, "u_dirLight.color"), *light.color)
        glUniform1f(glGetUniformLocation(shader.id, "u_dirLight.intensity"), light.intensity)

    def _upload_point_light(self, shader, index: int, light: PointLight, transform: Transform):
        # Helper to construct array strings: u_pointLights[0].position
        base = f"u_pointLights[{index}]"
        
        glUniform3f(glGetUniformLocation(shader.id, f"{base}.position"), *transform.position)
        glUniform3f(glGetUniformLocation(shader.id, f"{base}.color"), *light.color)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.intensity"), light.intensity)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.constant"), light.constant)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.linear"), light.linear)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.quadratic"), light.quadratic)

    def update(self, entity_manager: EntityManager):
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 1. Find Main Camera (Generic search)
        camera_component = None
        camera_transform = None
        is_3d_mode = False

        # Look for entity with MainCamera AND Transform
        # Note: We check specifically for Camera3D or Camera2D
        # Or you can just duck-type if you iterate all entities with MainCamera
        
        for entity, (main_cam_tag, transform) in entity_manager.get_entities_with(MainCamera, Transform):
            # Check if it has 3D or 2D camera
            c3d = entity_manager.get_component(entity, Camera3D)
            c2d = entity_manager.get_component(entity, Camera2D)
            
            if c3d:
                camera_component = c3d
                camera_transform = transform
                is_3d_mode = True
                break
            elif c2d:
                camera_component = c2d
                camera_transform = transform
                is_3d_mode = False
                break
        
        if not camera_component:
            Logger.warning("No camera found")
            return
        
        if is_3d_mode:
            # 3D: We need Z-Buffer to handle occlusion
            glEnable(GL_DEPTH_TEST)
        else:
            # 2D: We usually disable Z-Buffer so sprites behave like layers 
            # (or use Z for layering, but disabling is safer for simple 2D)
            glDisable(GL_DEPTH_TEST)
        
        view_matrix = camera_component.get_view_matrix(camera_transform)
        proj_matrix = camera_component.get_projection_matrix()

        # --- LIGHTING SETUP (NEW) ---
        
        # 1. Find Directional Light (Only 1 supported in this shader version)
        dir_light = None
        for _, (l,) in entity_manager.get_entities_with(DirectionalLight):
            dir_light = l
            break # Take the first one found
        
        # 2. Find Point Lights
        point_lights = []
        for _, (l, t) in entity_manager.get_entities_with(PointLight, Transform):
            point_lights.append((l, t))
            if len(point_lights) >= 4: break # Max 4 lights

        for entity, (transform, renderer) in entity_manager.get_entities_with(Transform, MeshRenderer):
            
            # Accès via le material
            material: Material = renderer.material
            mesh = renderer.mesh
            
            material.shader.use()

            # --- 1. Material Properties (Texture & Color) ---
            self._bind_material(material)

            # --- UPLOAD LIGHT UNIFORMS ---
            
            # Ambient
            loc_amb = glGetUniformLocation(material.shader.id, "u_ambientColor")
            glUniform3f(loc_amb, 0.1, 0.1, 0.1) # Soft global ambient

            # Directional Light
            if dir_light:
                self._upload_dir_light(material.shader, dir_light)
            else:
                # Disable dir light (intensity 0)
                glUniform1f(glGetUniformLocation(material.shader.id, "u_dirLight.intensity"), 0.0)

            # Point Lights
            glUniform1i(glGetUniformLocation(material.shader.id, "u_pointLightCount"), len(point_lights))
            
            for i, (light, light_trans) in enumerate(point_lights):
                self._upload_point_light(material.shader, i, light, light_trans)

            # Check if this entity has a SpriteSheet component
            sprite_sheet = entity_manager.get_component(entity, SpriteSheet)
            loc_scale = glGetUniformLocation(material.shader.id, "u_uv_scale")
            loc_offset = glGetUniformLocation(material.shader.id, "u_uv_offset")

            if sprite_sheet:
                # Calculate UVs based on current frame
                sx, sy, ox, oy = sprite_sheet.get_uv_transform()
                glUniform2f(loc_scale, sx, sy)
                glUniform2f(loc_offset, ox, oy)
            else:
                # Default for normal objects (Display full texture)
                glUniform2f(loc_scale, 1.0, 1.0)
                glUniform2f(loc_offset, 0.0, 0.0)

            # --- 2. Camera Matrices ---
            material.shader.set_uniform_matrix("u_view", view_matrix)
            material.shader.set_uniform_matrix("u_projection", proj_matrix)

            # --- 3. Model Matrix ---
            model = glm.mat4(1.0)
            model = glm.translate(model, transform.position)

            # Rotation logic (Handling 3D rotation vs 2D rotation)
            # transform.rotation is usually a vec3. 
            # Ideally, transform should handle full Quaternion or Euler XYZ rotation.
            # For now, applying axes sequentially:
            model = glm.rotate(model, transform.rotation.x, glm.vec3(1, 0, 0))
            model = glm.rotate(model, transform.rotation.y, glm.vec3(0, 1, 0))
            model = glm.rotate(model, transform.rotation.z, glm.vec3(0, 0, 1))

            model = glm.scale(model, transform.scale)

            material.shader.set_uniform_matrix("u_model",model)

            # --- 3. Draw ---
            mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, mesh.count)
            mesh.unbind()
            
            material.shader.unuse()
