// warp_burst.glsl — base16 · Estallido (CORONA x FUTURE x ULTRA)
// Ref. cliente pinterest5: explosión radial de partículas con estela (salto a hiperespacio), polvo
// de estrellas fino y brillo en el centro. Cada estela acelera hacia afuera y engorda al acercarse.
// Paleta del cliente por estela: 70% azul · 20% amarillo · 10% blanco (Accent / White la ajustan).
// u_surface: 0 = columnas (un estallido por tira) · 1 = techo: un solo estallido desde la corona, dibujado
// sobre los escalones reales del techo (carriles por brazo + onda cuadrada), ver burstTecho().
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_low;         // graves suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    vuelo de las partículas
uniform float u_swirl;       // 3 distorsión · 0–1    giro en espiral
uniform float u_accent;      // 4 color      · 0–1    fracción de estelas amarillas (0.2 = paleta)
uniform float u_count;       // 5 firma      · 0.1–1  cantidad de estelas

// extras
uniform float u_streak;      // 0.2–2  largo de las estelas
uniform float u_dust;        // 0–1    polvo de estrellas
uniform float u_white;       // 0–0.5  fracción de estelas blancas (0.1 = paleta)
uniform float u_panels;      // 1–16   tiras en el canvas (8 = booth)

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

// techo (booth_geo.techo): el LED es la corona (cuadro central, lo más bajo) + 3 escalones de barras en
// 4 brazos que suben hacia afuera. El estallido se dibuja en ese espacio: carriles rectos a lo largo de cada
// brazo (cruzan las barras de frente → la luz salta de escalón en escalón hacia afuera) + una onda cuadrada
// que sale de la corona. d = distancia cuadrada al centro: escalones en d ≈ 0.09–0.18 · 0.18–0.28 · 0.29–0.38.
vec3 burstTecho(vec2 uv, float e, float lo, float kick) {
    vec2 c = uv - 0.5;
    float d = max(abs(c.x), abs(c.y));
    bool sideX = abs(c.x) > abs(c.y);
    float arm = sideX ? (c.x > 0.0 ? 0.0 : 2.0) : (c.y > 0.0 ? 1.0 : 3.0);
    float tg = (sideX ? c.y : c.x) + u_swirl * d * 0.8;          // posición a lo ancho del brazo (+ giro)
    vec3 col = vec3(0.0);
    float density = clamp(u_count + kick * 0.3, 0.0, 1.0);
    for (int L = 0; L < 2; L++) {
        float fl = float(L);
        float g = (tg + 0.5) * (24.0 + 16.0 * fl);              // carriles a lo ancho del brazo
        float id = floor(g) + arm * 101.0;
        if (hash21(vec2(id, fl + 9.0)) > density) continue;
        float v = mix(0.25, 0.8, hash21(vec2(id, fl + 4.0)));
        float ph = fract(u_time * u_speed * v + hash21(vec2(id, fl + 1.0)));
        float rp = 0.04 + ph * ph * 0.4;                         // cabeza: de la corona al escalón exterior
        float len = (0.03 + 0.12 * ph) * u_streak * (0.8 + 0.4 * lo);
        float along = (d - (rp - len)) / len;                   // 0 cola · 1 cabeza
        if (along < 0.0 || along > 1.0) continue;
        float m = 1.0 - smoothstep(0.2, 0.32, abs(fract(g) - 0.5));   // carril ancho: se lee en el LED
        vec3 cc = pick(hash21(vec2(id, fl + 13.0)));
        col += cc * m * along * along * 1.5;
        col += mix(cc, u_color1, 0.5) * m * smoothstep(0.85, 1.0, along);
    }
    float wave = fract(u_time * u_speed * 0.5);                  // onda cuadrada desde la corona
    col += mix(u_color4, u_color1, 0.3) * exp(-abs(d - wave * 0.4) / 0.01) * (1.0 - wave) * (0.3 + 0.4 * e + 0.9 * kick);
    col += u_color4 * (1.0 - smoothstep(0.05, 0.062, d)) * (0.35 + 0.5 * e + 0.8 * kick);   // corona
    return col;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float lo = clamp(u_low, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    if (u_surface > 0.5) {
        vec3 tc = burstTecho(uv, e, lo, kick) * u_intensity * (0.8 + 0.3 * e);
        fragColor = TDOutputSwizzle(vec4(tonemap(tc, 1.3) + u_color3, 1.0));
        return;
    }

    // marco local: cada tira (columnas) o el cuadro completo (techo)
    float N = u_surface > 0.5 ? 1.0 : max(floor(u_panels + 0.5), 1.0);
    vec2 frame = vec2(u_res.x / N, u_res.y);
    vec2 p = (vec2(fract(uv.x * N), uv.y) - 0.5) * frame;   // px desde el centro
    float R = 0.5 * length(frame);
    float r = length(p) / R;                                 // 0 centro · 1 esquina
    float a = atan(p.y, p.x) + u_swirl * r * 2.5;            // espiral

    vec3 col = vec3(0.0);
    float density = clamp(u_count + kick * 0.3, 0.0, 1.0);
    for (int L = 0; L < 3; L++) {
        float fl = float(L);
        float bins = floor(80.0 + 90.0 * fl);
        float ai = (a / 6.28318 + 0.5) * bins;
        float id = floor(ai);
        float h = hash21(vec2(id, fl * 7.0 + 1.0));
        if (hash21(vec2(id, fl * 3.0 + 9.0)) > density) continue;
        float v = mix(0.25, 0.8, hash21(vec2(id, fl + 4.0))) * (0.6 + 0.25 * fl);
        float ph = fract(u_time * u_speed * v + h);
        float rp = ph * ph * 1.25;                          // acelera hacia afuera (perspectiva)
        float len = (0.03 + 0.35 * rp) * u_streak * (0.8 + 0.4 * lo);
        float along = (r - (rp - len)) / len;               // 0 cola · 1 cabeza
        if (along < 0.0 || along > 1.0) continue;
        float wPx = abs(fract(ai) - 0.5) * 6.28318 * r * R / bins;   // distancia lateral en px
        float th = mix(0.5, 3.0 + fl, rp);
        float m = 1.0 - smoothstep(th * 0.4, th, wPx);
        vec3 c = pick(hash21(vec2(id, fl + 13.0)));
        float b = along * along * (0.4 + rp) * (1.0 - smoothstep(1.0, 1.25, rp));
        col += c * m * b * 1.4;
        col += mix(c, u_color1, 0.5) * m * smoothstep(0.85, 1.0, along) * rp * 1.2;   // cabeza
    }

    // polvo de estrellas
    vec2 dg = (uv * u_res) / 6.0;
    vec2 did = floor(dg);
    float dh = hash21(did + 3.3);
    float tw = 0.5 + 0.5 * sin(u_time * 3.0 + dh * 40.0);
    float dot_ = (1.0 - smoothstep(0.6, 1.4, length((fract(dg) - 0.5) * 6.0))) * step(0.93, dh);
    col += mix(u_color4, u_color1, step(0.8, hash21(did))) * dot_ * tw * u_dust * 0.6;

    col += u_color4 * exp(-r * 9.0) * (0.25 + 0.5 * e + kick * 0.6);   // núcleo
    col *= u_intensity * (0.8 + 0.3 * e);
    col = tonemap(col, 1.3);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
