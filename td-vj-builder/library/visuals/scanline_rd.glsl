// scanline_rd.glsl: reaccion-difusion por renglones (recetario 44; ref. Basement Vibes "Scanline Reaction Diffusion";
// automatas 1D de Simon Alexander-Adams). Un solo pase con feedback: la pantalla es una reticula de celdas de 6 px.
// En cada cuadro nace UN renglon nuevo en el centro, calculado solo del renglon anterior (activacion local menos
// inhibicion lateral, horizontal = "scanline") y del de dos generaciones atras (memoria: alterna y teje). La historia
// se aleja del centro hacia arriba y hacia abajo una celda por cuadro y se apaga: la pantalla se llena en ~3 s.
// Cada celda se dibuja como hilo: estado alto = hilo horizontal, bajo = hilo vertical -> textura de tejido.
// Patron (slot 5): radio de inhibicion + memoria: de rayas a tejido a laberinto. Warp: deriva lateral (diagonales).
// Kick: re-siembra el renglon con bits nuevos (una banda nueva en el tejido). Bajos: mas difusion (hilos mas largos).
// Agudos: ruido de mutacion.
// El estado vive en el pixel central de cada celda (color = tinta * estado * 0.6 fijo, se recupera con dot);
// Intensity solo escala los demas pixeles del hilo.
// sTD2DInputs[0] = cuadro anterior (feedback1).
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
uniform float u_warp;        // 3 distorsion: deriva lateral del kernel (diagonales)
uniform float u_tono;
uniform float u_firma;       // 5 firma: patron (0 rayas -> 1 laberinto/tejido)
out vec4 fragColor;
#define CELL 6
#define FADE 0.985

int COLS;
vec3 TINTA;
float GAN;

float hash21(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }

// estado (0..1) de la celda (cx, cy) en el cuadro anterior; cx con vuelta horizontal
float estado(int cx, int cy) {
    if (cx < 0) cx += COLS;
    if (cx >= COLS) cx -= COLS;
    ivec2 ij = ivec2(cx * CELL + CELL / 2, cy * CELL + CELL / 2);
    vec3 c = texelFetch(sTD2DInputs[0], ij, 0).rgb - u_color3;
    return clamp(dot(c, TINTA) / max(dot(TINTA, TINTA) * GAN, 1e-4), 0.0, 1.0);
}

void main() {
    ivec2 fc = ivec2(gl_FragCoord.xy);
    ivec2 SZ = min(textureSize(sTD2DInputs[0], 0), ivec2(u_res + 0.5));
    COLS = max(SZ.x / CELL, 1);
    int ROWS = max(SZ.y / CELL, 3);
    int cy0 = ROWS / 2;
    ivec2 cell = fc / CELL;
    ivec2 loc = fc - cell * CELL;
    TINTA = mix(u_color1, u_color2, u_tono);
    GAN = 0.6;                                   // ganancia FIJA del estado (Intensity no la toca: si no, el audio moveria el estado)
    float disp = 0.6 * clamp(u_intensity, 0.0, 2.0);
    float lo = clamp(max(u_bass, u_low), 0.0, 1.5);
    float hi = clamp(u_high, 0.0, 1.5);
    float k = clamp(u_kick, 0.0, 1.0);
    float golpe = smoothstep(0.6, 1.0, k);
    float t = u_time * u_speed;
    float paso = floor(u_step + 0.5);

    vec3 col = u_color3;
    if (cell.x >= COLS || cell.y >= ROWS) {
        col = u_color3;                                              // sobrante si la resolucion no es multiplo de 6
    } else if (cell.y > cy0) {                                       // historia que sube
        vec3 pv = texelFetch(sTD2DInputs[0], fc - ivec2(0, CELL), 0).rgb;
        col = u_color3 + (pv - u_color3) * FADE;
    } else if (cell.y < cy0) {                                       // historia que baja (espejo)
        vec3 pv = texelFetch(sTD2DInputs[0], fc + ivec2(0, CELL), 0).rgb;
        col = u_color3 + (pv - u_color3) * FADE;
    } else {
        // ---- renglon nuevo: activacion local - inhibicion lateral (solo horizontal) + memoria
        int cx = cell.x;
        float pat = clamp(u_firma, 0.0, 1.0);
        int ri = int(mix(3.0, 8.0, pat) + 0.5);
        int sh = int(floor(sin(t * 0.37) * clamp(u_warp, 0.0, 1.0) * 2.0 + 0.5));
        float A = 0.0, I = 0.0;
        for (int i = -8; i <= 8; i++) {
            if (i < -ri || i > ri) continue;
            float v = estado(cx + i + sh, cy0);
            I += v;
            if (i == 0) A += 0.5 * v;
            else if (i == 1 || i == -1) A += 0.25 * v;
        }
        I /= float(2 * ri + 1);
        A = mix(A, I, 0.3 * lo);                                     // bajos: mas difusion
        float b = estado(cx, cy0 + 1);                               // dos generaciones atras
        float mem = mix(0.15, 1.0, pat);
        float ruido = (hash21(vec2(float(cx), floor(u_time * 30.0))) - 0.5) * (0.15 + 0.35 * hi);
        float x = 0.5 + 5.0 * (A - I) - mem * (b - 0.5) + ruido;
        float s = smoothstep(0.1, 0.9, x);
        // kick: re-siembra con bits nuevos
        float sem = step(0.5, hash21(vec2(float(cx) * 1.7, paso * 31.0 + 5.0)));
        s = mix(s, sem, 0.85 * golpe);
        // ---- hilo: horizontal con el estado, vertical con su complemento; el pixel central guarda el estado
        bool centro = (loc.x == CELL / 2 && loc.y == CELL / 2);
        float hor = (loc.y == CELL / 2 && loc.x >= 1) ? s : 0.0;
        float ver = (loc.x == CELL / 2 && loc.y >= 1 && loc.y != CELL / 2) ? (1.0 - s) * 0.7 : 0.0;
        col = u_color3 + TINTA * (centro ? GAN * s : disp * max(hor, ver));
    }
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
