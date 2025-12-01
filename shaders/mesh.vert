#version 120

attribute vec3 a_position;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;

uniform mat4 u_model;

void main() {
    gl_Position = u_model * vec4(a_position, 1.0);
    v_texcoord = a_texcoord;
}