// esferas.glsl — base15 · Esferas (moodboard Mercado Ads, 2026-10-08)
// Campo de esferas con degradado (amarillas, algunas lila) que flotan; las personas las EMPUJAN y las
// agrandan a su alrededor. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600
uniform vec3  u_color2;      // lila      #AB86FF (acentos)
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo general
uniform float u_speed;       // 2 velocidad  · 0–2     flotación
uniform float u_push;        // 3 distorsión · 0–2     cuánto empujan las personas
uniform float u_accent;      // 4 color      · 0–1     fracción de esferas lila
uniform float u_size;        // 5 firma      · 0.3–1.5 separación de la retícula (m)

// extras
uniform float u_radius;      // radio de influencia por persona (m)
uniform float u_grow;        // cuánto crecen cerca de la gente

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

// capa Figura (tdvj_core): si se elige una figura del moodboard, se oculta el marcador original
float marker(vec2 d, float px) { return marker0(d, px) * (1.0 - u_hide_marker); }

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    vec3 col = u_color3 + u_color1 * 0.05 * smoothstep(0.7, 0.0, vUV.t);
    float cell = max(u_size, 0.2);
    vec2 base = floor(q / cell);
    float best = 1e9;
    // 3x3 vecinos: una esfera empujada puede invadir la celda de al lado
    for (int j = -1; j <= 1; j++)
    for (int k = -1; k <= 1; k++) {
        vec2 id = base + vec2(float(k), float(j));
        float h = hash21(id), h2 = hash21(id + 9.1);
        vec2 c = (id + 0.5) * cell + (vec2(noise(id + u_time * u_speed * 0.2), noise(id + 31.0 - u_time * u_speed * 0.2)) - 0.5) * cell * 0.35;
        vec2 disp = vec2(0.0);
        float infl = 0.0;
        for (int i = 0; i < MAXP; i++) {
            if (P[i].z < 0.5) continue;
            vec2 v = c - P[i].xy * A;
            float d = length(v);
            float w = exp(-d * d / max(u_radius * u_radius * 0.5, 1e-3));
            disp += normalize(v + 1e-4) * w * u_push * cell * 0.5;
            infl = max(infl, w);
        }
        c += disp;
        float R = cell * (0.22 + 0.08 * h) * (1.0 + u_grow * infl);
        vec2 dq = q - c;
        float dl = length(dq);
        if (dl > R + 2.0 * px || dl > best) continue;
        best = dl;
        float m = 1.0 - smoothstep(R - 1.5 * px, R, dl);
        vec3 tint = h2 < u_accent * 0.35 ? u_color2 : u_color1;   // lila escaso (acento)
        float sh = smoothstep(R * 0.9, -R * 0.9, dq.x + dq.y * 0.3);
        vec3 sc = tint * mix(0.18, 1.0, sh) * (0.55 + 0.45 * infl);
        col = mix(col, sc * u_intensity, m);
    }
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, vec3(1.0), marker(q - P[i].xy * A, px));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
