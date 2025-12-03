#version 120

varying vec2 v_texcoord;

// Box Parameters
uniform vec4 u_color;       // R, G, B, A
uniform vec2 u_dimensions;  // Width, Height in pixels
uniform float u_radius;     // Corner radius in pixels

// Function to calculate Signed Distance Field for a rounded box
// p: current pixel position (relative to center)
// b: half-size of the box
// r: corner radius
float roundedBoxSDF(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + r;
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0)) - r;
}

void main() {
    // 1. Convert UVs (0..1) to Pixel Coordinates relative to center
    // If u_dimensions is (200, 100), coordinates go from (-100, -50) to (100, 50)
    vec2 pos = (v_texcoord - 0.5) * u_dimensions;
    
    // 2. Calculate Half-Size
    vec2 half_size = u_dimensions / 2.0;
    
    // 3. Calculate Distance
    float dist = roundedBoxSDF(pos, half_size, u_radius);
    
    // 4. Anti-Aliasing (Smooth edges)
    // If distance < 0, we are inside. If > 0, outside.
    // smoothstep creates a smooth transition between -1.0 and 1.0 pixel (soft edge)
    float alpha = 1.0 - smoothstep(0.0, 1.5, dist);
    
    // 5. Output Color
    // Apply object alpha * calculated shape alpha
    gl_FragColor = vec4(u_color.rgb, u_color.a * alpha);
    
    // Optimization: Discard fully transparent pixels
    if (gl_FragColor.a < 0.01) {
        discard;
    }
}
