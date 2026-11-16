// test_pattern.glsl: reticula de datos tipo test pattern (recetarios 1 y 3; ref. Ryoji Ikeda "test pattern" /
// "datamatics", Alva Noto "unitxt / univrs", raster-noton). Distinto del Barcode: aqui manda la reticula de 1 px.
// Una reticula de N columnas (Densidad, slot 5) con marcas de registro en los cruces; cada celda es un modulo de
// datos (cuadro, barras, bits, contador de 7 segmentos, mira circular) elegido por hash(celda + pagina).
// Kick: cambia la pagina de datos (u_step) y una sola fila se invierte un instante. Agudos: titileo de celdas.
// Bajos/medios/agudos: tres medidores con escala en el margen de abajo (el audio se lee). Un barrido vertical
// (velocidad) despierta las celdas que cruza. Arriba: regla y contador de cuadros.
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
uniform float u_warp;        // 3 distorsion: desfase de filas (shear digital)
uniform float u_tono;
uniform float u_firma;       // 5 firma: densidad (columnas de la reticula)
out vec4 fragColor;
#define PI 3.14159265

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash21(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float sdBox(vec2 p, vec2 b) { vec2 d = abs(p) - b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
float cubre(float d) { return 1.0 - smoothstep(-0.5, 0.5, d); }          // d en pixeles -> cobertura con antialias

// ---- 7 segmentos: bits a=1 b=2 c=4 d=8 e=16 f=32 g=64
int mascaraSeg(int d) {
    if (d == 0) return 63;
    if (d == 1) return 6;
    if (d == 2) return 91;
    if (d == 3) return 79;
    if (d == 4) return 102;
    if (d == 5) return 109;
    if (d == 6) return 125;
    if (d == 7) return 7;
    if (d == 8) return 127;
    return 111;
}
// q en pixeles relativo a la esquina inferior izquierda de la caja del digito (w x h)
float digito(vec2 q, float w, float h, int dg) {
    int m = mascaraSeg(dg);
    float th = max(1.0, w * 0.09);
    float d = 1e5;
    vec2 hh = vec2(w * 0.36, th);                  // segmentos horizontales
    vec2 vv = vec2(th, h * 0.22);                  // segmentos verticales
    if ((m & 1) != 0)  d = min(d, sdBox(q - vec2(w * 0.5, h * 0.95), hh));
    if ((m & 2) != 0)  d = min(d, sdBox(q - vec2(w * 0.88, h * 0.72), vv));
    if ((m & 4) != 0)  d = min(d, sdBox(q - vec2(w * 0.88, h * 0.28), vv));
    if ((m & 8) != 0)  d = min(d, sdBox(q - vec2(w * 0.5, h * 0.05), hh));
    if ((m & 16) != 0) d = min(d, sdBox(q - vec2(w * 0.12, h * 0.28), vv));
    if ((m & 32) != 0) d = min(d, sdBox(q - vec2(w * 0.12, h * 0.72), vv));
    if ((m & 64) != 0) d = min(d, sdBox(q - vec2(w * 0.5, h * 0.5), hh));
    return cubre(d);
}
// numero de 4 digitos en una caja (x0,y0) de ancho W y alto H, en pixeles
float numero4(vec2 px, vec2 o, float W, float H, float valor) {
    vec2 q = px - o;
    if (q.x < 0.0 || q.y < 0.0 || q.x > W || q.y > H) return 0.0;
    float dw = W / 4.0;
    int i = int(floor(q.x / dw));
    float pot = (i == 0) ? 1000.0 : ((i == 1) ? 100.0 : ((i == 2) ? 10.0 : 1.0));
    int dg = int(mod(floor(valor / pot), 10.0));
    return digito(vec2(q.x - float(i) * dw, q.y), dw * 0.82, H, dg);
}

void main() {
    vec2 px = vUV.st * u_res;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float mi = clamp(u_mid, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float golpe = smoothstep(0.6, 1.0, k);
    float t = u_time * u_speed;
    float pagina = floor(u_step + 0.5);
    float tick = floor(u_time * 15.0);
    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 acento = mix(tinta, vec3(1.0), 0.2);             // marcas: la misma tinta, apenas mas clara (una sola tinta)

    // ---- area de la reticula (margenes arriba/abajo para regla y medidores)
    float mx = floor(u_res.x * 0.05), myB = floor(u_res.y * 0.12), myT = floor(u_res.y * 0.08);
    float N = floor(clamp(u_firma, 8.0, 48.0));
    float cs = floor((u_res.x - 2.0 * mx) / N);
    float M = floor((u_res.y - myB - myT) / cs);
    vec2 o = vec2(floor((u_res.x - N * cs) * 0.5), myB + floor((u_res.y - myB - myT - M * cs) * 0.5));
    vec2 g = px - o;
    float fila = floor(g.y / cs);
    // shear digital: cada fila se corre segun la pagina (warp)
    g.x += floor((hash11(fila * 3.1 + pagina * 17.0) - 0.5) * u_warp * cs * 1.5);
    vec2 id = floor(g / cs);
    vec2 lp = g - id * cs;                                   // pixel dentro de la celda
    bool dentro = g.x >= 0.0 && g.y >= 0.0 && id.x < N && id.y < M;
    float val = 0.0, blanco = 0.0, acc = 0.0;

    if (dentro) {
        // lineas de 1 px de la reticula
        float dlx = min(lp.x, cs - lp.x), dly = min(lp.y, cs - lp.y);
        val += 0.10 * (cubre(dlx - 0.5) + cubre(dly - 0.5));
        // marcas de registro: cruz en cada 4o cruce
        vec2 cr = g - floor(g / (cs * 4.0) + 0.5) * cs * 4.0;
        float brazo = min(sdBox(cr, vec2(7.0, 0.5)), sdBox(cr, vec2(0.5, 7.0)));
        acc += 0.55 * cubre(brazo);

        float h = hash21(id + pagina * 17.31);
        float h2 = hash21(id * 1.7 + 9.1);
        vec2 c = lp - cs * 0.5;
        float mod1 = 0.0;
        if (h > 0.56 && h < 0.68) {                          // cuadro solido chico
            mod1 = cubre(sdBox(c, vec2(cs * 0.16))) * 0.6;
        } else if (h < 0.77 && h >= 0.68) {                  // barras finas (codigo)
            float sub = floor(lp.x / max(2.0, floor(cs / 18.0)));
            float barra = step(0.55, hash11(sub + h * 97.0 + pagina));
            mod1 = barra * cubre(abs(c.y) - cs * 0.3) * step(2.0, lp.x) * step(lp.x, cs - 2.0) * 0.45;
        } else if (h < 0.85 && h >= 0.77) {                  // contador de 7 segmentos
            float W = cs * 0.78, H = min(W / 4.0 * 1.6, cs * 0.45);
            float v = mod(floor(u_time * 30.0) + floor(h2 * 9000.0), 10000.0);
            mod1 = numero4(lp, vec2(cs * 0.11, (cs - H) * 0.5), W, H, v) * 0.7;
            blanco += mod1 * 0.35;
        } else if (h < 0.93 && h >= 0.85) {                  // 8 bits que cambian con el tiempo
            float bi = floor(lp.x / (cs / 8.0));
            float on = step(0.5, hash11(bi + h2 * 31.0 + floor(t * 4.0 + h2 * 8.0)));
            vec2 cb = vec2(mod(lp.x, cs / 8.0) - cs / 16.0, c.y);
            mod1 = on * cubre(sdBox(cb, vec2(cs / 16.0 - 2.0, cs * 0.05))) * 0.55;
        } else if (h >= 0.93) {                              // mira circular
            float r = length(c);
            float mira = min(abs(r - cs * 0.3) - 0.5, min(sdBox(c, vec2(cs * 0.42, 0.5)), sdBox(c, vec2(0.5, cs * 0.42))));
            acc += 0.5 * cubre(mira);
        }
        // titileo de celdas (agudos): unas pocas se encienden a 15 Hz
        float flick = step(hash21(id + tick * 1.37), 0.035 * hi) * cubre(sdBox(c, vec2(cs * 0.5 - 2.0)));
        // barrido: despierta las celdas que cruza
        float bx = fract(t * 0.08) * N;
        float barr = exp(-abs(id.x + 0.5 - bx) * 1.2);
        val += mod1 * (0.55 + 0.6 * barr) + flick * 0.3;
        // kick: una fila se invierte (solo la cresta del golpe)
        float filaK = floor(hash11(pagina * 7.7 + 1.0) * M);
        if (abs(id.y - filaK) < 0.5) val = mix(val, 0.45 - val * 0.8, golpe);
        // linea del barrido
        val += 0.35 * cubre(abs(g.x - bx * cs) - 0.5);
    }

    // ---- margen de abajo: medidores de bajos, medios y agudos con escala
    for (int i = 0; i < 3; i++) {
        float yy = myB * (0.25 + 0.2 * float(i));
        float nivel = (i == 0) ? lo : ((i == 1) ? mi : hi);
        float L = (u_res.x - 2.0 * mx) * 0.5 * clamp(nivel * 0.6, 0.0, 1.0);
        float barra = cubre(sdBox(px - vec2(mx + L * 0.5, yy), vec2(L * 0.5, 2.5)));
        val += barra * (0.35 + 0.2 * float(i == 0));
        // escala: ticks cada 1/16
        float xs = px.x - mx;
        float tk = mod(xs, (u_res.x - 2.0 * mx) * 0.5 / 16.0);
        float tic = cubre(abs(tk) - 0.5) * cubre(abs(px.y - yy + 6.0) - 2.0) * step(0.0, xs) * step(xs, (u_res.x - 2.0 * mx) * 0.5);
        val += tic * 0.18;
    }
    // ---- margen de arriba: regla + contador de cuadros
    float yt = u_res.y - myT * 0.55;
    float rx = px.x - o.x;
    float tickR = mod(rx, cs * 0.25);
    float largo = (mod(rx, cs) < 1.0) ? 9.0 : 4.0;
    val += 0.22 * cubre(min(tickR, cs * 0.25 - tickR) - 0.5) * cubre(abs(px.y - yt) - largo) * step(0.0, rx) * step(rx, N * cs);
    float cnt = numero4(px, vec2(mx, u_res.y - myT * 0.92), myT * 1.3, myT * 0.5, mod(floor(u_time * 30.0), 10000.0));
    val += cnt * 0.5;
    blanco += cnt * 0.3;
    float pg = numero4(px, vec2(u_res.x - mx - myT * 1.3, u_res.y - myT * 0.92), myT * 1.3, myT * 0.5, pagina);
    acc += pg * 0.5;

    val = clamp(val, 0.0, 1.0);
    vec3 col = tinta * val * 0.75 + acento * clamp(acc, 0.0, 1.0) * 0.45;
    col = mix(col, vec3(1.0) * max(val, acc) * 0.8, clamp(blanco, 0.0, 0.35));
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
