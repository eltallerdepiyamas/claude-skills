// dot_matrix.glsl — base8 · Matriz de puntos (CORONA x FUTURE x ULTRA)
// Retícula de puntos LED, como las barras de pixeles que rodean el centro del techo en el render.
// El campo se evalúa por punto (look LED): anillos desde el centro (en el techo caen sobre los
// escalones), barras que barren y chispas con los agudos. Mode 0 = automático (cambia solo cada
// ~16 s, sin operar). Puntos apagados quedan tenues: la matriz siempre se lee.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_high;        // agudos suavizados
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–3    anillos / barras
uniform float u_wave;        // 3 distorsión · 0–1    ondulación del campo
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_pitch;       // 5 firma      · 8–60   puntos por alto de pantalla

// extras
uniform float u_mode;        // 0–3   0 auto · 1 anillos · 2 barras · 3 chispas
uniform float u_size;        // 0.2–0.5 radio máximo del punto (fracción de celda)
uniform float u_sparkle;     // 0–1   chispas con los agudos (en todos los modos)

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float rings(vec2 c, float t, float e) {
    float r = max(abs(c.x), abs(c.y));             // cuadrados, como los escalones
    float w = 0.5 + 0.5 * sin(r * 22.0 - t * 3.0);
    return smoothstep(0.55 - 0.25 * e, 1.0, w);
}

float bars(vec2 c, float t, float e) {
    float h = smoothstep(0.7, 1.0, 0.5 + 0.5 * sin(c.y * 9.0 - t * 2.2));
    float v = smoothstep(0.85 - 0.2 * e, 1.0, 0.5 + 0.5 * sin(c.x * 5.0 + t * 1.4));
    return max(h, v);
}

float sparks(vec2 id, float t, float amt) {
    return step(1.0 - amt, hash21(id + floor(t * 9.0) * 17.3));
}

float field(int m, vec2 c, vec2 id, float t, float e, float hi) {
    if (m == 1) return rings(c, t, e);
    if (m == 2) return bars(c, t, e);
    return sparks(id, t, 0.02 + 0.15 * hi + 0.05 * e);
}

void main() {
    vec2 uv = vUV.st;
    float aspect = u_res.x / u_res.y;
    float e = clamp(u_bass, 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 1.5);
    float kick = clamp(u_kick, 0.0, 1.5);
    float t = u_time * u_speed;

    float pitch = max(floor(u_pitch + 0.5), 2.0);
    vec2 q = vec2(uv.x * aspect, uv.y) * pitch;
    vec2 id = floor(q);
    vec2 f = fract(q) - 0.5;
    vec2 c = ((id + 0.5) / pitch) - vec2(0.5 * aspect, 0.5);   // centro del punto, origen al centro
    c += u_wave * 0.04 * vec2(sin(c.y * 8.0 + t), sin(c.x * 6.0 - t * 0.8));

    // modo: 0 = automático con fundido entre modos cada 16 s
    float v;
    int m = int(clamp(floor(u_mode + 0.5), 0.0, 3.0));
    if (m == 0) {
        float cyc = u_time / 16.0;
        int a = int(mod(floor(cyc), 3.0)) + 1;
        int b = int(mod(floor(cyc) + 1.0, 3.0)) + 1;
        float k = smoothstep(0.85, 1.0, fract(cyc));
        v = mix(field(a, c, id, t, e, hi), field(b, c, id, t, e, hi), k);
    } else {
        v = field(m, c, id, t, e, hi);
    }
    v = max(v, sparks(id, t, u_sparkle * hi * 0.3));
    v *= 0.55 + 0.45 * e + 0.5 * kick;

    float aa = 1.5 * pitch / u_res.y;
    float rad = u_size * (0.45 + 0.55 * clamp(v, 0.0, 1.0));
    float dotOn = 1.0 - smoothstep(rad - aa, rad + aa, length(f));
    float dotOff = 1.0 - smoothstep(u_size * 0.45 - aa, u_size * 0.45 + aa, length(f));

    // acento: el color de marca se aplica tal cual (sin tonemap que lo deslave)
    vec3 lit = pick(hash21(id + 2.3));                      // cada punto elige color, como LED
    vec3 col = lit * dotOn * min(v, 1.0) + u_color4 * dotOff * 0.05;
    col *= u_intensity;
    col = min(col, vec3(1.0));
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
