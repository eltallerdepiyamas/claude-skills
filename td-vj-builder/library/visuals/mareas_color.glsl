// base6 · mareas_color
// Dos frentes de color que se invaden mutuamente con un borde iridiscente donde se tocan.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_amount;        // intensidad (slot 1)
uniform float u_speed;         // velocidad (slot 2)
uniform float u_turbulence;    // distorsion (slot 3)
uniform float u_iridescence;   // color (slot 4)
uniform float u_front;         // firma (slot 5)  — posicion del frente
uniform float u_edge_width;    // extra
uniform vec3  u_color1;        // turquesa (frente izquierdo)
uniform vec3  u_color2;        // ambar (frente derecho)
uniform vec3  u_color3;        // rosa (borde iridiscente)

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
    float t = u_time * u_speed;

    // frente ondulante — perturbado con noise por turbulencia
    float boundary = u_front + sin(uv.y * 6.0 + t * 1.5) * 0.05;
    boundary += (noise(vec2(uv.y * 3.0 + t, uv.x * 2.0)) - 0.5) * u_turbulence * 0.15;

    float side = smoothstep(boundary - u_edge_width, boundary + u_edge_width, uv.x);
    float edge = 1.0 - smoothstep(0.0, u_edge_width * 2.0, abs(uv.x - boundary));

    // color base: turquesa a la izquierda, ambar a la derecha
    vec3 col = mix(u_color1, u_color2, side);

    // borde iridiscente: mezcla animada con rosa
    vec3 iridColor = mix(u_color3, u_color2, sin(t + uv.y * 8.0) * 0.5 + 0.5);
    col = mix(col, iridColor, edge * u_iridescence);

    col *= u_amount;
    col *= 1.0 + u_bass * 0.1;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
