// physarum.glsl: pinta la red de venas del Physarum (recetario 9; referente Sage Jenson / MUTEK "red de nodos organica").
// sTD2DInputs[0] = estado de la simulacion (base50/red/out1, 960x540, r = rastro). Venas finas en la tinta,
// nudos hacia blanco; el kick hace respirar la red (en la simulacion) y la ilumina un instante.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;
uniform float u_tono;
uniform float u_firma;       // 5 firma: ramificacion (la usa la simulacion)
out vec4 fragColor;

float rastro(vec2 uv) { return texture(sTD2DInputs[0], uv).r; }

void main() {
    vec2 uv = vUV.st;
    vec2 px = uTD2DInfos[0].res.xy;
    float asp = u_res.x / u_res.y;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);

    float tr = rastro(uv);
    float v = 1.0 - exp(-tr * 0.3);
    v = smoothstep(0.1, 1.0, v);                                   // el fondo queda negro
    float gx = rastro(uv + vec2(px.x, 0.0)) - rastro(uv - vec2(px.x, 0.0));
    float gy = rastro(uv + vec2(0.0, px.y)) - rastro(uv - vec2(0.0, px.y));
    float borde = clamp(length(vec2(gx, gy)) * 0.12, 0.0, 1.0);   // filo de la vena: se ve dibujada, no borrosa
    float nucleo = smoothstep(0.8, 1.0, v);

    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 col = tinta * (0.5 * v + 0.3 * borde) * (0.85 + 0.25 * lo + 0.6 * k)
             + mix(tinta, vec3(1.0), 0.6) * nucleo * (0.25 + 0.25 * hi);
    vec2 q = (uv - 0.5) * vec2(asp, 1.0);
    col *= 1.0 - 0.6 * smoothstep(0.35, 0.85, length(q));         // los bordes respiran en negro
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
