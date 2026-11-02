// splashes.glsl — base9 · Splashes (Mercado Libre)
// Cada persona "salpica" el piso a ritmo: impacto con borde irregular + anillo de choque azul
// con marcas de mira + corona de gotas amarillas que salen disparadas con estela de movimiento.
// Donde caen las gotas queda una MANCHA que envejece a azul ML y se desvanece.
// Usa FEEDBACK: sTD2DInputs[0] = salida anterior de este mismo GLSL (build_visual(feedback=True)).
// El alfa guarda qué fracción del píxel es mancha (lo demás es la salpicadura en vuelo, que NO debe
// quedarse pegada). El builder agrega glsl_opaque después, que pone alfa = 1 para la salida.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600  (gotas / manchas)
uniform vec3  u_color2;      // azul ML      #3483FA  (anillo / manchas viejas)
uniform vec3  u_color3;      // fondo azul marino

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2      brillo general
uniform float u_speed;       // 2 velocidad  · 0.1–3    salpicaduras por segundo (por persona)
uniform float u_spread;      // 3 distorsión · 0–1      caos: ángulos, distancias y borde irregular
uniform float u_mix;         // 4 color      · 0–1      proporción de salpicaduras azules (0 = todas amarillas)
uniform float u_size;        // 5 firma      · 0.4–3    alcance de la salpicadura (m)

// extras
uniform float u_persist;     // 0–1  cuánto duran las manchas en el piso (0 = no quedan)
uniform float u_drops;       // 4–16 gotas por salpicadura

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
#define MAXD  16
#define TAU   6.2831853

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

float hash11(float n) { return fract(sin(n * 127.1) * 43758.5453); }

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

// distancia a un segmento (estela de la gota)
float sdSeg(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
    return length(pa - ba * h);
}

void main() {
    vec2 A = aspectM();
    vec2 uv = vUV.st;
    vec2 q = uv * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    // manchas anteriores (sin el fondo): se apagan y viran de amarillo a azul
    vec4 prev = texture(sTD2DInputs[0], uv);
    vec3 pc = max(prev.rgb - u_color3, 0.0) * clamp(prev.a, 0.0, 1.0);
    vec2 lost = pc.rg * vec2(0.006, 0.0035);
    pc.rg -= lost;
    pc.b += (lost.x + lost.y) * 0.9;
    pc *= 1.0 - 0.08 * pow(0.02, clamp(u_persist, 0.0, 1.0));   // 0 ≈ 0.2 s · 1 ≈ 7 s
    pc = max(pc - 0.0015, 0.0);                           // que termine en negro, sin residuo

    float S = max(u_size, 0.1) * (1.0 + 0.2 * u_bass);
    float rate = max(u_speed, 0.05);
    int nd = int(clamp(u_drops, 4.0, float(MAXD)));

    vec3 live = vec3(0.0);                               // salpicadura en vuelo (no se acumula)
    vec3 stain = vec3(0.0);                              // lo que se pega al piso este cuadro

    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        vec2 c = P[i].xy * A;
        float id = P[i].w;

        // reloj de salpicadura por persona (desfasado por id)
        float ph = u_time * rate + hash11(id + 3.1);
        float a = fract(ph);                             // 0..1 dentro de la salpicadura
        float seed = floor(ph) * 7.13 + id * 31.7;
        float blue = step(hash11(seed + 0.5), u_mix);
        vec3 ink = mix(u_color1, u_color2, blue);

        vec2 d = q - c;
        float r = length(d);
        float ang = atan(d.y, d.x);

        // impacto: mancha central con borde irregular, aparece de golpe y se encoge
        float edge = noise(vec2(ang * 2.5, seed)) * 2.0 - 1.0;
        float rs = S * 0.22 * (1.0 + edge * 0.35 * u_spread) * (1.0 - smoothstep(0.0, 0.6, a));
        float splat = 1.0 - smoothstep(rs - 1.5 * px, rs + 1.5 * px, r);
        live = max(live, ink * splat);
        stain = max(stain, ink * splat * step(a, 0.08));            // el primer instante deja marca

        // anillo de choque + 4 marcas de mira (el toque "tech")
        float ra = S * (0.15 + 0.95 * (1.0 - pow(1.0 - a, 3.0)));
        float fade = 1.0 - a;
        float ring = 1.0 - smoothstep(0.0, 2.0 * px, abs(r - ra) - 0.012);
        float tk = (1.0 - smoothstep(0.0, 1.5 * px, min(abs(d.x), abs(d.y)) - 0.006))
                 * step(ra + 0.06, r) * step(r, ra + 0.2);
        live = max(live, u_color2 * (ring * 0.9 + tk * 0.7) * fade * fade);

        // marcador fijo de la persona (anillo fino + punto), siempre visible
        float mk = max(1.0 - smoothstep(0.0, 1.5 * px, abs(r - 0.14) - 0.008),
                       1.0 - smoothstep(0.04, 0.04 + 1.5 * px, r));
        live = max(live, u_color1 * mk * 0.9);

        // corona de gotas: vuelan, frenan y caen (a ≈ 0.55)
        float fly = 1.0 - pow(1.0 - clamp(a / 0.55, 0.0, 1.0), 2.5);
        float fly0 = 1.0 - pow(1.0 - clamp((a - 0.07) / 0.55, 0.0, 1.0), 2.5);
        for (int j = 0; j < MAXD; j++) {
            if (j >= nd) break;
            float fj = float(j);
            float h1 = hash11(seed + fj * 1.37);
            float h2 = hash11(seed + fj * 2.91 + 5.0);
            float th = TAU * (fj + 0.5 + (h1 - 0.5) * u_spread) / float(nd);
            vec2 dir = vec2(cos(th), sin(th));
            float dist = S * (0.45 + 0.55 * mix(0.8, h2, u_spread));
            float rad = S * mix(0.035, 0.08, hash11(seed + fj * 4.3)) * (1.0 - 0.4 * fly);
            vec2 p1 = c + dir * dist * fly;
            vec2 p0 = c + dir * dist * fly0;
            float dd = sdSeg(q, p0, p1);
            float drop = 1.0 - smoothstep(rad - 1.5 * px, rad + 1.5 * px, dd);
            float land = step(0.55, a) * step(a, 0.62);    // aterrizaje: deja mancha
            float inAir = 1.0 - smoothstep(0.55, 0.75, a);
            live = max(live, ink * drop * inAir);
            // la mancha es un poco más grande que la gota (se "aplasta" al caer)
            float blot = 1.0 - smoothstep(rad * 1.3 - 1.5 * px, rad * 1.3 + 1.5 * px, length(q - p1));
            stain = max(stain, ink * blot * land);
        }
    }

    float k = u_intensity;
    vec3 st = max(pc, min(stain, vec3(1.0)) * 0.9 * k);   // manchas persistentes
    vec3 col = max(st, min(live, vec3(1.0)) * k);         // salpicadura viva encima
    float ls = max(max(st.r, st.g), st.b);
    float lc = max(max(col.r, col.g), col.b);
    float frac = lc > 1e-4 ? clamp(ls / lc, 0.0, 1.0) : 1.0;   // parte del píxel que es mancha
    col = min(col + u_color3, vec3(1.0));                 // fondo sumado (se resta al leer: no se acumula)
    fragColor = TDOutputSwizzle(vec4(col, frac));
}
