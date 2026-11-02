// eclipse_field.glsl — base7 · Campo de eclipses (del video de referencia del cliente)
// Retícula de cuadros amarillos, cada uno con un círculo negro que se desliza despacio (como en el
// video). Las personas EMPUJAN los círculos fuera de su cuadro → a su alrededor se revela el amarillo.
// Un contorno lila fino marca dónde estaba cada círculo desplazado. Resplandor amarillo bajo la gente.
// Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // acento lila (del video del cliente)
uniform vec3  u_color3;      // fondo negro

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo general
uniform float u_speed;       // 2 velocidad  · 0–2     deriva de los círculos
uniform float u_push;        // 3 distorsión · 0–2     cuánto empujan las personas a los círculos
uniform float u_accent;      // 4 color      · 0–1     contorno lila (fantasma) de los círculos desplazados
uniform float u_tile;        // 5 firma      · 0.3–2.0 tamaño del cuadro (m)

// extras
uniform float u_radius;      // radio de influencia por persona (m)
uniform float u_gap;         // separación entre cuadros (fracción del cuadro)

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
float marker(vec2 d, float px) {
    float r = length(d);
    float ring = 1.0 - smoothstep(0.0, 1.5 * px, abs(r - 0.16) - 0.01);
    float core = 1.0 - smoothstep(0.05, 0.05 + 1.5 * px, r);
    float ticks = (1.0 - smoothstep(0.0, 1.5 * px, min(abs(d.x), abs(d.y)) - 0.005))
                * step(0.21, r) * step(r, 0.27);
    return max(max(ring, core), ticks);
}

float sdBox(vec2 p, float b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    float t = u_time * u_speed;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    float tile = max(u_tile, 0.1);
    vec2 g = q / tile;
    vec2 id = floor(g);
    vec2 f = fract(g) - 0.5;
    vec2 cq = (id + 0.5) * tile;
    float aa = px / tile * 1.5;
    float h = hash21(id);

    // deriva lateral lenta, como el círculo del video
    vec2 off = vec2(sin(t * 0.6 + h * 6.2831853) * 0.12, 0.0);

    // empuje: cada persona aleja el círculo de su posición (en unidades de cuadro)
    float R = max(u_radius, 0.1) * (1.0 + 0.1 * u_bass);
    vec2 push = vec2(0.0);
    float glow = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        vec2 v = cq - P[i].xy * A;
        float w = exp(-dot(v, v) / (R * R));
        push += v / (length(v) + 0.15 * tile) * w;
        vec2 dq = q - P[i].xy * A;
        glow += exp(-dot(dq, dq) / (R * R * 0.8));
    }
    float pl = length(push);
    if (pl > 1.0) push /= pl;                                      // como mucho, fuera del cuadro
    off += push * u_push * 0.95;

    // cuadro amarillo con círculo negro (recortado al cuadro)
    float half_ = 0.5 - max(u_gap, 0.0) * 0.5;
    float inSq = 1.0 - smoothstep(-aa, aa, sdBox(f, half_));
    float cr = half_ * 1.08;                                        // en reposo solo asoman las esquinas
    float inCi = 1.0 - smoothstep(-aa, aa, length(f - off) - cr);
    float act = smoothstep(0.0, 0.45, pl * u_push);                 // qué tanto se desplazó
    vec3 yellow = u_color1 * mix(0.28, 1.0, act);                   // tenue en reposo, pleno al revelarse
    vec3 col = u_color3 + u_color1 * 0.14 * glow;                   // resplandor bajo la gente
    col = mix(col, yellow, inSq * (1.0 - inCi));

    // fantasma lila: dónde estaba el círculo antes del empuje
    float moved = smoothstep(0.35, 0.6, pl * u_push);
    float ghost = 1.0 - smoothstep(0.0, aa, abs(length(f - vec2(off.x - push.x * u_push * 0.95, 0.0)) - cr) - 0.01);
    col = mix(col, u_color2, ghost * moved * u_accent * inSq * 0.8);

    fragColor = TDOutputSwizzle(vec4(col * u_intensity, 1.0));
}
