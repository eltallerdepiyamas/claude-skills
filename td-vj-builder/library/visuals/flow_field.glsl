// flow_field.glsl — base4 · Flujo (Mercado Libre)
// El piso es un flujo de líneas (rutas) que corre de lado a lado; cada persona es un obstáculo que el
// flujo RODEA (flujo potencial alrededor de un cilindro, superpuesto por persona). Las líneas se
// aprietan y se vuelven amarillas donde el flujo acelera; guiones viajan sobre ellas como paquetes.
// Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo negro
uniform float u_hide_marker; // 1 = ocultar el marcador por persona (página Figura)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo de las líneas
uniform float u_speed;       // 2 velocidad  · 0–3     avance de los guiones
uniform float u_turb;        // 3 distorsión · 0–1     turbulencia del flujo
uniform float u_mix;         // 4 color      · 0–1     cuánto amarillo en las zonas rápidas
uniform float u_density;     // 5 firma      · 2–30    líneas por metro

// extras
uniform float u_radius;      // radio del obstáculo por persona (m)
uniform float u_angle;       // dirección del flujo (grados)

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

vec2 cmul(vec2 a, vec2 b) { return vec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x); }
vec2 cinv(vec2 a) { return vec2(a.x, -a.y) / max(dot(a, a), 1e-6); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, s, -s, c); }

// capa Figura (tdvj_core): si se elige una figura del moodboard, se oculta el marcador original
float marker(vec2 d, float px) { return marker0(d, px) * (1.0 - u_hide_marker); }

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    float t = u_time * u_speed;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    mat2 R = rot(radians(u_angle));
    vec2 z = R * (q - A * 0.5);                               // coordenadas del flujo (x = corriente)
    float rad = max(u_radius, 0.05) * (1.0 + 0.1 * u_bass);
    float R2 = rad * rad;

    // potencial complejo W = z + Σ R² / (z - c)   →  φ = Re(W) (avance), ψ = Im(W) (líneas)
    vec2 W = z;
    vec2 dW = vec2(1.0, 0.0);                                  // dW/dz → velocidad
    float inside = 0.0;
    float ring = 0.0;
    float mk = 0.0;
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 c = R * (p.xy * A - A * 0.5);
        vec2 d = z - c;
        vec2 inv = cinv(d);
        W += R2 * inv;
        dW -= R2 * cmul(inv, inv);
        float r = length(d);
        inside = max(inside, 1.0 - smoothstep(rad * 0.97, rad, r));
        ring = max(ring, 1.0 - smoothstep(0.0, 1.5 * px, abs(r - rad) - 0.006));
        mk = max(mk, marker(q - p.xy * A, px));
    }

    // turbulencia suave
    vec2 n = vec2(noise(z * 0.7 + vec2(t * 0.2, 0.0)), noise(z * 0.7 + vec2(4.1, -t * 0.15))) - 0.5;
    float psi = W.y + n.x * u_turb * 0.6;
    float phi = W.x + n.y * u_turb * 0.6;
    float speed = length(dW);

    // líneas de flujo (isolíneas de ψ) con grosor constante en pantalla
    float k = max(u_density, 1.0);
    float sl = psi * k;
    float dl = abs(fract(sl + 0.5) - 0.5) / max(fwidth(sl), 1e-5);
    float lineM = 1.0 - smoothstep(0.6, 1.6, dl);

    // paquetes: segmentos cortos y brillantes que viajan sobre cada línea (fase = φ, desfasada por línea)
    float f = fract(phi * 1.2 - t * 0.6 + fract(floor(sl) * 0.618) * 3.0);
    float pk = smoothstep(0.0, 0.03, f) * (1.0 - smoothstep(0.10, 0.14, f));

    float fast = smoothstep(1.05, 1.6, speed);                // zonas donde el flujo acelera (a los lados)
    vec3 lc = mix(u_color2, u_color1, clamp(fast * u_mix * 1.6, 0.0, 1.0));
    vec3 col = u_color3;
    col += lc * lineM * (0.22 + 0.25 * fast + 1.1 * pk) * u_intensity;
    col += u_color1 * pk * lineM * fast * 0.5 * u_intensity;  // paquetes más calientes al acelerar

    // dentro del obstáculo: vacío + anillo + marcador
    col = mix(col, u_color3 + u_color1 * 0.04, inside);
    col = mix(col, u_color1, ring * 0.9);
    col = mix(col, u_color1, mk * inside);

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
