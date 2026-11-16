// slit_scan_mapa.glsl: mapa de tiempo del Time Machine (0 = ahora, 1 = lo mas viejo del cache).
// Distorsion 0: franjas verticales (cada columna es otro instante) · 1: desde el centro hacia arriba y abajo.
uniform float u_time;
uniform float u_warp;
uniform float u_retraso;     // firma: que tan atras llega el tiempo
uniform float u_kick;
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    float columnas = uv.x;
    float centro = abs(uv.y - 0.5) * 2.0;
    float m = mix(columnas, centro, clamp(u_warp, 0.0, 1.0));
    m += 0.05 * sin(uv.y * 20.0 + u_time) * u_warp;
    m = clamp(m, 0.0, 1.0) * u_retraso * (1.0 - 0.5 * clamp(u_kick, 0.0, 1.0));
    fragColor = vec4(vec3(m), 1.0);
}
