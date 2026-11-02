// base8 · cuerdas
// Lineas verticales que vibran con motion blur. Reactivas a agudos:
// visual de los solos con fuzz.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_amount;       // intensidad (slot 1)
uniform float u_speed;        // velocidad (slot 2)
uniform float u_amplitude;    // distorsion (slot 3)  — audio High empuja aqui
uniform float u_color_shift;  // color (slot 4)
uniform float u_count;        // firma (slot 5)       — numero de cuerdas
uniform float u_blur;         // extra                — motion blur horizontal
uniform vec3  u_color1;       // crema
uniform vec3  u_color2;       // violeta
uniform vec3  u_color3;       // turquesa

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void main() {
    vec2 uv = vUV.st;

    float count = max(u_count, 1.0);
    float t = u_time * u_speed;

    vec3 col = vec3(0.0);
    const int SAMPLES = 5;
    for (int s = 0; s < SAMPLES; s++) {
        float off = (float(s) / float(SAMPLES - 1) - 0.5) * u_blur;
        float ux = uv.x + off;

        float xIndex  = floor(ux * count);
        float xInCell = fract(ux * count) - 0.5;

        // wobble por columna via hash
        float h = hash(vec2(xIndex, 0.0));
        float wobbleX = sin(t + h * 6.28318 + uv.y * 4.0) * u_amplitude * count;
        float dist = abs(xInCell - wobbleX);

        // linea centrada en la celda
        float line = smoothstep(0.5, 0.0, dist * 8.0);

        // color por columna (con shift)
        float ch = fract(h + u_color_shift);
        vec3 lc;
        if (ch < 0.34) lc = u_color1;
        else if (ch < 0.67) lc = u_color2;
        else lc = u_color3;

        col += lc * line;
    }
    col /= float(SAMPLES);
    col *= u_amount;
    col *= 1.0 + u_bass * 0.2;

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
