// automata_sim.glsl: automata celular 1D con historia que baja (recetarios 2 y 41; ref. Ryoji Ikeda / Castle de LZX).
// La fila de arriba se calcula con la regla (0-255, bits de Wolfram) sobre la fila de arriba anterior; las demas
// bajan una fila. Solo avanza cuando cambia el tick (u_rate pasos por segundo). El kick siembra bits en una franja.
// Estado rgba32float por celda: r = viva (0/1) / g = ultimo tick / b = 0 / a = ultimo codigo de kick (Step mod 64).
uniform float u_time;
uniform float u_rate;        // pasos por segundo
uniform float u_regla;       // 0..255
uniform float u_variar;      // >0.5: la regla salta entre reglas buenas cada 8 kicks
uniform float u_step;        // contador de kicks
uniform float u_mut;         // probabilidad de mutacion por celda (agudos)
out vec4 fragColor;

ivec2 SZ;
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float viva(int x, int y) { return texelFetch(sTD2DInputs[0], ivec2((x + SZ.x) % SZ.x, y), 0).r; }

int reglaActual() {
    const int BUENAS[8] = int[8](30, 90, 110, 45, 150, 73, 105, 54);
    if (u_variar > 0.5) return BUENAS[int(mod(floor(max(u_step, 0.0) / 8.0), 8.0))];
    return int(clamp(floor(u_regla + 0.5), 0.0, 255.0));
}

void main() {
    SZ = textureSize(sTD2DInputs[0], 0);
    ivec2 ij = ivec2(gl_FragCoord.xy);
    vec4 c = texelFetch(sTD2DInputs[0], ij, 0);
    int arriba = SZ.y - 1;
    float tick = mod(floor(u_time * max(u_rate, 0.0)), 4096.0);
    bool avanza = abs(tick - c.g) > 0.5;
    float codigo = mod(floor(u_step + 0.5), 64.0);
    bool kick = abs(codigo - c.a) > 0.5;

    float cel = c.r;
    if (avanza) {
        if (ij.y < arriba) {
            cel = texelFetch(sTD2DInputs[0], ij + ivec2(0, 1), 0).r;      // la historia baja
        } else {
            int l = int(viva(ij.x - 1, arriba) > 0.5);
            int m = int(viva(ij.x, arriba) > 0.5);
            int d = int(viva(ij.x + 1, arriba) > 0.5);
            int idx = l * 4 + m * 2 + d;
            cel = float((reglaActual() >> idx) & 1);
            if (hash21(vec2(float(ij.x), tick * 1.618 + u_time)) < u_mut) cel = 1.0 - cel;
        }
    }
    // kick: siembra bits al azar en una franja de la fila de arriba
    if (kick && ij.y == arriba) {
        float x0 = hash21(vec2(codigo, 7.0)) * float(SZ.x);
        float dx = mod(float(ij.x) - x0 + float(SZ.x), float(SZ.x));
        if (dx < float(SZ.x) * 0.3) cel = step(0.5, hash21(vec2(float(ij.x), codigo * 3.1 + u_time)));
    }
    fragColor = vec4(cel, tick, 0.0, codigo);
}
