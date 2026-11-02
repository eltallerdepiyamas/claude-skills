// kick_blocks.glsl — base11 · Bloques de golpe (CORONA x FUTURE x ULTRA)
// Pensado para las 8 columnas en Repartido. Cada kick (u_step) elige un patrón nuevo de bloques:
// columnas alternadas, mitades arriba/abajo, tablero, una sola columna, o todo en los picos.
// El brillo sigue la envolvente del kick (golpe → caída). Para drops.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;        // Energy (página Audio)
uniform float u_kick;        // kick crudo (envolvente)
uniform float u_step;        // paso (página Secuencia: kick o BPM)
uniform vec3  u_color1;      // blanco (10%)
uniform vec3  u_color2;      // amarillo Corona (20%)
uniform vec3  u_color3;      // fondo
uniform vec3  u_color4;      // azul (70%, dominante)
uniform float u_surface;     // 0 = columnas · 1 = techo (retícula cuadrada en todo el techo)

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo
uniform float u_speed;       // 2 velocidad  · 0–4    lamas internas que corren
uniform float u_split;       // 3 distorsión · 0–1    bloques partidos en lamas
uniform float u_accent;      // 4 color      · 0–1    fracción amarilla (0.2 = paleta 70/20/10)
uniform float u_density;     // 5 firma      · 0.1–1  fracción de bloques encendidos

// extras
uniform float u_panels;      // 1–16  columnas en el canvas (8 = booth)
uniform float u_rows;        // 1–8   divisiones verticales por columna
uniform float u_floor;       // 0–0.5 brillo mínimo entre golpes

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

void main() {
    vec2 uv = vUV.st;
    float N = u_surface > 0.5 ? max(floor(u_rows + 0.5), 4.0) : max(floor(u_panels + 0.5), 1.0);
    float R = u_surface > 0.5 ? N : max(floor(u_rows + 0.5), 1.0);
    float e = clamp(u_bass, 0.0, 2.0);
    float kick = clamp(u_kick, 0.0, 1.5);
    float s = floor(u_step);

    vec2 id = vec2(floor(uv.x * N), floor(uv.y * R));
    vec2 lu = vec2(fract(uv.x * N), fract(uv.y * R));
    float pat = floor(hash21(vec2(s, 4.2)) * 5.0);

    float on;
    if (pat < 1.0)      on = mod(id.x + s, 2.0);                               // alternadas
    else if (pat < 2.0) on = step(R * 0.5, id.y + 0.5) == mod(s, 2.0) ? 1.0 : 0.0;  // mitades
    else if (pat < 3.0) on = mod(id.x + id.y + s, 2.0);                        // tablero
    else if (pat < 4.0) on = float(id.x == mod(s * 3.0, N));                   // una columna
    else                on = step(1.0 - u_density, hash21(id + s * 7.1));      // aleatorio
    on *= step(hash21(id + s * 3.3), u_density + 0.25);                        // densidad
    if (e > 1.4) on = 1.0;                                                     // picos: todo

    // lamas internas que corren (Split)
    float slat = mix(1.0, step(0.45, fract(lu.y * 10.0 - u_time * u_speed)), u_split);
    // margen entre bloques
    vec2 m = min(lu, 1.0 - lu) * vec2(u_res.x / N, u_res.y / R);
    float gap = step(3.0, min(m.x, m.y));

    float level = u_floor + (1.0 - u_floor) * clamp(kick, 0.0, 1.0);
    vec3 col = pick(hash21(id + s * 1.7)) * on * slat * gap * level;   // cada bloque elige color
    col *= u_intensity;
    col = min(col, vec3(1.0));
    col += u_color3;
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
