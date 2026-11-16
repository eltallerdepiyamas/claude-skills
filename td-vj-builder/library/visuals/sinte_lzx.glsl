// sinte_lzx.glsl: un patch de sintetizador de video LZX en un shader (recetarios 35-38 y 42, acabado CRT de la 43;
// ref. LZX Industries: Prismatic Ray / Stairs / Staircase / Keychain, Sandin Image Processor).
// Rampas (radial del sello + lineal rotada) -> 2 osciladores con FM -> multiplicador de 4 cuadrantes -> wavefolder
// (Stairs) + escalera (Staircase) -> keyer -> colorizer de una tinta + blanco en los nucleos -> sangrado horizontal,
// pasa altos y scanlines sutiles. Los osciladores van a tempo: cada kick salta la fase un cuarto de ciclo (u_step)
// y el bajo es el CV de la FM.
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
uniform float u_warp;        // 3 distorsion: profundidad de la FM / multiplicador
uniform float u_tono;
uniform float u_firma;       // 5 firma: pliegues del wavefolder (1 = casi seco, 8 = muchas bandas)
out vec4 fragColor;
#define PI 3.14159265
#define TAU 6.2831853
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }

float osc(float x) { return 0.5 + 0.5 * sin(TAU * x); }
float plegar(float x, float n) { return 1.0 - abs(1.0 - 2.0 * fract(x * n * 0.5)); }   // Stairs
float escalera(float x, float n) { return floor(x * n) / n; }                          // Staircase

// la senal del patch en un punto (patch es palabra reservada en GLSL 4) (0..1)
float senal(vec2 p, float t, float lo, float mi, float k, float paso) {
    // rampas
    float ang = 0.35 + t * 0.02 + paso * 0.5236;                // el kick gira la rampa 30 grados
    vec2 dir = vec2(cos(ang), sin(ang));
    float rLin = dot(p, dir) + 0.5;
    float rRad = length(p);                                     // rampa radial: los osciladores dan anillos
    // osciladores a tempo (fase en cuartos de ciclo por kick)
    float fase = paso * 0.25;
    float o2 = osc(rLin * 7.0 - t * 0.13 + fase * 0.5);
    float fm = (0.15 + 0.6 * clamp(u_warp, 0.0, 1.0)) * (0.5 + lo);
    float o1 = osc(rRad * 9.0 - t * 0.21 - fase + fm * (o2 - 0.5));
    // multiplicador de 4 cuadrantes (ring mod)
    float mult = clamp(0.5 + 2.0 * (o1 - 0.5) * (o2 - 0.5) * (1.0 + clamp(u_warp, 0.0, 1.0)), 0.0, 1.0);
    float x = mix(o1, mult, 0.55);
    // wavefolder + escalera; el medio desplaza la entrada (los pliegues caminan)
    float n = clamp(u_firma, 1.0, 8.0);
    float pl = plegar(x + 0.08 * mi, n);
    float es = escalera(pl, 5.0);
    float v = mix(pl, es, 0.35);
    // forma desde rampas (DSG): disco del sello como mascara suave
    float forma = smoothstep(0.44, 0.40, rRad);
    return v * mix(0.12, 1.0, forma) * (1.0 + 0.25 * k);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);

    // ruido de sincronia muy leve por linea (agudos)
    float linea = floor(uv.y * u_res.y);
    p.x += (hash11(linea * 0.37 + floor(u_time * 30.0)) - 0.5) * 0.0015 * hi;

    // sangrado horizontal: 5 tomas (ancho de banda analogico) + pasa altos (enhance)
    float dx = 1.6 / u_res.y;
    float s0 = senal(p, t, lo, mi, k, paso);
    float sb = (senal(p + vec2(-2.0 * dx, 0.0), t, lo, mi, k, paso) + senal(p + vec2(-dx, 0.0), t, lo, mi, k, paso)
              + senal(p + vec2(dx, 0.0), t, lo, mi, k, paso) + senal(p + vec2(2.0 * dx, 0.0), t, lo, mi, k, paso) + s0) / 5.0;
    float sig = mix(sb, s0, 0.4);
    sig = clamp(sig + 0.6 * (s0 - sb), 0.0, 1.2);

    // keyer + colorizer de una tinta: debajo del umbral es negro, arriba tinta, nucleos hacia blanco
    float umbral = 0.52 - 0.06 * lo;
    float k1 = smoothstep(umbral, umbral + 0.08, sig);
    float k2 = smoothstep(0.86, 1.0, sig);
    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 col = tinta * k1 * (0.25 + 0.45 * sig) + mix(tinta, vec3(1.0), 0.6) * k2 * 0.3;

    // CRT sutil: scanlines cada 2 lineas y vineta de tubo
    float scan = 0.88 + 0.12 * cos(uv.y * u_res.y * PI * 0.5);
    col *= scan;
    vec2 q = uv - 0.5;
    col *= 1.0 - 0.35 * dot(q, q) * 2.0;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
