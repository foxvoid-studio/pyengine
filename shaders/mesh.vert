#version 120
attribute vec3 a_position;

// New: Model Matrix uniform to handle position/rotation/scale
uniform mat4 u_model;

void main() {
    // Multiply the matrix by the vertex position
    gl_Position = u_model * vec4(a_position, 1.0);
}