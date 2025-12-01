#version 120

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

void main() {
    // Standard MVP (Model-View-Projection) multiplication order
    // Note: GLSL multiplies right-to-left
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
    
    v_texcoord = a_texcoord;
}