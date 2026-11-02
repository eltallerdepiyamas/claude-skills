// matrix_pulse.glsl — base6 · Matriz LED (Mercado Libre)
// El piso es una matriz de celdas. Cerca de cada persona las celdas crecen de punto a cuadro
// y pasan de azul a amarillo (blanco en el centro); ondas cuantizadas salen de cada persona
// y una línea de escaneo barre el piso. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2      brillo de la matriz
uniform float u_speed;       // 2 velocidad  · 0–3      ondas y escaneo
uniform float u_warp;        // 3 distorsión · 0–1      ruido que deforma el campo
uniform float u_mix;         // 4 color      · 0–1      rampa: más azul → más amarillo
uniform float u_cell;        // 5 firma      · 0.08–0.5 tamaño de celda (m)

// extras
uniform float u_radius;      // radio de influencia por persona (m)

// tracking (tdvj_core.build_tracking): xy = posición 0..1, z = activa, w = id
uniform vec2  u_floor_m;
uniform vec4  u_p0;
uniform vec4  u_p1;
uniform vec4  u_p2;
uniform vec4  u_p3;
uniform vec4  u_p4;
uniform vec4  u_p5;
uniform vec4  u_p6;
uniform vec4  u_p7;

out vec4 fragColor;

#define MAXP 8

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i),                 hash21(i + vec2(1.0, 0.0)), u.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}

// marcador de ubicación (anillo + punto + 4 ticks de mira), tipo FloorPresence
float marker0(vec2 d, float px) {
    float r = length(d);
    float ring = 1.0 - smoothstep(0.0, 1.5 * px, abs(r - 0.16) - 0.01);
    float core = 1.0 - smoothstep(0.05, 0.05 + 1.5 * px, r);
    float ticks = (1.0 - smoothstep(0.0, 1.5 * px, min(abs(d.x), abs(d.y)) - 0.005))
                * step(0.21, r) * step(r, 0.27);
    return max(max(ring, core), ticks);
}

float sdRoundBox(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + r;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0) - r;
}

// capa Figura (tdvj_core): si se elige una figura del moodboard, se oculta el marcador original
float marker(vec2 d, float px) { return marker0(d, px) * (1.0 - u_hide_marker); }

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    float cell = max(u_cell, 0.04);
    vec2 g = q / cell;
    vec2 f = fract(g) - 0.5;
    vec2 cq = (floor(g) + 0.5) * cell;                   // el campo se evalúa por celda → look LED
    vec2 w = vec2(noise(cq * 0.6 + u_time * 0.1), noise(cq * 0.6 + 7.3 - u_time * 0.1)) - 0.5;
    vec2 cw = cq + w * u_warp;

    float R = max(u_radius, 0.1);
    float t = u_time * u_speed;
    float field = 0.0;
    float ripple = 0.0;
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        float d = length(cw - p.xy * A);
        field += exp(-d * d / (R * R));
        ripple += smoothstep(0.85, 1.0, 0.5 + 0.5 * sin(d * 5.0 - t * 3.0 + p.w)) * exp(-d / (R * 3.5));
    }
    float scanX = mod(t * 1.2, A.x + 2.0) - 1.0;
    float scan = exp(-pow(cq.x - scanX, 2.0) / 0.02) * 0.25;
    float shimmer = noise(cq * 1.5 + u_time * 0.2) * 0.08;
    float v = clamp(field * 0.9 + ripple * 0.55 + scan + shimmer + 0.05 * u_bass, 0.0, 1.6);

    // forma: punto chico (v bajo) → cuadro redondeado (v alto)
    float vv = clamp(v, 0.0, 1.0);
    float half_ = mix(0.1, 0.42, vv);
    float sd = sdRoundBox(f, vec2(half_), mix(half_, 0.08, vv));
    float aa = px / cell * 1.5;
    float mask = 1.0 - smoothstep(-aa, aa, sd);

    float toY = smoothstep(0.85 - u_mix * 0.4, 1.1 - u_mix * 0.3, field);   // amarillo solo en el núcleo
    vec3 c = mix(u_color2, u_color1, toY);
    c = mix(c, vec3(1.0), smoothstep(1.1, 1.5, field + ripple * 0.3));
    vec3 col = u_color3 + c * mask * (0.18 + v) * u_intensity;

    // marcador encima de cada persona
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, vec3(1.0), marker(q - P[i].xy * A, px) * 0.9);   // blanco: se lee sobre azul y amarillo
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
