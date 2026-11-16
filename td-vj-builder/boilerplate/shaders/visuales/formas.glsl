// formas.glsl — base1 · Formas (LITTLE JESUS · RIO SALVAJE)
// Filas de figuras solidas sobre crema (el flyer): circulos, cuadrados, triangulos y medios discos,
// y discos de vinil con su etiqueta verde/azul y franja blanca (la foto de los viniles).
// Paleta del album: amarillo, verde, azul, negro, rojo. Las filas se deslizan en sentidos alternos.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy: bandas activas, suavizadas (pagina Audio)

// paleta (los 5 viniles) y fondo
uniform vec3  u_c1;          // amarillo
uniform vec3  u_c2;          // verde (tambien mitad de arriba de la etiqueta)
uniform vec3  u_c3;          // azul  (tambien mitad de abajo de la etiqueta)
uniform vec3  u_c4;          // negro
uniform vec3  u_c5;          // rojo
uniform vec3  u_bg;          // crema del flyer

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0-1.5  tamano de las figuras + golpe de audio
uniform float u_speed;       // 2 velocidad  · 0-2    deslizamiento de las filas y giro
uniform float u_warp;        // 3 distorsion · 0-1    desorden: giro, desfase entre filas, vaiven
uniform float u_palette;     // 4 color      · 0-1    rota la paleta (cada figura pasa al siguiente color)
uniform float u_shapes;      // 5 firma      · 2-9    figuras por fila

// extras
uniform float u_vinyl;       // 0-1  cuantas figuras son discos de vinil
uniform float u_dark;        // 0-1  fondo crema -> negro

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

vec3 pal(float i) {
    i = mod(floor(i), 5.0);
    if (i < 0.5) return u_c1;
    if (i < 1.5) return u_c2;
    if (i < 2.5) return u_c3;
    if (i < 3.5) return u_c4;
    return u_c5;
}

float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

// triangulo equilatero de radio r
float sdTri(vec2 p, float r) {
    const float k = 1.7320508;
    p.x = abs(p.x) - r;
    p.y = p.y + r / k;
    if (p.x + k * p.y > 0.0) p = vec2(p.x - k * p.y, -k * p.x - p.y) / 2.0;
    p.x -= clamp(p.x, -2.0 * r, 0.0);
    return -length(p) * sign(p.y);
}

// medio disco (la parte de abajo)
float sdHalf(vec2 p, float r) {
    return max(length(p) - r, p.y);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = u_res.x / u_res.y;
    vec2 p = (uv - 0.5) * vec2(aspect, 1.0);    // alto = 1
    float px = 1.0 / u_res.y;
    float t = u_time * u_speed;
    float e = clamp(u_bass, 0.0, 2.0);

    // rejilla de filas: n figuras por alto de pantalla
    float n = max(u_shapes, 1.0);
    vec2 q = p * n;
    float row = floor(q.y);
    float dir = mod(row, 2.0) < 1.0 ? 1.0 : -1.0;
    float rh = hash21(vec2(row, 7.0));
    q.x += dir * t * (0.25 + 0.5 * rh) + u_warp * 0.6 * sin(t * 0.7 + row);

    vec2 cid = floor(q);
    vec2 lp = fract(q) - 0.5;                   // -0.5..0.5 dentro de la celda
    float h1 = hash21(cid);
    float h2 = hash21(cid + 13.1);
    float h3 = hash21(cid + 29.7);
    float h4 = hash21(cid + 41.3);

    // vaiven y giro (solo con Distorsion)
    lp += u_warp * 0.08 * vec2(sin(t * 1.3 + h1 * 6.28), cos(t * 1.1 + h2 * 6.28));
    float ang = (h3 - 0.5) * 6.28 * u_warp + t * (h4 - 0.5) * 2.0;
    vec2 rp = rot(ang) * lp;

    // tamano: Intensidad + golpe de audio en algunas figuras
    float s = mix(0.28, 0.44, h2) * u_intensity * (1.0 + 0.25 * e * step(0.6, h4));
    s = min(s, 0.47);                           // que no se salga de su celda

    vec3 bg = mix(u_bg, vec3(0.02), u_dark);
    vec3 col = bg;
    vec3 c = pal(h3 * 5.0 + u_palette * 5.0);
    float aa = px * n * 1.5;

    if (h1 < u_vinyl) {
        // disco de vinil: surcos + brillo que gira + etiqueta verde/azul con franja blanca
        float r = length(lp);
        float m = 1.0 - smoothstep(-aa, aa, r - s);
        vec3 vc = c * (0.9 + 0.1 * sin(r / (px * n) * 1.2));
        vc += 0.12 * pow(abs(cos(atan(rp.y, rp.x))), 12.0);
        float lab = 1.0 - smoothstep(-aa, aa, r - s * 0.38);
        vec3 lc = rp.y > 0.0 ? u_c2 : u_c3;
        float stripe = 1.0 - smoothstep(s * 0.03 - aa, s * 0.03 + aa, abs(rp.y));
        lc = mix(lc, vec3(0.97), stripe);
        lc = mix(lc, vec3(0.0), 1.0 - smoothstep(-aa, aa, r - s * 0.04));   // hoyo central
        vc = mix(vc, lc, lab);
        col = mix(col, vc, m);
    } else {
        float k = floor(h4 * 3.0);
        float d;
        if (k < 0.5)      d = sdBox(rp, vec2(s * 0.85));
        else if (k < 1.5) d = sdTri(rp, s * 0.95);
        else              d = sdHalf(rp, s);
        col = mix(col, c, 1.0 - smoothstep(-aa, aa, d));
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
