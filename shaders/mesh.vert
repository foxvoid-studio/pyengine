#version 120

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

// Scale allows us to zoom into a single cell (e.g., 0.25 for a 4x4 grid)
uniform vec2 u_uv_scale; 
// Offset allows us to move to the specific cell (row/col)
uniform vec2 u_uv_offset;

void main() {
    // Standard MVP (Model-View-Projection) multiplication order
    // Note: GLSL multiplies right-to-left
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
    
    v_texcoord = (a_texcoord * u_uv_scale) + u_uv_offset;
}