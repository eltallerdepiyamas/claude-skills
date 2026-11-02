// base5 · campo_bokeh
// Circulos desenfocados que entran y salen de foco, respirando.
// Lo mas literalmente dream pop del set.
// Implementacion: hash por celda en una rejilla, no un loop sobre u_count particulas.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_amount;        // intensidad (slot 1)
uniform float u_speed;         // velocidad (slot 2)
uniform float u_defocus;       // distorsion (slot 3)  — cuanto se desenfocan
uniform float u_color_spread;  // color (slot 4)
uniform float u_count;         // firma (slot 5)       — densidad de la rejilla
uniform float u_size;          // extra
uniform vec3  u_color1;        // ambar
uniform vec3  u_color2;        // rosa
uniform vec3  u_color3;        // crema

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void main() {
    vec2 uv = vUV.st;
    float aspect = u_res.x / max(u_res.y, 1.0);
    vec2 uvA = vec2(uv.x * aspect, uv.y);

    float g = max(u_count, 1.0);
    vec2 cell = floor(uvA * g);

    vec3 col = vec3(0.0);
    // vecindario 3x3 para circulos que solapan celdas
    for (int oy = -1; oy <= 1; oy++) {
        for (int ox = -1; ox <= 1; ox++) {
            vec2 nc = cell + vec2(float(ox), float(oy));
            float h  = hash(nc);
            float h2 = hash(nc + 17.3);
            float h3 = hash(nc + 41.7);

            float phase = h * 6.28318;
            float t = u_time * u_speed + phase;

            // centro en la celda vecina + movimiento suave
            vec2 center = nc + vec2(0.5) + vec2(
                sin(t * 0.7 + h2 * 6.28) * 0.3,
                cos(t * 0.9 + h3 * 6.28) * 0.3
            );

            // respiracion del tamano
            float sz = u_size * (0.5 + 0.5 * sin(t + h * 6.28));
            sz *= mix(0.6, 1.4, h2);

            float d = length(uvA * g - center);
            // mas defocus = borde mas suave
            float edge = mix(sz * 0.3, sz * 1.8, u_defocus);
            float mask = smoothstep(sz + edge, max(sz - edge, 0.0), d);

            // color por hash con spread hacia paleta base
            vec3 c;
            if (h3 < 0.34) c = u_color1;
            else if (h3 < 0.67) c = u_color2;
            else c = u_color3;
            c = mix(c, mix(u_color1, u_color2, h), u_color_spread);

            col += c * mask;
        }
    }

    col = col * u_amount;
    col *= 1.0 + u_bass * 0.15;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
