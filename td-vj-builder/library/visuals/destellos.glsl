// destellos.glsl — base10 · Destellos (Mercado Libre)
// Piso de puntos LED que titilan tenues en azul. Alrededor de cada persona los puntos se encienden
// en amarillo/blanco. Cada persona = UN destello principal (estrella de 4 puntas) fijo sobre ella que
// late; alrededor, unos pocos destellos satélite chicos que brillan y se apagan (slider Satellites).
// Un barrido de brillo cruza el piso.
// Generativo puro, sin feedback.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600  (destellos cerca de la gente)
uniform vec3  u_color2;      // azul ML      #3483FA  (puntos lejanos)
uniform vec3  u_color3;      // fondo azul marino

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2      brillo general
uniform float u_speed;       // 2 velocidad  · 0–3      ritmo de titileo y de destellos
uniform float u_rays;        // 3 distorsión · 0–2      largo de los rayos de cada destello
uniform float u_warm;        // 4 color      · 0–1      núcleo del destello: amarillo → blanco
uniform float u_cell;        // 5 firma      · 0.12–0.6 separación de la retícula de puntos (m)

// extras
uniform float u_radius;      // 0.3–3  radio de influencia por persona (m)
uniform float u_ambient;     // 0–1    titileo de fondo lejos de la gente
uniform float u_sweep;       // 0–1    barrido diagonal de brillo
uniform float u_satellites;  // 0–6    destellos satélite por persona (0 = solo el principal)

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

#define MAXP  8
#define NSTAR 6

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

float hash11(float n) { return fract(sin(n * 127.1) * 43758.5453); }

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

// estrella de 4 puntas: cruz principal + diagonales más cortas + núcleo
float star(vec2 d, float size, float rays, float px) {
    float r = length(d) + 1e-4;
    float L = size * (0.6 + rays);                      // largo de los rayos
    float w = px * 1.2 + size * 0.02;
    vec2 a = abs(d);
    vec2 e = abs(vec2(d.x + d.y, d.x - d.y)) * 0.7071;
    float cross = (1.0 - smoothstep(0.0, w, min(a.x, a.y))) * pow(max(1.0 - r / L, 0.0), 2.0);
    float diag  = (1.0 - smoothstep(0.0, w * 0.7, min(e.x, e.y))) * pow(max(1.0 - r / (L * 0.45), 0.0), 2.0);
    float core  = exp(-r * r / (size * size * 0.02));
    float glow  = exp(-r / (size * 0.35)) * 0.35;
    return cross + diag * 0.6 + core + glow;
}

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    float t = u_time * u_speed;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);
    float R = max(u_radius, 0.1) * (1.0 + 0.25 * u_bass);

    // cercanía a la persona más próxima (0..1)
    float near = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        float d = length(q - P[i].xy * A);
        near = max(near, 1.0 - smoothstep(R * 0.3, R, d));
    }

    // barrido diagonal de brillo (cruza el piso cada ~6 s a velocidad 1)
    float diagPos = (q.x + q.y) / (A.x + A.y);
    float sw = fract(u_time * u_speed * 0.16);
    float sweep = exp(-pow((diagPos - (sw * 1.6 - 0.3)) / 0.04, 2.0)) * u_sweep;

    // retícula de puntos LED que titilan
    float cell = max(u_cell, 0.08);
    vec2 gi = floor(q / cell);
    vec2 gf = q - (gi + 0.5) * cell;
    float h = hash21(gi);
    float tw = pow(max(sin(t * (1.5 + 2.5 * h) + h * 40.0), 0.0), 12.0);   // parpadeo breve
    float lvl = mix(0.12 + 0.6 * tw * u_ambient, 0.35 + 1.2 * tw, near) + sweep * 1.5;
    float dotR = cell * mix(0.07, 0.14, near);
    float dotm = 1.0 - smoothstep(dotR - px, dotR + px, length(gf));
    vec3 dotCol = mix(u_color2, mix(u_color1, vec3(1.0), u_warm * tw), near);
    vec3 col = u_color3 + dotCol * dotm * lvl;

    // destellos en los puntos que parpadean fuerte (cruces pequeñas, pegadas a la retícula)
    float sm = star(gf, cell * 0.4, u_rays * 0.3, px) * tw * step(0.75, h) * (near * 0.5 + sweep * 2.0);
    col += mix(u_color1, vec3(1.0), u_warm) * sm * 0.5;

    int nsat = int(clamp(u_satellites + 0.5, 0.0, float(NSTAR)));
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        vec2 c = P[i].xy * A;
        float id = P[i].w;

        // destello principal: exacto sobre la persona, siempre encendido, late suave
        float beat = 0.8 + 0.2 * sin(t * 3.0 + id * 1.7);
        float main = star(q - c, cell * 3.2 * beat, u_rays, px) * 1.3;
        col += mix(u_color1, vec3(1.0), u_warm * smoothstep(0.0, 1.0, main)) * main;

        // satélites: chicos y tenues, aparecen, brillan y se apagan cerca de la persona
        for (int j = 0; j < NSTAR; j++) {
            if (j >= nsat) break;
            float fj = float(j);
            float ph = t * 0.9 + hash11(id * 7.1 + fj * 3.3);
            float life = fract(ph);
            float seed = floor(ph) * 13.7 + id * 5.3 + fj * 1.9;
            float ang = hash11(seed) * 6.2831853;
            float dist = R * (0.45 + 0.55 * sqrt(hash11(seed + 2.0)));
            // posición pegada a la retícula (look LED)
            vec2 sp = (floor((c + vec2(cos(ang), sin(ang)) * dist) / cell) + 0.5) * cell;
            float env = smoothstep(0.0, 0.06, life) * pow(1.0 - life, 2.5);   // golpe rápido + cola
            float size = cell * (0.8 + 0.6 * hash11(seed + 4.0));
            float st = star(q - sp, size, u_rays * 0.6, px) * env * 0.55;
            col += mix(u_color1, vec3(1.0), u_warm * smoothstep(0.0, 1.0, st)) * st;
        }
    }

    col = u_color3 + (col - u_color3) * u_intensity;
    fragColor = TDOutputSwizzle(vec4(min(col, vec3(1.0)), 1.0));
}
