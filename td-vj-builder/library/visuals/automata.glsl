// automata.glsl: pinta el automata celular 1D como tejido de datos (recetarios 2 y 41; ref. Ryoji Ikeda "test pattern", raster-noton).
// sTD2DInputs[0] = estado (base54/red/out1, una celda por texel). Celdas con margen fino; la fila nueva arriba casi blanca,
// la historia se apaga al bajar. Los bajos encienden las filas recientes; el kick invierte una franja de 3 filas (no strobe).
// Abajo a la izquierda: los 8 bits de la regla activa, como lectura de instrumento.
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
uniform float u_warp;        // 3 distorsion: 0 celdas cuadradas / 1 lineas verticales (codigo de barras)
uniform float u_tono;
uniform float u_firma;       // 5 firma: regla (0-255)
uniform float u_variar;      // extra: la regla salta entre reglas buenas cada 8 kicks
out vec4 fragColor;
float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }

int reglaActual() {
    const int BUENAS[8] = int[8](30, 90, 110, 45, 150, 73, 105, 54);
    if (u_variar > 0.5) return BUENAS[int(mod(floor(max(u_step, 0.0) / 8.0), 8.0))];
    return int(clamp(floor(u_firma + 0.5), 0.0, 255.0));
}

void main() {
    vec2 uv = vUV.st;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    ivec2 sz = textureSize(sTD2DInputs[0], 0);
    vec2 gpos = uv * vec2(sz);
    ivec2 cel = clamp(ivec2(floor(gpos)), ivec2(0), sz - 1);
    vec2 f = fract(gpos);
    float on = texelFetch(sTD2DInputs[0], cel, 0).r;

    // franja invertida por el kick (3 filas, se apaga con la envolvente)
    float fila = float(cel.y);
    float y0 = floor(hash11(floor(u_step + 0.5) + 3.0) * float(sz.y - 3));
    float franja = step(y0, fila) * step(fila, y0 + 2.0);
    on = mix(on, 1.0 - on, franja * step(0.15, k));

    // margen fino: la celda no toca a sus vecinas
    float w = clamp(u_warp, 0.0, 1.0);
    float mx = mix(0.14, 0.32, w), my = mix(0.14, 0.0, w);
    float caja = step(mx, f.x) * step(f.x, 1.0 - mx) * step(my, f.y) * step(f.y, 1.0 - my);

    float edad = 1.0 - fila / float(sz.y - 1);                  // 0 arriba (nueva) / 1 abajo (vieja)
    float luz = mix(0.85, 0.12, pow(edad, 0.7));
    luz += 0.5 * lo * exp(-edad * 14.0);                        // los bajos encienden las filas recientes
    float nueva = step(float(sz.y - 1), fila);                  // la fila que se esta escribiendo
    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 col = mix(tinta, vec3(1.0), 0.45 * nueva + 0.15 * franja * k) * on * caja * luz;
    col *= 1.0 + 0.6 * franja * k;
    // ruido de bits sobre la fila nueva con los agudos
    col += tinta * nueva * caja * step(0.97, hash11(float(cel.x) + floor(u_time * 30.0) * 17.0)) * hi * 0.4;

    // lectura de la regla: 8 cuadritos abajo a la izquierda (bit 7 a bit 0)
    vec2 pp = gl_FragCoord.xy;
    vec2 o = vec2(24.0, 22.0);
    float lado = 9.0, paso = 13.0;
    vec2 lr = pp - o;
    if (lr.y >= -4.0 && lr.y < lado + 4.0 && lr.x >= -4.0 && lr.x < paso * 8.0 + 4.0) {
        col = vec3(0.0);                                        // placa negra detras de la lectura
        int bi = int(floor(lr.x / paso));
        vec2 lq = vec2(mod(lr.x, paso), lr.y);
        if (bi >= 0 && bi < 8 && lq.x < lado && lq.y >= 0.0 && lq.y < lado) {
            int bit = (reglaActual() >> (7 - bi)) & 1;
            bool marco = lq.x < 1.0 || lq.x >= lado - 1.0 || lq.y < 1.0 || lq.y >= lado - 1.0;
            col = tinta * (bit == 1 ? 0.75 : (marco ? 0.35 : 0.0));
        }
    }
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
