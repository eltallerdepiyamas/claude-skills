// base3 · niebla_capas — fondo atmosferico
// Capas de niebla con paralax y un haz de luz atravesandolas.
// Penumbra de trip-hop.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_density;    // intensidad (slot 1)
uniform float u_speed;      // velocidad (slot 2)
uniform float u_paralax;    // distorsion (slot 3)
uniform float u_light_mix;  // color (slot 4)
uniform float u_layers;     // firma (slot 5) — float pero se usa como int
uniform float u_beam;       // extra
uniform vec3  u_color1;     // negro violaceo (fondo)
uniform vec3  u_color2;     // violeta (niebla media)
uniform vec3  u_color3;     // crema (haz de luz)

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

    // TD no soporta dynamic array indexing / loops con longitud variable limpia,
    // asi que se usa cadena if/else if (regla del brief §6)
    int layers = int(clamp(u_layers, 2.0, 6.0));
    float t = u_time * u_speed;

    float fog = 0.0;
    float weight = 0.0;
    if (layers >= 2) {
        fog += noise(p * 1.5 + vec2(t * 0.6, t * 0.2)) * 1.0;
        weight += 1.0;
    }
    if (layers >= 3) {
        fog += noise(p * 2.5 + vec2(t * 1.0 * u_paralax, -t * 0.15)) * 0.7;
        weight += 0.7;
    }
    if (layers >= 4) {
        fog += noise(p * 4.0 + vec2(t * 1.4 * u_paralax, t * 0.3)) * 0.5;
        weight += 0.5;
    }
    if (layers >= 5) {
        fog += noise(p * 6.0 + vec2(-t * 1.8 * u_paralax, t * 0.4)) * 0.35;
        weight += 0.35;
    }
    if (layers >= 6) {
        fog += noise(p * 9.0 + vec2(t * 2.2 * u_paralax, -t * 0.5)) * 0.25;
        weight += 0.25;
    }
    fog /= max(weight, 0.01);
    fog *= u_density;

    // haz de luz vertical con drift horizontal
    float beamX = 0.5 + sin(u_time * 0.15) * 0.15;
    float beam = 1.0 - smoothstep(0.05, 0.35, abs(uv.x - beamX));
    beam *= smoothstep(0.0, 0.4, uv.y);
    beam *= u_beam;

    // color base por altura
    vec3 base = mix(u_color1, u_color2, smoothstep(0.0, 0.6, uv.y));

    // niebla mezclada con color intermedio (u_light_mix suaviza el color de la niebla)
    vec3 fogTint = mix(u_color2, u_color3, u_light_mix);
    vec3 col = base + vec3(fog) * fogTint * 0.5;

    // haz de luz cremosa
    col += vec3(beam) * u_color3;

    // audio: la niebla respira con el bajo
    col *= 1.0 + u_bass * 0.1;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
