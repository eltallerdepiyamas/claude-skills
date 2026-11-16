// celdas.glsl: celdas de Voronoi, solo bordes finos que respiran (recetario 33; ref. Inigo Quilez, voronoi y bordes;
// Andy Lomas / Max Cooper, crecimiento celular). Barato: busqueda 3x3, borde = dist2 - dist1 con antialias por fwidth.
// Nada de vitral: el interior de las celdas es negro, solo el borde (tinta) y un nucleo diminuto en cada semilla.
// Kick: cada semilla sortea una posicion nueva (Step) y viaja a ella mientras el kick cae: el tejido se reacomoda.
// Bajos: grosor y brillo de los bordes (respiran). Medios: tamano de los nucleos. Agudos: un contorno interior tenue.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_mid;
uniform float u_high;
uniform float u_kick;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: cuanto deambulan las semillas
uniform float u_tono;
uniform float u_firma;       // 5 firma: celdas (cantidad a lo alto de la pantalla)
out vec4 fragColor;
#define PI 3.14159265

vec2 hash22(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    float n = clamp(u_firma, 3.0, 24.0);
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5) * n;
    vec2 g = floor(p), f = fract(p);
    float viaje = smoothstep(0.0, 1.0, 1.0 - k);           // 0 al golpe -> 1 cuando el kick cae
    float vaga = 0.15 + 0.3 * clamp(u_warp, 0.0, 1.0);

    float dist1 = 8.0, dist2 = 8.0;
    vec2 rel1 = vec2(0.0);
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 b = vec2(float(i), float(j));
            vec2 c = g + b;
            vec2 h0 = hash22(c + (paso - 1.0) * 7.31);
            vec2 h1 = hash22(c + paso * 7.31);
            vec2 o = mix(h0, h1, viaje);
            // respiracion lenta de cada semilla (dentro de su celda)
            o = 0.5 + (o - 0.5) * (1.0 - vaga) + vaga * 0.5 * sin(t * vec2(0.37, 0.29) + 6.2831 * o);
            vec2 rr = b + o - f;
            float d = length(rr);
            if (d < dist1) { dist2 = dist1; dist1 = d; rel1 = rr; }
            else if (d < dist2) { dist2 = d; }
        }
    }
    float e = dist2 - dist1;
    float fw = max(fwidth(e), 1e-4);
    float grosor = 0.9 + 1.4 * lo;                          // los bajos engrosan
    float borde = 1.0 - smoothstep(0.0, fw * grosor, e);
    // contorno interior (agudos)
    float inter = (1.0 - smoothstep(0.0, fw * 0.8, abs(e - 0.14))) * 0.35 * clamp(hi, 0.0, 1.0);
    // nucleo de la semilla (medios)
    float ppu = u_res.y / n;                                // pixeles por unidad de celda
    float rn = (1.2 + 2.5 * clamp(mi, 0.0, 1.5)) / ppu;
    float nucleo = 1.0 - smoothstep(rn, rn + 1.2 / ppu, dist1);
    // brillo del borde por el golpe: corto
    float golpe = smoothstep(0.6, 1.0, k);

    float luz = borde * (0.38 + 0.3 * lo + 0.35 * golpe) + inter + nucleo * 0.5;
    vec2 v = uv - 0.5;
    float vin = 1.0 - 0.7 * dot(v * vec2(asp, 1.0), v * vec2(asp, 1.0)) * 1.6;
    vec3 col = tinta * luz * 0.7 + vec3(1.0) * nucleo * 0.18;
    col *= clamp(vin, 0.0, 1.0);
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
