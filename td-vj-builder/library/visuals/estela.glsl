// estela.glsl — base8 · Estela (Mercado Libre)
// Cada persona PINTA el piso con luz amarilla; al envejecer, el trazo se vuelve azul ML y se
// desvanece. Pincel opcionalmente pixelado (look LED) y deriva suave del trazo.
// Usa FEEDBACK: sTD2DInputs[0] = salida anterior de este mismo GLSL (build_visual(feedback=True)).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo azul marino

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo del trazo nuevo
uniform float u_speed;       // 2 velocidad  · 0–1     qué tan rápido se desvanece la estela
uniform float u_drift;       // 3 distorsión · 0–1     deriva / humo del trazo
uniform float u_shift;       // 4 color      · 0–1     qué tan rápido pasa de amarillo a azul
uniform float u_width;       // 5 firma      · 0.1–1.5 grosor del pincel (m)

// extras
uniform float u_pixel;       // tamaño del píxel del pincel (m); 0 = pincel suave

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

void main() {
    vec2 A = aspectM();
    vec2 uv = vUV.st;
    vec2 q = uv * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    // estela anterior, con deriva suave (campo de ruido que cambia lento)
    vec2 n = vec2(noise(q * 0.8 + u_time * 0.1), noise(q * 0.8 + 5.0 - u_time * 0.1)) - 0.5;
    vec3 prev = texture(sTD2DInputs[0], uv + n * u_drift * 0.004).rgb;

    // envejecer: se apaga y vira de amarillo a azul
    // el rojo/verde que se pierde pasa a azul → amarillo vira a azul saturado (sin pasar por gris)
    vec3 pc = max(prev - u_color3, 0.0);                  // trabajar sobre el trazo, sin el fondo
    float k = u_shift * 0.06;
    vec2 lost = pc.rg * vec2(k, k * 0.55);
    pc.rg -= lost;
    pc.b += (lost.x + lost.y) * 0.9;
    pc *= 1.0 - (0.004 + u_speed * 0.05);
    pc = max(pc - 0.0015, 0.0);                           // que termine en negro, sin residuo
    pc = mix(pc, u_color2 * max(pc.b, max(pc.r, pc.g)), 0.02 * u_shift);   // tender al azul ML exacto

    // pincel: disco suave o bloques de píxel (se evalúa en el centro del bloque)
    vec2 sq = u_pixel > 0.01 ? (floor(q / u_pixel) + 0.5) * u_pixel : q;
    float rw = max(u_width, 0.02) * 0.5 * (1.0 + 0.2 * u_bass);
    float soft = u_pixel > 0.01 ? 1.5 * px : rw * 0.4;
    float stamp = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        float d = length(sq - P[i].xy * A);
        stamp = max(stamp, 1.0 - smoothstep(rw - soft, rw, d));
    }

    vec3 col = max(pc, u_color1 * stamp * u_intensity);
    col = min(col + u_color3, vec3(1.0));                 // fondo sumado (se resta al leer: no se acumula)
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
