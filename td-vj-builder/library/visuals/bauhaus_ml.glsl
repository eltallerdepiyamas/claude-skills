// bauhaus_ml.glsl — base5 · Bauhaus ML (Mercado Libre, línea tech)
// Retícula de módulos Bauhaus (cuadro con círculo recortado, cuarto de círculo, medio círculo,
// círculo, triángulo). Lejos de la gente: plano técnico (solo contornos azules). Cerca de cada
// persona: los módulos se RELLENAN con la paleta ML y GIRAN 90°. Marcador de detección encima.
// Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo general
uniform float u_speed;       // 2 velocidad  · 0–2     giros espontáneos de los módulos
uniform float u_rotate;      // 3 distorsión · 0–1     giro al activarse: 0 = nada · ~0.4 = 90° · ~0.7+ = 180°
uniform float u_mix;         // 4 color      · 0–1     paleta: amarillo dominante → más azul/blanco
uniform float u_tile;        // 5 firma      · 0.3–2.0 tamaño del módulo (m)

// extras
uniform float u_radius;      // radio de activación por persona (m)
uniform float u_wire;        // brillo del plano técnico (contornos lejos de la gente)

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

float sdBox(vec2 p, float b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, s, -s, c); }

// forma Bauhaus por tipo, en coordenadas del módulo (-0.5..0.5)
float shape(int type, vec2 f) {
    float box = sdBox(f, 0.42);
    if (type == 0) return max(box, -(length(f - vec2(0.12, 0.12)) - 0.28));   // cuadro con círculo recortado
    if (type == 1) return max(length(f + 0.42) - 0.84, box);                    // cuarto de círculo
    if (type == 2) return max(length(f) - 0.42, f.y);                           // medio círculo
    if (type == 3) return length(f) - 0.36;                                     // círculo
    return max(box, f.x + f.y);                                                 // triángulo diagonal
}

// capa Figura (tdvj_core): si se elige una figura del moodboard, se oculta el marcador original
float marker(vec2 d, float px) { return marker0(d, px) * (1.0 - u_hide_marker); }

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

    // activación por módulo (se evalúa en el centro del módulo → cambia de a módulo entero)
    float R = max(u_radius, 0.1) * (1.0 + 0.1 * u_bass);
    float act = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        vec2 d = cq - P[i].xy * A;
        act += exp(-dot(d, d) / (R * R));
    }
    act = clamp(act, 0.0, 1.0);
    float fill = smoothstep(0.25, 0.6, act);

    // tipo, orientación y color del módulo
    float h = hash21(id);
    float h2 = hash21(id + 31.7);
    int type = int(floor(h * 5.0));
    float e = fract(t * 0.2 + h2 * 10.0);                              // giros espontáneos
    float quarter = floor(h2 * 4.0) + floor(t * 0.2 + h2 * 10.0) + smoothstep(0.85, 1.0, e);
    // al acercarse alguien gira en pasos exactos de 90° (sin quedarse a medio giro)
    quarter += floor(u_rotate * 2.999) * smoothstep(0.47, 0.53, act);
    vec2 fr = rot(quarter * 1.5707963) * f;

    float sd = shape(type, fr);
    float inShape = 1.0 - smoothstep(-aa, aa, sd);
    float outline = 1.0 - smoothstep(0.0, aa, abs(sd) - 0.012);

    float pick = hash21(id + 7.3);
    vec3 fc = pick < 0.65 - u_mix * 0.4 ? u_color1 : (pick < 0.92 - u_mix * 0.1 ? u_color2 : vec3(1.0));

    // retícula del plano técnico
    vec2 gl = abs(f);
    float grid = 1.0 - smoothstep(0.0, aa, 0.5 - max(gl.x, gl.y) - 0.004);

    vec3 col = u_color3;
    col += u_color2 * grid * 0.12 * u_wire * 2.0;
    col += u_color2 * outline * u_wire * (1.0 - fill);                 // lejos: contorno azul
    col = mix(col, fc, inShape * fill);                                // cerca: relleno ML
    col += fc * outline * fill * 0.25;                                 // filo brillante al activarse
    col *= u_intensity;

    // marcador de detección sobre cada persona (blanco: se lee sobre amarillo y azul)
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, vec3(1.0), marker(q - P[i].xy * A, px) * 0.9);
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
