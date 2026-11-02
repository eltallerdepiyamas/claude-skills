// ondas.glsl — base14 · Ondas (moodboard Mercado Ads, 2026-10-08)
// Cada persona emite anillos amarillos con resplandor (como el halo del eclipse) que se expanden y se
// apagan. Donde se cruzan las ondas de dos personas brillan en lila. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600
uniform vec3  u_color2;      // lila      #AB86FF (acentos)
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo general
uniform float u_speed;       // 2 velocidad  · 0–3     velocidad de expansión
uniform float u_wobble;      // 3 distorsión · 0–1     anillos ondulados
uniform float u_accent;      // 4 color      · 0–1     lila donde se cruzan las ondas
uniform float u_spacing;     // 5 firma      · 0.2–1.5 separación entre anillos (m)

// extras
uniform float u_reach;       // alcance de las ondas (m)
uniform float u_thick;       // grosor del anillo (m)

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

    vec3 col = u_color3 + u_color1 * 0.04 * smoothstep(0.7, 0.0, vUV.t);
    float sum = 0.0, cnt = 0.0, glowSum = 0.0;
    float sp = max(u_spacing, 0.1);
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 d = q - p.xy * A;
        float r = length(d);
        float ang = atan(d.y, d.x);
        r += u_wobble * 0.06 * sin(ang * 5.0 + u_time * 1.3 + p.w) * smoothstep(0.0, 1.0, r);
        float ph = r / sp - u_time * u_speed * 0.6 - p.w * 0.37;
        float k = abs(fract(ph) - 0.5) * sp;                 // distancia al anillo más cercano (m)
        float fade = smoothstep(u_reach, 0.0, r) * smoothstep(0.0, 0.25, r);
        float ring = (1.0 - smoothstep(u_thick * 0.5, u_thick * 0.5 + 1.5 * px, k)) * fade;
        float glow = exp(-k / max(u_thick * 2.5, 1e-3)) * fade * 0.45;
        sum += ring;
        glowSum += glow;
        cnt += smoothstep(0.08, 0.2, glow);                 // cuántas ondas cubren este punto
    }
    float xover = smoothstep(1.5, 2.0, cnt) * u_accent;
    vec3 ink = mix(u_color1, u_color2, xover);
    col += u_color1 * glowSum * u_intensity;
    col = mix(col, ink * u_intensity, clamp(sum, 0.0, 1.0));
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, vec3(1.0), marker(q - P[i].xy * A, px));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
