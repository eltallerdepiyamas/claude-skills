// filotaxis.glsl: espiral de Vogel (filotaxis) con los primos marcados (recetario 30; ref. Max Cooper "Emergence", espiral de Sacks).
// Punto n en r = c * n^p, angulo = n * divergencia. Cada pixel busca el punto mas cercano en su banda de radio
// (sin trigonometria: distancia polar aproximada). Primos en la tinta, compuestos tenues. El kick lanza una onda que
// recorre los indices del centro hacia afuera y enciende otra parastichia (n = Step mod 34). Circular como el sello.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform float u_step;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: exponente del radio (0 = Vogel, 1 = mas denso al centro)
uniform float u_tono;
uniform float u_firma;       // 5 firma: angulo de divergencia en grados (137.508 = aureo)
out vec4 fragColor;
#define PI 3.14159265
#define NMAX 1400
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }

bool esPrimo(int n) {
    if (n < 2) return false;
    if (n < 4) return true;
    if (n % 2 == 0) return false;
    for (int q = 3; q < 40; q += 2) {
        if (q * q > n) break;
        if (n % q == 0) return false;
    }
    return true;
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float px = 1.0 / u_res.y;

    float R = 0.43 * (1.0 + 0.035 * lo);                     // el bajo respira el disco
    float pe = mix(0.5, 0.62, clamp(u_warp, 0.0, 1.0));
    float c = R / pow(float(NMAX), pe);
    float g = clamp(u_firma, 100.0, 180.0) / 360.0;          // vueltas por indice
    float r = length(p);
    float a01 = (atan(p.y, p.x) - t * 0.03) / (2.0 * PI);

    // banda de busqueda: solo los indices cuyo radio cae cerca de r
    float s = 0.0075;
    float nlo = pow(max(r - s, 0.0) / c, 1.0 / pe);
    float nhi = pow((r + s) / c, 1.0 / pe);
    int i0 = int(max(floor(nlo), 1.0));
    int i1 = int(min(ceil(nhi), float(NMAX)));
    float mejor = 1e9;
    int bn = -1;
    for (int it = 0; it < 200; it++) {
        int n = i0 + it;
        if (n > i1) break;
        float fn = float(n);
        float rn = c * pow(fn, pe);
        float da = fract(fn * g - a01 + 0.5) - 0.5;          // diferencia de angulo en vueltas
        float arco = da * 2.0 * PI * 0.5 * (r + rn);
        float d2 = (r - rn) * (r - rn) + arco * arco;
        if (d2 < mejor) { mejor = d2; bn = n; }
    }

    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 col = vec3(0.0);
    if (bn > 0) {
        float fb = float(bn);
        float d = sqrt(mejor);
        float tam = (1.4 + 1.6 * sqrt(fb / float(NMAX))) * px * (0.85 + 0.35 * lo);
        float punto = smoothstep(tam + px, tam - px, d);
        bool primo = esPrimo(bn);
        // onda del kick: el frente sale del centro (indice 0) y recorre los indices mientras el kick cae
        float frente = (1.0 - k) * float(NMAX) * 1.1;
        float onda = exp(-pow((fb - frente) / 70.0, 2.0)) * k;
        // parastichia encendida por el contador de kicks
        float brazo = (abs(mod(fb - floor(u_step + 0.5), 34.0)) < 0.5) ? 1.0 : 0.0;
        float chispa = primo ? step(0.93, hash11(fb + floor(u_time * 8.0) * 13.0)) * hi : 0.0;
        float luz = (primo ? 0.7 : 0.16) + 0.35 * brazo + 0.9 * onda + 0.4 * chispa;
        float blanco = clamp(0.5 * onda + 0.3 * chispa + (primo ? 0.1 : 0.0), 0.0, 0.7);
        col = mix(tinta, vec3(1.0), blanco) * punto * luz;
        col *= smoothstep(R + 0.01, R - 0.03, r);              // borde del disco suave
    }
    // canto fino del sello
    col += tinta * 0.1 * smoothstep(1.5 * px, 0.0, abs(r - R - 0.02));
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
