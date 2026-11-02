// hud_detection.glsl — base3 · HUD de detección (Mercado Libre)
// El piso como pantalla de visión por computadora: caja de detección con corchetes y etiqueta
// tipo código de barras por persona, guías CAD con regla hasta los bordes, líneas de distancia
// entre personas cercanas y un barrido de radar que "hace ping" al pasar por cada persona.
// Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo ML  #FFE600
uniform vec3  u_color2;      // azul ML      #3483FA
uniform vec3  u_color3;      // fondo azul marino

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2     brillo de retícula, guías y radar
uniform float u_speed;       // 2 velocidad  · 0–3     radar, guiones y jitter
uniform float u_jitter;      // 3 distorsión · 0–1     inestabilidad de la detección (cajas tiemblan)
uniform float u_mix;         // 4 color      · 0–1     guías azul → amarillo
uniform float u_boxsize;     // 5 firma      · 0.4–2.0 tamaño de la caja de detección (m)

// extras
uniform float u_linkdist;    // distancia máx. para líneas de medición entre personas (m)
uniform float u_grid;        // separación de la retícula (m)

// tracking (tdvj_core.build_tracking): xy = posición 0..1, z = activa, w = id
uniform vec2  u_floor_m;
uniform vec4  u_p0;
uniform vec4  u_p1;
uniform vec4  u_p2;
uniform vec4  u_p3;
uniform vec4  u_p4;
uniform vec4  u_p5;
uniform vec4  u_p6;
uniform vec4  u_p7;

out vec4 fragColor;

#define MAXP 8

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i),                 hash21(i + vec2(1.0, 0.0)), u.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}

// marcador de ubicación (anillo + punto + 4 ticks de mira), tipo FloorPresence
float marker(vec2 d, float px) {
    float r = length(d);
    float ring = 1.0 - smoothstep(0.0, 1.5 * px, abs(r - 0.16) - 0.01);
    float core = 1.0 - smoothstep(0.05, 0.05 + 1.5 * px, r);
    float ticks = (1.0 - smoothstep(0.0, 1.5 * px, min(abs(d.x), abs(d.y)) - 0.005))
                * step(0.21, r) * step(r, 0.27);
    return max(max(ring, core), ticks);
}

float line(float d, float w, float px) { return 1.0 - smoothstep(w, w + 1.5 * px, d); }

