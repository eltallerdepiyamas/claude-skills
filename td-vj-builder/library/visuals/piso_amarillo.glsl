// piso_amarillo.glsl — base16 · Piso amarillo (moodboard / guía Mercado Ads, 2026-10-08)
// El amarillo protagonista (80% de la guía): todo el piso amarillo con una trama de puntos; cada persona
// abre un ECLIPSE negro con borde brillante que respira, y un anillo lila fino como acento. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600
uniform vec3  u_color2;      // lila      #AB86FF (acentos)
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–1.5   brillo del amarillo
uniform float u_speed;       // 2 velocidad  · 0–3     respiración del eclipse
uniform float u_wobble;      // 3 distorsión · 0–1     borde ondulado del eclipse
uniform float u_accent;      // 4 color      · 0–1     anillo lila alrededor del eclipse
uniform float u_hole;        // 5 firma      · 0.2–1.5 radio del eclipse (m)

// extras
uniform float u_dots;        // trama de puntos negros sobre el amarillo (0 = liso)
uniform float u_merge;       // cuánto se funden los eclipses de personas cercanas

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

    // amarillo con trama de puntos que se encoge cerca de la gente
    float g = 0.22;
    vec2 gid = floor(q / g);
    vec2 gf = q - (gid + 0.5) * g;

    // campo de eclipses: unión suave (smooth min) de discos por persona
    float sd = 1e9;
    float k = max(u_merge, 1e-3) * 0.6;
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 d = q - p.xy * A;
        float r = length(d);
        float ang = atan(d.y, d.x);
        float R = u_hole * (0.92 + 0.08 * sin(u_time * u_speed * 1.5 + p.w));
        R += u_wobble * 0.05 * sin(ang * 6.0 - u_time * u_speed + p.w);
        float s = r - R;
        float hh = clamp(0.5 + 0.5 * (sd - s) / k, 0.0, 1.0);
        sd = mix(sd, s, hh) - k * hh * (1.0 - hh);
    }

    float near = exp(-max(sd, 0.0) / 0.6);
    float dotR = g * 0.16 * u_dots * (1.0 - near);
    float dotm = 1.0 - smoothstep(dotR - px, dotR + px, length(gf));
    vec3 col = u_color1 * u_intensity * (1.0 - 0.85 * dotm);

    float hole = 1.0 - smoothstep(-1.5 * px, 1.5 * px, sd);
    float rim = exp(-abs(sd) / 0.05);                           // borde brillante del eclipse
    col = mix(col, u_color3, hole);
    col += mix(u_color1, vec3(1.0), 0.5) * rim * 0.6 * u_intensity;
    float lilaRing = (1.0 - smoothstep(0.012, 0.012 + 1.5 * px, abs(sd - 0.12))) * u_accent;
    col = mix(col, u_color2, lilaRing);

    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        col = mix(col, u_color1, marker(q - P[i].xy * A, px));
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
