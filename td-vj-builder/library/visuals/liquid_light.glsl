// base2 · liquid_light — look base fuerte
// Oil & water sesentero: blobs de aceite que se dividen y se funden.
// Metaballs con domain warping — borde definido = aceite proyectado, no humo.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_amount;      // intensidad (slot 1)
uniform float u_speed;       // velocidad (slot 2)
uniform float u_warp;        // distorsión (slot 3)  — domain warping
uniform float u_sat;         // color (slot 4)       — saturación
uniform float u_blob_scale;  // firma (slot 5)       — densidad de blobs
uniform float u_edge;        // extra                — dureza del borde
uniform vec3  u_color1;      // ámbar
uniform vec3  u_color2;      // turquesa
uniform vec3  u_color3;      // rosa

out vec4 fragColor;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

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

vec3 satAdjust(vec3 c, float s) {
    float l = dot(c, vec3(0.299, 0.587, 0.114));
    return mix(vec3(l), c, s);
}

void main() {
    vec2 uv = vUV.st;
    vec2 p = (uv - 0.5);
    p.x *= u_res.x / max(u_res.y, 1.0);
    p *= u_blob_scale;

    float t = u_time * u_speed;

    // domain warping
    vec2 w = vec2(
        noise(p + vec2(t * 0.7, 0.0)),
        noise(p + vec2(0.0, t * 0.9) + 5.7)
    ) - 0.5;
    p += w * u_warp;

    // 5 blobs en Lissajous
    vec2 c1 = vec2(sin(t * 0.60) * 1.10, cos(t * 0.70) * 0.90);
    vec2 c2 = vec2(cos(t * 0.50 + 1.3) * 0.90, sin(t * 0.80 + 2.1) * 1.20);
    vec2 c3 = vec2(sin(t * 0.90 + 0.5) * 1.00, cos(t * 0.40 + 3.7) * 0.80);
    vec2 c4 = vec2(cos(t * 0.70 + 2.9) * 1.20, sin(t * 0.60 + 1.1) * 1.00);
    vec2 c5 = vec2(sin(t * 0.55 + 4.4) * 0.70, cos(t * 0.65 + 0.9) * 1.10);

    float r = 0.70;
    float f = 0.0;
    f += (r * r) / (dot(p - c1, p - c1) + 0.001);
    f += (r * r) / (dot(p - c2, p - c2) + 0.001);
    f += (r * r) / (dot(p - c3, p - c3) + 0.001);
    f += (r * r) / (dot(p - c4, p - c4) + 0.001);
    f += (r * r) / (dot(p - c5, p - c5) + 0.001);

    // borde tipo aceite (más u_edge = borde más duro)
    float edgeW = mix(0.55, 0.05, u_edge);
    float m = smoothstep(1.0 - edgeW, 1.0 + edgeW, f);

    // color por campo — rota por el field magnitude para dar iridiscencia
    float t2 = fract(f * 0.14 + u_time * 0.04);
    vec3 col;
    if (t2 < 0.5) {
        col = mix(u_color1, u_color2, t2 * 2.0);
    } else {
        col = mix(u_color2, u_color3, (t2 - 0.5) * 2.0);
    }

    col = satAdjust(col, u_sat);

    // presencia del blob + amount global
    vec3 result = col * mix(0.15, 1.0, m) * mix(0.2, 1.0, u_amount);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
