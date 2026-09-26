// =====================================================
// logo_player.glsl — Reproductor de imagenes con look Escuby
// Trata una imagen (logo/PNG) de la carpeta: tinte Yves Klein,
// strobo blanco/negro, stripes, escala. Sencillo y elegante.
// Convencion del skill: snake_case, sTD2DInputs[0] = imagen.
// =====================================================

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;          // energia de audio (sumada por el builder)

uniform float u_image_index;   // selector (lo maneja el Movie File In; aqui no se usa)
uniform float u_strobe_speed;  // velocidad de strobo (0 = off)
uniform float u_stripes;       // numero de franjas (0 = off)
uniform float u_klein_mix;     // 0 = imagen original, 1 = full Klein
uniform float u_scale;         // escala de la imagen

uniform float u_invert;        // 0..1 invierte a negativo en el strobo

uniform vec3 u_color1;         // Yves Klein blue
uniform vec3 u_color2;         // blanco
uniform vec3 u_color3;         // negro

#define u_input sTD2DInputs[0]

out vec4 fragColor;

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main() {
    vec2 uv = vUV.st;

    // --- escala desde el centro ---
    vec2 c = (uv - 0.5) / max(u_scale, 0.001) + 0.5;

    // fuera de rango -> transparente/negro
    vec4 src = (c.x < 0.0 || c.x > 1.0 || c.y < 0.0 || c.y > 1.0)
               ? vec4(0.0) : texture(u_input, c);

    float a = src.a;
    float l = luma(src.rgb);

    // --- tinte Klein: la imagen se tine de azul Klein segun su luma ---
    // luma alta -> blanco; luma media -> Klein; oscuro -> negro
    vec3 klein = mix(u_color3, u_color1, smoothstep(0.05, 0.6, l));
    klein = mix(klein, u_color2, smoothstep(0.6, 0.95, l));
    vec3 col = mix(src.rgb, klein, u_klein_mix);

    // --- strobo blanco/negro (y opcional invert) ---
    if (u_strobe_speed > 0.001) {
        float ph = step(0.5, fract(u_time * u_strobe_speed));
        // alterna entre el color actual y blanco/negro
        vec3 flash = mix(u_color2, u_color3, ph);
        float k = 0.5 + 0.5 * u_bass;     // el bass empuja el strobo
        col = mix(col, flash, ph * k);
        if (u_invert > 0.5) col = 1.0 - col;
    }

    // --- stripes: franjas verticales que enmascaran/colorean ---
    if (u_stripes > 0.001) {
        float s = step(0.5, fract(c.x * u_stripes));
        col = mix(col, u_color1, s * 0.5);
    }

    fragColor = TDOutputSwizzle(vec4(col, max(a, u_klein_mix)));
}
