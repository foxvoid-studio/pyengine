#version 120

attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_texcoord;

varying vec2 v_texcoord;
varying vec3 v_normal;
varying vec3 v_frag_pos;

uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;

// Scale allows us to zoom into a single cell (e.g., 0.25 for a 4x4 grid)
uniform vec2 u_uv_scale;

// Offset allows us to move to the specific cell (row/col)
uniform vec2 u_uv_offset;

void main() {
    // Calculate world position
    vec4 world_pos = u_model * vec4(a_position, 1.0);
    v_frag_pos = world_pos.xyz;

    // Transform Normal to World Space
    // Ideally use a Normal Matrix (transpose(inverse(model))) to handle non-uniform scaling
    // For now, casting u_model to mat3 works if scaling is uniform.
    v_normal = mat3(u_model) * a_normal;

    gl_Position = u_projection * u_view * world_pos;
    
    v_texcoord = (a_texcoord * u_uv_scale) + u_uv_offset;
}