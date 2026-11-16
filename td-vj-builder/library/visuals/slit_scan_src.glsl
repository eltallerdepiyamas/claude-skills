// slit_scan_src.glsl: fuente en grises para Slit Scan: cintas de luz que ondulan con el bajo.
// Se guarda en un Texture 3D (64 cuadros) y el Time Machine la estira en el tiempo.
uniform float u_time;
uniform float u_low;
uniform float u_kick;
uniform float u_speed;
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    float t = u_time * max(u_speed, 0.05);
    float lo = clamp(u_low, 0.0, 2.0);
    float l = 0.0;
    for (int i = 0; i < 4; i++) {
        float fi = float(i);
        float y = 0.5 + (0.12 + 0.18 * lo) * sin(uv.x * (2.0 + fi * 1.3) + t * (0.6 + fi * 0.27) + fi * 1.9)
                      + 0.08 * sin(t * 0.31 + fi * 2.7);
        float grosor = 0.006 + 0.004 * fi + 0.02 * clamp(u_kick, 0.0, 1.0);
        float d = abs(uv.y - y);
        l += (1.0 - smoothstep(grosor * 0.4, grosor, d)) * (1.0 - fi * 0.18);
        l += 0.15 * exp(-d * 60.0);
    }
    // una hoja vertical que barre la pantalla
    float xb = fract(t * 0.07);
    l += 0.6 * (1.0 - smoothstep(0.0, 0.004, abs(uv.x - xb)));
    l = min(l, 1.5);
    fragColor = vec4(vec3(l), 1.0);
}
