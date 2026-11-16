// moire.glsl: interferencia de dos familias de anillos finos (recetario 34; ref. raster-noton / Carsten Nicolai, rigor optico).
// Dos rejillas de anillos concentricos con centros apenas separados y frecuencias apenas distintas: donde coinciden
// (producto) salen las ondas gigantes del moire. Los bajos separan los centros y desfasan la segunda familia; el kick
// cambia la frecuencia base cada 4 golpes (salto de figura, mismo brillo: nada de strobe). Dentro del disco del sello.
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
uniform float u_warp;        // 3 distorsion: la segunda familia se achata (anillos -> elipses)
uniform float u_tono;
uniform float u_firma;       // 5 firma: diferencia de frecuencia entre familias
uniform float u_densidad;    // extra: anillos por unidad de alto (periodo en pantalla)
out vec4 fragColor;
#define PI 3.14159265
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// lineas antialiasadas: x en ciclos; ancho = fraccion del periodo; px = tamano de pixel en ciclos
float rejilla(float x, float ancho, float px) {
    float d = abs(fract(x + 0.5) - 0.5);                         // distancia al centro de la linea (ciclos)
    float l = smoothstep(ancho + px, ancho - px, d);
    return l * smoothstep(0.45, 0.2, px);                         // si el periodo baja de ~3 px se apaga (sin aliasing)
}

float familias(vec2 p, vec2 c1, vec2 c2, float f1, float f2, float fase2, float ach, float px, out float l1, out float l2) {
    float d1 = length(p - c1);
    vec2 q = rot(0.6) * (p - c2);
    q.x *= ach;
    float d2 = length(q);
    l1 = rejilla(d1 * f1, 0.17, px * f1);
    l2 = rejilla(d2 * f2 + fase2, 0.17, px * f2);
    return l1 * l2;
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

    // frecuencia base: cambia cada 4 kicks entre 4 valores cercanos
    float etapa = floor(max(u_step, 0.0) / 4.0);
    float f1 = clamp(u_densidad, 40.0, 260.0) * (1.0 + 0.06 * (mod(etapa, 4.0) - 1.5));
    float f2 = f1 * (1.0 + clamp(u_firma, 0.0, 0.2));
    // centros que derivan lento; el bajo los separa
    float sep = 0.012 + 0.05 * lo;
    vec2 dir = vec2(cos(t * 0.11), sin(t * 0.07));
    vec2 c1 = 0.03 * vec2(sin(t * 0.05), cos(t * 0.04)) - dir * sep;
    vec2 c2 = 0.03 * vec2(sin(t * 0.05), cos(t * 0.04)) + dir * sep;
    float fase2 = t * 0.15 + 0.6 * lo;
    float ach = 1.0 + 0.12 * clamp(u_warp, 0.0, 1.0);

    // supersampling 2x2
    float L1 = 0.0, L2 = 0.0, M = 0.0;
    for (int j = 0; j < 4; j++) {
        vec2 o = (vec2(float(j % 2), float(j / 2)) - 0.5) * 0.5 * px;
        float a, b;
        M += familias(p + o, c1, c2, f1, f2, fase2, ach, px, a, b);
        L1 += a; L2 += b;
    }
    L1 *= 0.25; L2 *= 0.25; M *= 0.25;

    vec3 tinta = mix(u_color1, u_color2, u_tono);
    float r = length(p);
    float disco = smoothstep(0.45, 0.43, r);
    // lineas sueltas muy tenues; la interferencia (producto) es la que se ve
    vec3 col = tinta * (0.07 * (L1 + L2)) + mix(tinta, vec3(1.0), 0.25 + 0.2 * k) * M * (0.75 + 0.3 * hi);
    col *= disco;
    col += tinta * 0.08 * smoothstep(1.5 * px, 0.0, abs(r - 0.455));   // canto del sello
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
