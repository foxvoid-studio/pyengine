#version 120

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texcoord;      // Received from vertex shader
uniform sampler2D u_texture;  // The texture object

void main() {
    // Sample the color from the texture at coordinates v_texcoord
    gl_FragColor = texture2D(u_texture, v_texcoord);
}
