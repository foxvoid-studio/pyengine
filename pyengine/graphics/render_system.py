import glm
from OpenGL.GL import *
from pyengine.core.logger import Logger
from pyengine.ecs.entity_manager import EntityManager
from pyengine.gui.ui_box import UIBox
from pyengine.physics.transform import Transform
from pyengine.graphics.mesh_renderer import MeshRenderer
from pyengine.graphics.camera import Camera2D, Camera3D, MainCamera
from pyengine.graphics.material import Material
from pyengine.graphics.sprite import SpriteSheet
from pyengine.graphics.light import DirectionalLight, PointLight
from pyengine.gui.text_renderer import TextRenderer
from pyengine.gl_utils.mesh import Rectangle

class RenderSystem:
    def __init__(self):
        self.box_mesh = None  # Uses ui.vert (No Normals)
        self.text_mesh = None # Uses mesh.vert (With Normals)

    def update(self, entity_manager: EntityManager):
        """
        Main rendering loop orchestration.
        """
        # 1. Clear Screen
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 2. Find Camera & Determine Mode (2D vs 3D)
        camera_data = self._find_active_camera(entity_manager)
        if not camera_data:
            return # Warning is logged inside _find_active_camera

        cam_component, cam_transform, is_3d_mode = camera_data

        # 3. Collect Lights (shared for the whole frame)
        lights = self._collect_lights(entity_manager)

        # 4. RENDER WORLD (Meshes, Sprites, 3D Models)
        self._render_world_pass(entity_manager, cam_component, cam_transform, is_3d_mode, lights)

        # 5. RENDER UI (Text, Overlays)
        self._render_ui_pass(entity_manager)

    # =========================================================================
    # INTERNAL HELPERS (LOGIC SEPARATION)
    # =========================================================================

    def _find_active_camera(self, entity_manager: EntityManager):
        """
        Returns (camera_component, camera_transform, is_3d_mode) or None.
        """
        for entity, (main_cam_tag, transform) in entity_manager.get_entities_with(MainCamera, Transform):
            c3d = entity_manager.get_component(entity, Camera3D)
            c2d = entity_manager.get_component(entity, Camera2D)
            
            if c3d: return c3d, transform, True
            if c2d: return c2d, transform, False
        
        # Limit warning spam in a real engine, but fine for now
        # Logger.warning("No camera found") 
        return None

    def _collect_lights(self, entity_manager: EntityManager):
        """
        Returns a tuple (DirectionalLight, List[PointLights]).
        """
        dir_light = None
        for _, (l,) in entity_manager.get_entities_with(DirectionalLight):
            dir_light = l
            break 
        
        point_lights = []
        for _, (l, t) in entity_manager.get_entities_with(PointLight, Transform):
            point_lights.append((l, t))
            if len(point_lights) >= 4: break 
            
        return dir_light, point_lights

    # =========================================================================
    # RENDER PASSES
    # =========================================================================

    def _render_world_pass(self, entity_manager, camera, cam_transform, is_3d, lights):
        """
        Handles the rendering of the 3D/2D game world.
        """
        dir_light, point_lights = lights
        
        # Configure OpenGL for World
        if is_3d:
            glEnable(GL_DEPTH_TEST)
        else:
            glDisable(GL_DEPTH_TEST)

        # Pre-calculate Matrices
        view_matrix = camera.get_view_matrix(cam_transform)
        proj_matrix = camera.get_projection_matrix()

        # Render Loop
        for entity, (transform, renderer) in entity_manager.get_entities_with(Transform, MeshRenderer):
            material = renderer.material
            mesh = renderer.mesh
            shader = material.shader
            
            shader.use()

            # 1. Bind Material (Texture/Color)
            self._bind_material(material)

            # 2. Upload Lights
            self._upload_lighting_uniforms(shader, dir_light, point_lights)

            # 3. Handle SpriteSheet Animation
            self._upload_sprite_uniforms(entity_manager, entity, shader)

            # 4. Upload Matrices
            shader.set_uniform_matrix("u_view", view_matrix)
            shader.set_uniform_matrix("u_projection", proj_matrix)

            model = self._calculate_model_matrix(transform)
            shader.set_uniform_matrix("u_model", model)

            # 5. Draw
            mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, mesh.count)
            mesh.unbind()
            shader.unuse()

    def _render_ui_pass(self, entity_manager: EntityManager):
        """
        Handles the rendering of UI elements using separate meshes to prevent VAO conflicts.
        """
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width, height = viewport[2], viewport[3]
        ui_projection = glm.ortho(0.0, width, 0.0, height)
        ui_view = glm.mat4(1.0)

        # ---------------------------------------------------------
        # 1. RENDER UI BOXES (Using self.box_mesh)
        # ---------------------------------------------------------
        for entity, (transform, ui_box) in entity_manager.get_entities_with(Transform, UIBox):
            if not ui_box.material: continue
            
            shader = ui_box.material.shader
            shader.use()
            
            # Init box mesh if needed
            if self.box_mesh is None: 
                self.box_mesh = Rectangle(shader)

            # Uniforms
            glUniformMatrix4fv(glGetUniformLocation(shader.id, "u_view"), 1, GL_FALSE, glm.value_ptr(ui_view))
            glUniformMatrix4fv(glGetUniformLocation(shader.id, "u_projection"), 1, GL_FALSE, glm.value_ptr(ui_projection))
            glUniform4f(glGetUniformLocation(shader.id, "u_color"), *ui_box.color)
            glUniform2f(glGetUniformLocation(shader.id, "u_dimensions"), ui_box.width, ui_box.height)
            glUniform1f(glGetUniformLocation(shader.id, "u_radius"), ui_box.border_radius)

            # Transform
            model = glm.mat4(1.0)
            model = glm.translate(model, transform.position)
            model = glm.scale(model, glm.vec3(ui_box.width, ui_box.height, 1.0))
            glUniformMatrix4fv(glGetUniformLocation(shader.id, "u_model"), 1, GL_FALSE, glm.value_ptr(model))

            self.box_mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, self.box_mesh.count)
            self.box_mesh.unbind()
            shader.unuse()

        # ---------------------------------------------------------
        # 2. RENDER TEXT (Using self.text_mesh)
        # ---------------------------------------------------------
        for entity, (transform, text_renderer) in entity_manager.get_entities_with(Transform, TextRenderer):
            if text_renderer.is_dirty:
                if text_renderer.texture: text_renderer.texture.destroy()
                text_renderer.texture = text_renderer.font.render_text(text_renderer.text, text_renderer.color)
                text_renderer.is_dirty = False
                # If using generic material from main.py, it's fine.

            if not text_renderer.texture or not text_renderer.material: continue

            shader = text_renderer.material.shader
            shader.use()

            # Init text mesh if needed
            if self.text_mesh is None: 
                self.text_mesh = Rectangle(shader)

            # Bind Texture
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, text_renderer.texture.id)
            glUniform1i(glGetUniformLocation(shader.id, "u_texture"), 0)
            glUniform1i(glGetUniformLocation(shader.id, "u_use_texture"), 1)
            glUniform4f(glGetUniformLocation(shader.id, "u_color"), 1, 1, 1, 1)

            # Disable Lights for Text
            glUniform3f(glGetUniformLocation(shader.id, "u_ambientColor"), 1, 1, 1)
            glUniform1f(glGetUniformLocation(shader.id, "u_dirLight.intensity"), 0.0)
            glUniform1i(glGetUniformLocation(shader.id, "u_pointLightCount"), 0)
            
            # Reset UVs
            glUniform2f(glGetUniformLocation(shader.id, "u_uv_scale"), 1.0, 1.0)
            glUniform2f(glGetUniformLocation(shader.id, "u_uv_offset"), 0.0, 0.0)

            # Transform
            shader.set_uniform_matrix("u_view", ui_view)
            shader.set_uniform_matrix("u_projection", ui_projection)
            model = glm.mat4(1.0)
            model = glm.translate(model, transform.position)
            model = glm.scale(model, glm.vec3(text_renderer.texture.width, text_renderer.texture.height, 1.0))
            model = glm.scale(model, transform.scale)
            shader.set_uniform_matrix("u_model", model)

            self.text_mesh.bind()
            glDrawArrays(GL_TRIANGLES, 0, self.text_mesh.count)
            self.text_mesh.unbind()
            shader.unuse()

    # =========================================================================
    # LOW-LEVEL UPLOAD HELPERS
    # =========================================================================

    def _bind_material(self, material: Material):
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

    def _upload_lighting_uniforms(self, shader, dir_light, point_lights):
        # Ambient
        loc_amb = glGetUniformLocation(shader.id, "u_ambientColor")
        glUniform3f(loc_amb, 0.1, 0.1, 0.1)

        # Directional
        if dir_light:
            self._upload_dir_light(shader, dir_light)
        else:
            glUniform1f(glGetUniformLocation(shader.id, "u_dirLight.intensity"), 0.0)

        # Point Lights
        glUniform1i(glGetUniformLocation(shader.id, "u_pointLightCount"), len(point_lights))
        for i, (light, light_trans) in enumerate(point_lights):
            self._upload_point_light(shader, i, light, light_trans)

    def _upload_sprite_uniforms(self, entity_manager, entity, shader):
        sprite_sheet = entity_manager.get_component(entity, SpriteSheet)
        loc_scale = glGetUniformLocation(shader.id, "u_uv_scale")
        loc_offset = glGetUniformLocation(shader.id, "u_uv_offset")

        if sprite_sheet:
            sx, sy, ox, oy = sprite_sheet.get_uv_transform()
            glUniform2f(loc_scale, sx, sy)
            glUniform2f(loc_offset, ox, oy)
        else:
            glUniform2f(loc_scale, 1.0, 1.0)
            glUniform2f(loc_offset, 0.0, 0.0)

    def _calculate_model_matrix(self, transform):
        model = glm.mat4(1.0)
        model = glm.translate(model, transform.position)
        
        # Simple Euler Rotation (Sequential)
        if transform.rotation.x != 0: model = glm.rotate(model, transform.rotation.x, glm.vec3(1, 0, 0))
        if transform.rotation.y != 0: model = glm.rotate(model, transform.rotation.y, glm.vec3(0, 1, 0))
        if transform.rotation.z != 0: model = glm.rotate(model, transform.rotation.z, glm.vec3(0, 0, 1))

        model = glm.scale(model, transform.scale)
        return model

    def _upload_dir_light(self, shader, light: DirectionalLight):
        glUniform3f(glGetUniformLocation(shader.id, "u_dirLight.direction"), *light.direction)
        glUniform3f(glGetUniformLocation(shader.id, "u_dirLight.color"), *light.color)
        glUniform1f(glGetUniformLocation(shader.id, "u_dirLight.intensity"), light.intensity)

    def _upload_point_light(self, shader, index: int, light: PointLight, transform: Transform):
        base = f"u_pointLights[{index}]"
        glUniform3f(glGetUniformLocation(shader.id, f"{base}.position"), *transform.position)
        glUniform3f(glGetUniformLocation(shader.id, f"{base}.color"), *light.color)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.intensity"), light.intensity)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.constant"), light.constant)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.linear"), light.linear)
        glUniform1f(glGetUniformLocation(shader.id, f"{base}.quadratic"), light.quadratic)
