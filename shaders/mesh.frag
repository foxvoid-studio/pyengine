#version 120

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texcoord;     // Received from vertex shader
uniform sampler2D u_texture; // The texture object
uniform vec4 u_color;        // The tint color (R, G, B, A)
uniform int u_use_texture;   //Boolean flag (1 = use texture, 0 = use color only)

void main() {
    vec4 tex_color = vec4(1.0, 1.0, 1.0, 1.0);

    // If texture is enabled, sample it
    if (u_use_texture == 1) {
        tex_color = texture2D(u_texture, v_texcoord);
    }

    // Multiply the texture color (or white) by the tint color
    gl_FragColor = tex_color * u_color;
}