float sdRect(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

float sdSeg(vec2 p, vec2 a, vec2 b, out float h) {
    vec2 pa = p - a, ba = b - a;
    h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-6), 0.0, 1.0);
    return length(pa - ba * h);
}

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    float t = u_time * u_speed;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);
    vec3 guide = mix(u_color2, u_color1, u_mix);

    vec3 col = u_color3;

    // retícula menor / mayor + marco del piso
    vec2 gd  = abs(fract(q / u_grid - 0.5) - 0.5) * u_grid;
    vec2 gd4 = abs(fract(q / (u_grid * 4.0) - 0.5) - 0.5) * u_grid * 4.0;
    col += u_color2 * (line(min(gd.x, gd.y), 0.0012, px) * 0.10
                     + line(min(gd4.x, gd4.y), 0.0025, px) * 0.18) * u_intensity;
    vec2 e = min(q, A - q);
    col += u_color2 * line(min(e.x, e.y), 0.006, px) * 0.5 * u_intensity;

    // radar desde el centro del piso
    vec2 ctr = A * 0.5;
    vec2 rv = q - ctr;
    float rr = length(rv);
    float sweepA = mod(t * 0.8, 6.2831853) - 3.1415927;
    float dA = mod(sweepA - atan(rv.y, rv.x), 6.2831853);          // 0 = línea del barrido, crece hacia atrás
    col += u_color2 * (exp(-dA * 4.0) * 0.16
                     + line(min(dA, 6.2831853 - dA) * rr, 0.003, px) * 0.45) * u_intensity;
    col += u_color2 * line(abs(fract(rr - 0.5) - 0.5), 0.0012, px) * 0.08 * u_intensity;

    // líneas de medición entre personas cercanas (guiones + regla cada 0.5 m + rombo al centro)
    for (int i = 0; i < MAXP; i++) {
        if (P[i].z < 0.5) continue;
        for (int j = i + 1; j < MAXP; j++) {
            if (P[j].z < 0.5) continue;
            vec2 a = P[i].xy * A;
            vec2 b = P[j].xy * A;
            float L = length(b - a);
            if (L > u_linkdist) continue;
            float fade = 1.0 - smoothstep(u_linkdist * 0.6, u_linkdist, L);
            float h;
            float d = sdSeg(q, a, b, h);
            float s = h * L;
            float dash = step(0.5, fract(s / 0.12 - t * 0.5));
            float ticks = line(abs(fract(s / 0.5 + 0.5) - 0.5) * 0.5, 0.003, px) * step(d, 0.035);
            vec2 dm = abs(q - (a + b) * 0.5);
            float dia = line(abs(dm.x + dm.y - 0.05), 0.003, px);
            col += guide * (line(d, 0.003, px) * dash * 0.8 + ticks * 0.7) * fade * u_intensity;
            col += u_color1 * dia * fade;
        }
    }

    // personas: guías CAD, caja de detección, etiqueta, mira
    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        float id = p.w;
        vec2 jit = (vec2(noise(vec2(t * 6.0, id * 3.1)), noise(vec2(id * 3.1, t * 6.0 + 3.0))) - 0.5);
        vec2 c = p.xy * A + jit * 0.06 * u_jitter;
        vec2 hb = vec2(u_boxsize * 0.5) * (1.0 + 0.08 * u_bass + (noise(vec2(t * 4.0, id)) - 0.5) * 0.12 * u_jitter);
        vec2 l = q - c;

        // guías horizontales/verticales hasta los bordes, con guiones y regla
        float gh = line(abs(l.y), 0.0012, px) * step(hb.x, abs(l.x)) * step(0.5, fract(q.x / 0.08));
        float gv = line(abs(l.x), 0.0012, px) * step(hb.y, abs(l.y)) * step(0.5, fract(q.y / 0.08));
        float th = line(abs(fract(q.x / 0.5 + 0.5) - 0.5) * 0.5, 0.002, px) * line(abs(l.y), 0.025, px) * step(hb.x, abs(l.x));
        float tv = line(abs(fract(q.y / 0.5 + 0.5) - 0.5) * 0.5, 0.002, px) * line(abs(l.x), 0.025, px) * step(hb.y, abs(l.y));
        col += guide * ((gh + gv) * 0.45 + (th + tv) * 0.5) * u_intensity;

        // ping cuando el radar pasa por la persona
        float ping = exp(-mod(sweepA - atan(c.y - ctr.y, c.x - ctr.x), 6.2831853) * 1.5);

        // caja: contorno tenue + corchetes en las esquinas + relleno que destella con el ping
        float sd = sdRect(l, hb);
        float Lc = min(hb.x, hb.y) * 0.35;
        float corner = step(hb.x - Lc, abs(l.x)) * step(hb.y - Lc, abs(l.y));
        col += u_color1 * line(abs(sd), 0.0015, px) * 0.25;
        col = mix(col, u_color1, line(abs(sd), 0.006, px) * corner);
        float inside = 1.0 - step(0.0, sd);
        col += u_color1 * inside * (0.03 + ping * 0.12 * u_intensity);

        // mira al centro
        float r = length(l);
        col = mix(col, u_color1, line(min(abs(l.x), abs(l.y)), 0.002, px) * step(r, 0.08) * step(0.025, r));

        // etiqueta: barra amarilla con "código de barras" único por ID sobre la esquina sup-izq
        vec2 tl = q - (c + vec2(-hb.x, hb.y + 0.03));
        vec2 tagS = vec2(hb.x * 1.1, 0.09);
        if (tl.x > 0.0 && tl.y > 0.0 && tl.x < tagS.x && tl.y < tagS.y) {
            float bar = step(0.45, hash21(vec2(floor(tl.x / 0.018), id)));
            float inBars = step(0.02, tl.y) * step(tl.y, tagS.y - 0.02) * step(0.02, tl.x) * step(tl.x, tagS.x - 0.02);
            col = mix(u_color1, u_color3, bar * inBars);
        }
    }

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
