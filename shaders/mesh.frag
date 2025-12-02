#version 120

#ifdef GL_ES
    precision mediump float;
#endif

// --- INPUTS ---
varying vec2 v_texcoord;
varying vec3 v_normal;
varying vec3 v_frag_pos;

// --- UNIFORMS ---
uniform sampler2D u_texture;
uniform vec4 u_color;
uniform int u_use_texture;

uniform vec3 u_view_pos; // Need camera position for specular (later), or simple distance checks

// --- LIGHT STRUCTURES ---
struct DirLight {
    vec3 direction;
    vec3 color;
    float intensity;
};

struct PointLight {
    vec3 position;
    vec3 color;
    float intensity;
    
    float constant;
    float linear;
    float quadratic;
};

// Define max number of lights
#define NR_POINT_LIGHTS 4

uniform DirLight u_dirLight;
uniform PointLight u_pointLights[NR_POINT_LIGHTS];
uniform int u_pointLightCount; // How many active lights?

uniform vec3 u_ambientColor; 

// --- FUNCTIONS ---

vec3 CalcDirLight(DirLight light, vec3 normal) {
    // Light direction (negate because we want direction FROM light TO fragment usually), 
    // but typically diff calculation wants FROM fragment TO light.
    // Let's standardise: light.direction is direction of rays. 
    // We need direction TO light source = -light.direction
    vec3 lightDir = normalize(-light.direction);
    
    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    
    // Combine results
    vec3 diffuse = diff * light.color * light.intensity;
    return diffuse;
}

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos) {
    vec3 lightDir = normalize(light.position - fragPos);
    
    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    
    // Attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));    
    
    vec3 diffuse = diff * light.color * light.intensity;
    
    return diffuse * attenuation;
}

void main() {
    // 1. Base Color
    vec4 objectColor = u_color;
    if (u_use_texture == 1) {
        objectColor = texture2D(u_texture, v_texcoord) * u_color;
    }

    vec3 norm = normalize(v_normal);
    vec3 result = vec3(0.0);

    // 2. Add Ambient
    result += u_ambientColor * objectColor.rgb;

    // 3. Add Directional Light
    result += CalcDirLight(u_dirLight, norm) * objectColor.rgb;

    // 4. Add Point Lights
    for(int i = 0; i < NR_POINT_LIGHTS; i++) {
        // GLSL 1.20 workaround: Loops must be unrolled or fixed size.
        // We iterate all and check count inside or just assume valid data if 0 intensity.
        if (i < u_pointLightCount) {
            result += CalcPointLight(u_pointLights[i], norm, v_frag_pos) * objectColor.rgb;
        }
    }

    gl_FragColor = vec4(result, objectColor.a);
}