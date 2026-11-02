// envios_network.glsl — base2 · Red de envíos (Mercado Libre)
// Cada persona es un nodo de ubicación. Las personas cercanas se conectan con rutas en L (calles)
// por donde viajan paquetes amarillos. Retícula de puntos que se ilumina cerca de la gente.
// Glitch de cortes horizontales opcional. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2   brillo de rutas y retícula
uniform float u_speed;       // 2 velocidad  · 0–3   velocidad de los paquetes
uniform float u_glitch;      // 3 distorsión · 0–1   glitch de cortes horizontales
uniform float u_mix;         // 4 color      · 0–1   rutas azul → amarillo
uniform float u_linkdist;    // 5 firma      · 1–8   distancia máx. de conexión (m)

// extras
uniform float u_packets;     // paquetes por ruta 1–8
uniform float u_grid;        // separación de la retícula de puntos (m)

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

float sdSeg(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
    return length(pa - ba * h);
}

float sdBox(vec2 p, float s) {
    vec2 d = abs(p) - s;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// capa Figura (tdvj_core): si se elige una figura del moodboard, se oculta el marcador original
float marker(vec2 d, float px) { return marker0(d, px) * (1.0 - u_hide_marker); }

void main() {
    vec2 A = aspectM();
    vec2 uv = vUV.st;

    // glitch: franjas horizontales desplazadas en saltos
    float band = floor(uv.y * 24.0);
    float gt = floor(u_time * 8.0);
    float gOn = step(1.0 - u_glitch * 0.35, hash21(vec2(band, gt)));
    uv.x += gOn * (hash21(vec2(band + 3.1, gt)) - 0.5) * 0.08 * u_glitch;

    vec2 q = uv * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    float near = 0.0;
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        vec2 d = q - P[i].xy * A;
        near += exp(-dot(d, d) / 1.2);
    }

    vec3 col = u_color3;

    // retícula de puntos (se enciende cerca de la gente)
    vec2 gf = fract(q / u_grid) - 0.5;
    float dotMask = 1.0 - smoothstep(0.04, 0.04 + 1.5 * px / u_grid, length(gf));
    col += u_color2 * dotMask * (0.10 + 0.55 * min(near, 1.5)) * u_intensity;

    // rutas en L entre personas cercanas + paquetes
    vec3 routeCol = mix(u_color2, u_color1, u_mix);
    int np = int(clamp(u_packets, 1.0, 8.0));
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        for (int j = i + 1; j < MAXP; j++) {
            if (P[j].z < 0.5) continue;
            vec2 a = P[i].xy * A;
            vec2 b = P[j].xy * A;
            float L = length(b - a);
            if (L > u_linkdist) continue;
            float fade = 1.0 - smoothstep(u_linkdist * 0.6, u_linkdist, L);
            vec2 m = vec2(b.x, a.y);                                   // esquina de la ruta
            float d = min(sdSeg(q, a, m), sdSeg(q, m, b));
            float line = 1.0 - smoothstep(0.01, 0.01 + 1.5 * px, d);
            float halo = exp(-d * d / 0.004) * 0.35;
            col += routeCol * (line * 0.8 + halo) * fade * u_intensity;

            float l1 = length(m - a);
            float l2 = length(b - m);
            float Lt = l1 + l2 + 1e-4;
            float seed = hash21(vec2(float(i), float(j)));
            for (int k = 0; k < 8; k++) {
                if (k >= np) break;
                float s = fract(u_time * u_speed * 0.6 / Lt + float(k) / float(np) + seed);
                if (seed > 0.5) s = 1.0 - s;                            // mitad de rutas en sentido contrario
                float dd = s * Lt;
                vec2 pp = dd < l1 ? mix(a, m, dd / max(l1, 1e-4)) : mix(m, b, (dd - l1) / max(l2, 1e-4));
                float pk = 1.0 - smoothstep(0.0, 1.5 * px, sdBox(q - pp, 0.035));
                col = mix(col, u_color1, pk * fade);
                col += u_color1 * exp(-dot(q - pp, q - pp) / 0.003) * 0.3 * fade;
            }
        }
    }

    // nodos: marcador + pulso que se expande
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 d = q - p.xy * A;
        float ph = fract(u_time * 0.6 + p.w * 0.37);
        float pr = (1.0 - smoothstep(0.0, 2.0 * px, abs(length(d) - ph * (0.9 + 0.3 * u_bass)) - 0.006)) * (1.0 - ph);
        col = mix(col, u_color1, marker(d, px));
        col += u_color1 * pr * 0.6;
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
