#version 120

#ifdef GL_ES
    precision mediump float;
#endif

varying vec2 v_texcoord;     // Received from vertex shader
varying vec3 v_normal;
varying vec3 v_frag_pos;

uniform sampler2D u_texture; // The texture object
uniform vec4 u_color;        // The tint color (R, G, B, A)
uniform int u_use_texture;   //Boolean flag (1 = use texture, 0 = use color only)

// Light Uniforms (We will set a default in shader for now)
// Directional Light coming from up-right-front
vec3 lightDir = normalize(vec3(0.5, 1.0, 0.5)); 
vec3 lightColor = vec3(1.0, 1.0, 1.0);
vec3 ambientColor = vec3(0.3, 0.3, 0.3); // Base brightness

void main() {
    // 1. Texture/Base Color
    vec4 objectColor = u_color;
    if (u_use_texture == 1) {
        objectColor = texture2D(u_texture, v_texcoord) * u_color;
    }

    // 2. Diffuse Lighting
    vec3 norm = normalize(v_normal);
    // Dot product between Normal and Light Direction
    // max(..., 0.0) ensures we don't get negative light (darkness)
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;

    // 3. Combine
    vec3 result = (ambientColor + diffuse) * objectColor.rgb;

    gl_FragColor = vec4(result, objectColor.a);
}
