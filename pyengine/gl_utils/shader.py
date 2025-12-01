import sys
import glm
from sdl2 import *
from OpenGL.GL import *
from OpenGL.GL import shaders

# =============================================================================
# Handles the compilation, linking, and management of GLSL shaders.
# =============================================================================
class ShaderProgram:
    def __init__(self, vertex_code: str, fragment_code: str):
        """
        Standard constructor taking raw GLSL strings.
        Compiles and links the shaders immediately.
        """
        self.id = None
        self.uniforms = {}
        self._compile(vertex_code, fragment_code)

    @classmethod
    def from_files(cls, vertex_path: str, fragment_path: str) -> 'ShaderProgram':
        """
        Factory method to create a ShaderProgram directly from file paths.
        Useful for keeping GLSL code in separate files.
        """
        try:
            # Read vertex shader source
            with open(vertex_path, 'r') as v_file:
                vertex_code = v_file.read()
            
            # Read fragment shader source
            with open(fragment_path, 'r') as f_file:
                fragment_code = f_file.read()
                
            # Return a new instance of ShaderProgram
            return cls(vertex_code, fragment_code)
            
        except IOError as e:
            print(f"Error loading shader files: {e}")
            sys.exit(1)

    def _compile(self, vertex_code: str, fragment_code: str) -> None:
        """
        Internal method to compile vertex and fragment shaders and link them into a program.
        """
        try:
            # Compile individual shaders
            vs = shaders.compileShader(vertex_code, GL_VERTEX_SHADER)
            fs = shaders.compileShader(fragment_code, GL_FRAGMENT_SHADER)

            # Link them together into a program
            self.id = shaders.compileProgram(vs, fs)

            # Shaders are now linked into the program, we can delete the individual objects
            # to free up memory.
            glDeleteShader(vs)
            glDeleteShader(fs)
        except shaders.ShaderCompilationError as e:
            print(f"Shader Compilation Error: {e}")
            sys.exit(1)

    def use(self) -> None:
        """Activates this shader program for subsequent rendering commands."""
        glUseProgram(self.id)

    def unuse(self) -> None:
        """Deactivates the current shader program."""
        glUseProgram(0)

    def get_attrib_location(self, attrib_name) -> int:
        """
        Retrieves the location ID of a specific attribute variable (e.g., 'a_position')
        from the compiled shader program.
        """
        return glGetAttribLocation(self.id, attrib_name)
    
    def set_uniform_matrix(self, name, matrix) -> None:
        """
        Sends a GLM 4x4 matrix to the shader.
        """
        if name not in self.uniforms:
            self.uniforms[name] = glGetUniformLocation(self.id, name)
        
        loc = self.uniforms[name]
        if loc != -1:
            # GL_FALSE because GLM is already Column-Major (OpenGL standard).
            # We use glm.value_ptr to get the raw C pointer of the matrix.
            glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(matrix))
    
    def destroy(self) -> None:
        """
        Explicitly delete the program from GPU memory.
        Must be called before the OpenGL context is destroyed.
        """
        if self.id:
            glDeleteProgram(self.id)
            self.id = None
            