// sdf_morph.glsl: isolineas de una forma SDF 2D que se transforma (recetario 22; ref. Inigo Quilez, distance
// functions 2D; Torin Blankensmith / Shader Park). Formas: circulo -> anillo -> cruz -> rombo (una por kick, Step).
// Se dibujan solo las curvas de nivel de la distancia (1 px con fwidth) que salen despacio de la forma y se apagan
// con la distancia: el negro manda. El contorno cero va mas brillante. Al kick la distancia pasa de la forma vieja a
// la nueva mientras el kick cae (morph) y un anillo de golpe recorre la distancia hacia afuera.
// Bajos: engrosan las lineas. Medios: la forma se redondea. Agudos: las isolineas lejanas titilan.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_mid;
uniform float u_high;
uniform float u_kick;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: ondulacion del espacio
uniform float u_tono;
uniform float u_firma;       // 5 firma: isolineas por unidad de distancia
out vec4 fragColor;
#define PI 3.14159265

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
float ndot(vec2 a, vec2 b) { return a.x * b.x - a.y * b.y; }

float sdCirculo(vec2 p, float r) { return length(p) - r; }
float sdAnillo(vec2 p, float r, float w) { return abs(length(p) - r) - w; }
float sdCruz(vec2 p, vec2 b) {                     // IQ sdCross (sin redondeo)
    p = abs(p);
    p = (p.y > p.x) ? p.yx : p.xy;
    vec2 q = p - b;
    float kk = max(q.y, q.x);
    vec2 w = (kk > 0.0) ? q : vec2(b.y - p.x, -kk);
    return sign(kk) * length(max(w, 0.0));
}
float sdRombo(vec2 p, vec2 b) {                    // IQ sdRhombus
    p = abs(p);
    float h = clamp(ndot(b - 2.0 * p, b) / dot(b, b), -1.0, 1.0);
    float d = length(p - 0.5 * b * vec2(1.0 - h, 1.0 + h));
    return d * sign(p.x * b.y + p.y * b.x - b.x * b.y);
}
float forma(vec2 p, int i, float s) {
    if (i == 0) return sdCirculo(p, s);
    if (i == 1) return sdAnillo(p, s * 0.95, s * 0.22);
    if (i == 2) return sdCruz(p, vec2(s * 1.05, s * 0.3));
    return sdRombo(p, vec2(s * 1.15, s * 1.15));
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float golpe = smoothstep(0.6, 1.0, k);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    // espacio: giro lento + ondulacion suave (warp)
    vec2 q = rot(t * 0.05) * p;
    float wa = clamp(u_warp, 0.0, 1.0) * 0.025;
    q += wa * vec2(sin(q.y * 9.0 + t * 0.7), sin(q.x * 9.0 - t * 0.6));

    // morph: forma del kick anterior -> forma nueva mientras el kick cae
    int i1 = int(mod(paso, 4.0));
    int i0 = int(mod(paso + 3.0, 4.0));
    float m = smoothstep(0.0, 1.0, 1.0 - k);
    float s = 0.2;
    float redondeo = 0.02 * clamp(mi, 0.0, 1.5);
    float d = mix(forma(q, i0, s), forma(q, i1, s), m) - redondeo;

    // isolineas: suben despacio desde la forma
    float N = clamp(u_firma, 4.0, 40.0);
    float x = d * N - t * 0.35;
    float fw = max(fwidth(x), 1e-4);
    float grosor = 0.9 + 1.8 * lo;                           // los bajos engrosan
    float iso = 1.0 - smoothstep(0.0, fw * grosor, abs(fract(x + 0.5) - 0.5));
    float idx = floor(x + 0.5);
    float tit = 1.0 - hi * 0.6 * step(0.5, hash11(idx * 3.7 + floor(u_time * 12.0))) * smoothstep(0.05, 0.25, abs(d));
    float caida = d > 0.0 ? exp(-d * 4.5) : exp(d * 9.0);   // afuera se apagan despacio, adentro rapido
    // contorno cero
    float f0 = max(fwidth(d), 1e-5);
    float cero = 1.0 - smoothstep(0.0, f0 * (1.4 + 1.8 * lo), abs(d));
    // anillo de golpe: recorre la distancia hacia afuera mientras el kick cae
    float frente = (1.0 - k) * 0.55;
    float onda = (1.0 - smoothstep(0.0, f0 * 2.5, abs(d - frente))) * smoothstep(0.05, 0.35, k) * exp(-frente * 3.0);

    float luz = iso * caida * tit * (0.42 + 0.3 * golpe) + cero * 0.75 + onda * 0.6;
    vec3 col = tinta * luz * 0.7 + vec3(1.0) * (cero * 0.22 + onda * 0.15);
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
