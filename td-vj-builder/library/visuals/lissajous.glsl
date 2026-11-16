// lissajous.glsl: figura de Lissajous en un osciloscopio XY con persistencia de fosforo (recetario 32; ref. tradicion
// "oscilloscope music", Jerobeam Fenderson; Robert Henke Lumiere para el trazo vector sobre negro).
// Distinto del Osciloscopio de CH10 (forma de onda) y del Armonografo (pendulos amortiguados): aqui una sola figura
// x = sin(a s + fase), y = sin(b s) que el haz recorre rapido. En cada cuadro solo se dibuja el tramo que el haz
// barrio en ese cuadro (36 segmentos); el feedback (fosforo) guarda el resto y la figura se ve completa, con la
// cabeza del haz mas brillante. Slot 5 = razon de frecuencias (tabla de razones limpias); cada kick avanza a la
// siguiente razon y la figura vieja se apaga en el fosforo mientras la nueva se dibuja.
// Bajos: tamano de la figura. Medios: la fase gira (la figura rota en 3D). Agudos: grano del haz.
// sTD2DInputs[0] = cuadro anterior (feedback1).
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
uniform float u_warp;        // 3 distorsion: desfase entre ejes
uniform float u_tono;
uniform float u_firma;       // 5 firma: razon de frecuencias (indice 0-7 en la tabla)
uniform float u_persist;     // extra: persistencia del fosforo por cuadro
out vec4 fragColor;
#define PI 3.14159265
#define TAU 6.2831853
#define SEG 36

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }

vec2 razon(int i) {
    if (i == 0) return vec2(1.0, 2.0);
    if (i == 1) return vec2(2.0, 3.0);
    if (i == 2) return vec2(3.0, 4.0);
    if (i == 3) return vec2(3.0, 5.0);
    if (i == 4) return vec2(4.0, 5.0);
    if (i == 5) return vec2(5.0, 6.0);
    if (i == 6) return vec2(5.0, 7.0);
    return vec2(2.0, 5.0);
}

float distSeg(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-9), 0.0, 1.0);
    return length(pa - ba * h);
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
    vec3 tinta = mix(u_color1, u_color2, u_tono);

    // ---- fosforo: el cuadro anterior se apaga (max, no suma: nunca satura)
    vec3 prev = texture(sTD2DInputs[0], uv).rgb;
    prev = max(prev * clamp(u_persist, 0.5, 0.985) - 0.002, 0.0);

    // ---- la figura
    int idx = int(mod(floor(u_firma + 0.5) + floor(u_step + 0.5), 8.0));
    vec2 ab = razon(idx);
    float fase = u_time * 0.25 * u_speed + clamp(u_warp, 0.0, 1.0) * 1.6 + 0.35 * mi;
    float R = 0.33 * (1.0 + 0.12 * lo);
    // el haz: recorre la figura 3 veces por segundo; este cuadro dibuja el ultimo tramo (con traslape)
    float sv = TAU * 3.0 * max(u_speed, 0.05);
    float s1 = TAU * fract(u_time * 3.0 * max(u_speed, 0.05));   // la figura es periodica en TAU: sin perder precision en shows largos
    float tramo = sv / 30.0 * 1.25;
    float ds = tramo / float(SEG);
    float s = s1 - tramo;
    vec2 a = R * vec2(sin(ab.x * s + fase), sin(ab.y * s));
    float dmin = 1e5, cabeza = 0.0;
    for (int i = 1; i <= SEG; i++) {
        s = s1 - tramo + float(i) * ds;
        vec2 b = R * vec2(sin(ab.x * s + fase), sin(ab.y * s));
        b += (vec2(hash11(s * 91.7), hash11(s * 37.3)) - 0.5) * 0.004 * hi;   // grano del haz
        float d = distSeg(p, a, b);
        if (d < dmin) { dmin = d; cabeza = float(i) / float(SEG); }
        a = b;
    }
    float px = 1.0 / u_res.y;
    float haz = 1.0 - smoothstep(px * 0.6, px * 1.8, dmin);
    float halo = exp(-dmin / (px * 5.0)) * 0.18;
    float nivel = (0.45 + 0.35 * cabeza + 0.35 * golpe) * clamp(u_intensity, 0.0, 2.0);
    vec3 trazo = tinta * (haz + halo) * nivel;
    trazo = mix(trazo, vec3(1.0) * haz * nivel, 0.28 * haz * cabeza);          // nucleo del haz casi blanco

    // reticula del osciloscopio, muy tenue (centro y bordes de la figura)
    float ret = (1.0 - smoothstep(0.0, px * 1.2, abs(p.x))) + (1.0 - smoothstep(0.0, px * 1.2, abs(p.y)));
    ret *= 0.035 * (1.0 - smoothstep(0.36, 0.42, max(abs(p.x), abs(p.y))));

    vec3 col = max(prev, trazo);
    col = clamp(col, 0.0, 1.0);
    // la salida ES la memoria del fosforo; la reticula entra con max: se queda fija en su nivel, no se acumula
    col = max(col, tinta * ret);
    fragColor = TDOutputSwizzle(vec4(max(col, u_color3), 1.0));
}
