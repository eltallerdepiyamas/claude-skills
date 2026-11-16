// cortinas.glsl: capas de lineas verticales finas con paralaje; donde se cruzan sale moire.
// Cada capa es una cortina con una abertura que el kick abre (las capas de atras con retraso).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_mid;
uniform float u_high;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: ondulacion / inclinacion de las lineas
uniform float u_tono;
uniform float u_firma;       // 5 firma: densidad de lineas
out vec4 fragColor;

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    float t = u_time * u_speed;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 otro = mix(u_color2, u_color1, u_tono);
    vec3 col = vec3(0.0);

    for (int i = 0; i < 5; i++) {
        float fi = float(i);
        float prof = fi / 4.0;                              // 0 enfrente, 1 al fondo
        float dens = u_firma * (1.0 + prof * 0.37);
        float x = (uv.x - 0.5) * asp;
        x += t * 0.04 * (1.0 - prof * 0.7) * (mod(fi, 2.0) < 1.0 ? 1.0 : -1.0);
        x += u_warp * (0.04 * sin(uv.y * 6.0 + t * 0.5 + fi) + 0.08 * (uv.y - 0.5) * sin(fi * 1.3));
        float f = fract(x * dens);
        float ancho = fwidth(x * dens) * (1.0 + 0.6 * hi);
        float dist = 0.5 - abs(f - 0.5);                  // 0 sobre la linea
        float linea = 1.0 - smoothstep(ancho * 0.6, ancho * 1.6, dist);
        // abertura de la cortina: crece con el bajo, cada capa con su altura y retraso
        float centro = 0.5 + 0.25 * sin(t * 0.13 + fi * 2.0);
        float abre = 0.08 + 0.35 * clamp(lo * (1.0 - prof * 0.4) + mi * 0.2, 0.0, 1.2);
        float mascara = smoothstep(abre, abre - 0.05, abs(uv.y - centro));
        float panel = step(0.35, hash11(floor(x * 3.0) + fi * 11.0 + floor(t * 0.25)));
        float brillo = mix(1.0, 0.35, prof) * (0.15 + 0.85 * mascara) * (0.4 + 0.6 * panel);
        col += (mod(fi, 3.0) < 2.0 ? tono : otro * 0.8) * linea * brillo * 0.55;
    }
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
