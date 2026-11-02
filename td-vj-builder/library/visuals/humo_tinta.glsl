// base4 · humo_tinta
// Tinta en agua: columnas de fbm advectado que suben y se difunden.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_amount;      // intensidad (slot 1)
uniform float u_rise;        // velocidad (slot 2)  — velocidad de subida
uniform float u_turbulence;  // distorsion (slot 3)
uniform float u_ink_mix;     // color (slot 4)
uniform float u_diffusion;   // firma (slot 5)      — cuanto se difunde la tinta
uniform float u_octaves;     // extra — float pero se usa como int (if/else if)
uniform vec3  u_color1;      // violeta
uniform vec3  u_color2;      // turquesa
uniform vec3  u_color3;      // crema

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// fbm hasta 6 octavas con cadena if/else if (no array indexing dinamico)
float fbm(vec2 p, int oct) {
    float f = 0.0;
    float a = 0.5;
    if (oct >= 1) { f += a * noise(p); p *= 2.0; a *= 0.5; }
    if (oct >= 2) { f += a * noise(p); p *= 2.0; a *= 0.5; }
    if (oct >= 3) { f += a * noise(p); p *= 2.0; a *= 0.5; }
    if (oct >= 4) { f += a * noise(p); p *= 2.0; a *= 0.5; }
    if (oct >= 5) { f += a * noise(p); p *= 2.0; a *= 0.5; }
    if (oct >= 6) { f += a * noise(p); }
    return f;
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv - 0.5;
    p.x *= u_res.x / max(u_res.y, 1.0);
    p *= 2.5;

    int octaves = int(clamp(u_octaves, 2.0, 6.0));
    float t = u_time * 0.3;

    // adveccion hacia arriba
    p.y -= u_time * u_rise * 0.3;

    // dominio deformado con fbm anidado
    vec2 q = vec2(fbm(p + vec2(0.0, t), octaves),
                  fbm(p + vec2(5.7, -t * 0.7), octaves));
    vec2 r = vec2(fbm(p + 4.0 * q + vec2(1.7, 9.2), octaves),
                  fbm(p + 4.0 * q + vec2(8.3, 2.8), octaves));
    float f = fbm(p + 4.0 * r * u_turbulence, octaves);

    // difusion: mas alto = umbral mas ancho = tinta se dispersa
    float ink = smoothstep(mix(0.6, 0.15, u_diffusion), mix(0.85, 0.5, u_diffusion), f);

    // colores por fase
    vec3 col;
    if (f < 0.5) {
        col = mix(u_color1, u_color2, f * 2.0);
    } else {
        col = mix(u_color2, u_color3, (f - 0.5) * 2.0);
    }
    col = mix(col, col * u_color1 * 1.4, u_ink_mix);

    vec3 result = col * ink * u_amount;
    result *= 1.0 + u_bass * 0.12;

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
