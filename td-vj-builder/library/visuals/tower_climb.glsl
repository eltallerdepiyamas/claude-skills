// tower_climb.glsl — base5 · Torre que sube (CORONA x FUTURE x ULTRA)
// De la referencia de la torre roja: un panel horizontal por nivel del andamio; los niveles
// se encienden en secuencia SUBIENDO, con estela abajo; en los picos (drop) se prende todo.
//  COLUMNAS (u_surface 0): cada columna es una torre; Skew desfasa las columnas alrededor del booth.
//  TECHO (u_surface 1): la subida continúa hacia el centro — anillos cuadrados completos del borde al centro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_kick;        // kick crudo
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–4    subida (niveles por segundo / 4)
uniform float u_skew;        // 3 distorsión · 0–1    desfase entre columnas (0 juntas · 1 espiral)
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_levels;      // 5 firma      · 4–16   niveles de la torre

// extras
uniform float u_trail;       // 0–1     largo de la estela
uniform float u_drop;        // 0.5–2   energía a partir de la cual se prende todo
uniform float u_panels;      // 1–16    columnas en el canvas (8 = booth)

uniform float u_white;       // 0–0.5  fracción blanca (0.1 = paleta)

out vec4 fragColor;

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

// paleta del cliente por elemento: White → blanco · Accent → amarillo · resto → azul
vec3 pick(float h) {
    if (h < u_white) return u_color1;
    if (h < u_white + u_accent) return u_color2;
    return u_color4;
}

vec3 tonemap(vec3 c, float k) {
    float m = max(c.r, max(c.g, c.b));
    return m > 1e-5 ? c * (1.0 - exp(-m * k)) / m : c;
}

void main() {
    vec2 uv = vUV.st;
    float e = clamp(u_bass, 0.0, 2.0);
    float kick = clamp(u_kick, 0.0, 1.5);
    float L = max(floor(u_levels + 0.5), 2.0);

    float idx, lev, across, along;    // índice de torre/cuadrante · nivel · posición en el panel
    if (u_surface < 0.5) {
        float N = max(floor(u_panels + 0.5), 1.0);
        idx = floor(uv.x * N) / N;
        float y = uv.y * L;
        lev = floor(y);
        across = fract(uv.x * N);                // 0..1 a lo ancho de la columna
        along = fract(y);                        // 0..1 dentro del nivel
    } else {
        vec2 c = uv - 0.5;
        float d = max(abs(c.x), abs(c.y)) / 0.5; // 0 centro · 1 borde
        float r = (1.0 - d) * L;                 // sube del borde (0) al centro (L)
        lev = floor(r);
        along = fract(r);
        idx = 0.0;                               // el anillo completo sube junto (sin cortes)
        across = 0.5;
    }

    float head = floor(fract(u_time * u_speed * 0.25 + idx * u_skew) * L);
    float dist = mod(head - lev + L, L);         // 0 = activo · 1 = el de abajo...
    float tail = max(u_trail * L * 0.35, 0.05);
    float isHead = step(dist, 0.5);
    float lit = isHead + (1.0 - isHead) * exp(-dist / tail) * 0.55;
    if (e > u_drop) lit = 1.0;                    // drop: toda la torre

    // panel horizontal dentro del nivel (con aire arriba/abajo y a los lados)
    float panel = step(0.3, along) * step(along, 0.7) * step(0.12, across) * step(across, 0.88);
    float glow = exp(-abs(along - 0.5) * 9.0) * 0.25;

    vec3 lc = pick(hash21(vec2(idx * 13.0, lev)));          // cada nivel de cada torre elige color
    vec3 col = lc * lit * (panel * (0.8 + 0.5 * kick) + glow);
    col *= u_intensity;
    col = tonemap(col, 1.4);
    fragColor = TDOutputSwizzle(vec4(col + u_color3, 1.0));
}
