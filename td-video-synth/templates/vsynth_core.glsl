// vsynth_core.glsl — libreria de "modulos" de sintesis de video estilo LZX para GLSL TOP de TouchDesigner.
// Convencion: toda senal es float 0..1 (como 0-1 V de LZX). Rampas, osciladores, keys: todo intercambiable.
// Pegar arriba del shader (o cargar con un Text DAT y #include no existe en TD: concatenar en el builder).

#define TAU 6.28318530718

// ---------- RAMPAS (Cadet IV, Scrolls, Angles) ----------
float rampH(vec2 uv)                { return uv.x; }
float rampV(vec2 uv)                { return uv.y; }
// rampa a cualquier angulo (0..1 a lo largo de 'ang'), centrada
float rampAng(vec2 uv, float ang)   { vec2 d = vec2(cos(ang), sin(ang)); return dot(uv - 0.5, d) / 1.41421 + 0.5; }
float rampRadial(vec2 uv, float asp){ vec2 p = uv - 0.5; p.x *= asp; return clamp(length(p) * 1.41421, 0., 1.); }
float rampPolar(vec2 uv, float asp) { vec2 p = uv - 0.5; p.x *= asp; return atan(p.y, p.x) / TAU + 0.5; }
// scroll: desplaza una rampa en el tiempo (Scrolls)
float scroll(float r, float t)      { return fract(r + t); }

// ---------- OSCILADORES (Prismatic Ray, DWO3) ----------
float oscSin(float r, float f, float ph) { return 0.5 + 0.5 * sin(TAU * (r * f + ph)); }
float oscTri(float r, float f, float ph) { return abs(fract(r * f + ph) * 2. - 1.); }
float oscSaw(float r, float f, float ph) { return fract(r * f + ph); }
float oscSqr(float r, float f, float ph, float pw) { return step(pw, fract(r * f + ph)); }
// FM: otra senal suma a la fase
float oscFM(float r, float f, float ph, float mod, float depth) { return oscSin(r, f, ph + depth * (mod - 0.5)); }

// ---------- WAVESHAPERS (Stairs, Staircase, Arch, Doubler) ----------
float fold(float x, float n)        { return abs(fract(x * n * 0.5) * 2. - 1.); }      // wavefolder
float stairs(float x, float n)      { return floor(x * n) / max(n - 1., 1.); }          // escalera
float arch(float x, float k)        { return pow(clamp(x, 0., 1.), exp2(k)); }          // curva (k -2..2)
float doubler(float x)              { return abs(x * 2. - 1.); }                        // rectificador
float invert(float x)               { return 1. - x; }

// ---------- PROCESO / MEZCLA (Proc, Bridge, Factors, SMX3) ----------
float gainOff(float x, float g, float o) { return clamp((x - 0.5) * g + 0.5 + o, 0., 1.); }
float mul4q(float a, float b)       { return clamp(0.5 + 2. * (a - 0.5) * (b - 0.5), 0., 1.); } // cuatro cuadrantes
float mul2q(float a, float b)       { return a * b; }
float sumDist(float a, float b)     { return clamp(a + b - 0.5, 0., 1.); }
float diffAbs(float a, float b)     { return abs(a - b); }
float vmax(float a, float b)        { return max(a, b); }   // "non-additive mix" (NAM) LZX
float vmin(float a, float b)        { return min(a, b); }

// ---------- KEYERS (Keychain, Doorway, FKG3, Topogram) ----------
float keyHard(float x, float th)              { return step(th, x); }
float keySoft(float x, float th, float soft)  { return smoothstep(th - soft, th + soft, x); }
float keyWindow(float x, float lo, float hi, float soft) { return keySoft(x, lo, soft) * (1. - keySoft(x, hi, soft)); }
// Topogram: N bandas de nivel en cascada, devuelve 0..1 por banda
float topogram(float x, float n, float soft) {
    float acc = 0.;
    for (int i = 1; i < 16; i++) { if (float(i) >= n) break; acc += keySoft(x, float(i) / n, soft); }
    return acc / max(n - 1., 1.);
}

// ---------- FORMAS (DSG3, Shapechanger, Navigator) ----------
vec2  centered(vec2 uv, float asp)  { vec2 p = uv - 0.5; p.x *= asp; return p; }
vec2  rot2(vec2 p, float a)         { float c = cos(a), s = sin(a); return mat2(c, -s, s, c) * p; }
float shapeNorm(vec2 p, float pn)   { p = abs(p); return pow(pow(p.x, pn) + pow(p.y, pn), 1. / pn); } // 1 diamante, 2 circulo, >8 cuadro
vec2  perspective(vec2 p, float z)  { return p / (1. + z * p.y); }

// ---------- DIGITAL / LOGICA (Castle, Ribbons, Fortress) ----------
float quantBits(float x, float bits){ float n = exp2(bits) - 1.; return floor(x * n + 0.5) / n; }
float bitXor(float a, float b, float bits) { int n = int(exp2(bits)) - 1; return float((int(a * float(n)) ^ int(b * float(n))) & n) / float(n); }
float bitAnd(float a, float b, float bits) { int n = int(exp2(bits)) - 1; return float((int(a * float(n)) & int(b * float(n))) & n) / float(n); }
float bitOr (float a, float b, float bits) { int n = int(exp2(bits)) - 1; return float((int(a * float(n)) | int(b * float(n))) & n) / float(n); }
vec2  pixelate(vec2 uv, vec2 cells) { return (floor(uv * cells) + 0.5) / cells; }

// ---------- RUIDO (War of the Ants) ----------
float hash12(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * .1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float staticNoise(vec2 uv, vec2 res, float t) { return hash12(floor(uv * res) + floor(t * 60.) * 17.); }

// ---------- COLOR (colorizer del rig: SIEMPRE paleta, nunca HSB libre) ----------
// x = luma 0..1 -> negro -> c1 -> c2 -> blanco suave. c1/c2 vienen de los uniforms de paleta del rig.
vec3 colorize2(float x, vec3 bg, vec3 c1, vec3 c2, float cross) {
    vec3 col = mix(bg, c1, smoothstep(0.0, cross, x));
    col = mix(col, c2, smoothstep(cross, 1.0, x));
    return col;
}
// colorizer por bandas (Jones): cada banda de topogram toma una tinta de una tabla (Lookup TOP es mejor si son > 3)
