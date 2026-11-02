// base7 · eclipse
// Anillo de luz con corona; el disco central respira. Guino a Meddle, geometria simple.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_corona;      // intensidad (slot 1)
uniform float u_speed;       // velocidad (slot 2)
uniform float u_wobble;      // distorsion (slot 3)
uniform float u_ring_mix;    // color (slot 4)
uniform float u_radius;      // firma (slot 5)  — audio Low empuja aqui
uniform float u_thickness;   // extra
uniform vec3  u_color1;      // ambar (corona)
uniform vec3  u_color2;      // negro violaceo (fondo/disco)
uniform vec3  u_color3;      // rosa (anillo)

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

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv - 0.5;
    p.x *= u_res.x / max(u_res.y, 1.0);

    float t = u_time * u_speed;

    // disco central respira
    float r = u_radius + sin(t * 2.0) * u_wobble;
    r += (noise(vec2(t * 1.3, 0.0)) - 0.5) * u_wobble * 2.0;

    float d = length(p);

    // disco central (negro violaceo)
    float disc = smoothstep(r, r - 0.005, d);

    // anillo brillante justo fuera del disco
    float ringR = r + u_thickness * 2.0;
    float ring  = 1.0 - smoothstep(0.0, u_thickness, abs(d - ringR));

    // corona (halo suave alrededor del disco)
    float corona = exp(-abs(d - r) * 20.0 / max(u_corona, 0.01)) * u_corona;

    // fondo violaceo profundo
    vec3 col = u_color2;

    // corona en ambar
    col = mix(col, u_color1, clamp(corona, 0.0, 1.0));

    // anillo brillante: ambar mezclado con rosa segun u_ring_mix
    vec3 ringColor = mix(u_color1, u_color3, u_ring_mix);
    col = mix(col, ringColor, ring);

    // disco central: casi negro
    col = mix(col, u_color2 * 0.4, disc);

    col *= 1.0 + u_bass * 0.08;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
