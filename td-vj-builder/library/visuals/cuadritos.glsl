// cuadritos.glsl — base13 · Cuadritos (moodboard Mercado Ads, 2026-10-08)
// Retícula de cuadros blancos chicos que titilan (como los cuadritos del video). Cerca de cada persona
// los cuadros crecen y se vuelven amarillos; unos pocos destellan en lila. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600
uniform vec3  u_color2;      // lila      #AB86FF (acentos)
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo general
uniform float u_speed;       // 2 velocidad  · 0–3     titileo
uniform float u_jitter;      // 3 distorsión · 0–1     desorden: cuadros corridos y girados
uniform float u_warm;        // 4 color      · 0–1     cuánto se vuelven amarillos cerca de la gente
uniform float u_cell;        // 5 firma      · 0.1–0.6 tamaño de la celda (m)

// extras
uniform float u_radius;      // radio de influencia por persona (m)
uniform float u_density;     // fracción de cuadros encendidos lejos de la gente

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

    float cell = max(u_cell, 0.05);
    vec2 id = floor(q / cell);
    vec2 cc = (id + 0.5) * cell;
    float h = hash21(id), h2 = hash21(id + 17.3);

    // influencia de la gente en el centro de la celda
    float infl = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        float d = length(cc - P[i].xy * A);
        infl = max(infl, exp(-d * d / max(u_radius * u_radius * 0.5, 1e-3)));
    }

    float tw = 0.5 + 0.5 * sin(u_time * u_speed * (1.0 + 2.0 * h) + h * 40.0);
    float on = step(h2, u_density) * smoothstep(0.35, 1.0, tw);
    float sz = mix(0.12, 0.3, on) + 0.18 * infl;                    // fracción de la celda (medio lado)
    vec2 f = q - cc - (vec2(h, h2) - 0.5) * cell * 0.4 * u_jitter;
    float an = (h - 0.5) * 1.6 * u_jitter + infl * 0.785398 * u_jitter;
    f = mat2(cos(an), -sin(an), sin(an), cos(an)) * f;
    vec2 b = abs(f) - sz * cell;
    float sd = length(max(b, 0.0)) + min(max(b.x, b.y), 0.0);
    float sq = 1.0 - smoothstep(-px, px, sd);

    float bright = max(on * 0.75, infl);
    vec3 ink = mix(vec3(1.0), u_color1, clamp(infl * 1.4 * u_warm, 0.0, 1.0));
    float lila = step(0.985, hash21(id + floor(u_time * u_speed * 0.5))) * (1.0 - infl);
    ink = mix(ink, u_color2, lila);
    bright = max(bright, lila);

    vec3 col = u_color3 + u_color1 * 0.05 * smoothstep(0.7, 0.0, vUV.t);
    col = mix(col, ink * bright * u_intensity, sq * step(0.02, bright));
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, u_color1, marker(q - P[i].xy * A, px));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
