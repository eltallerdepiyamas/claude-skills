// base43 · crt_edge_bleed (APF 09 — EXTENDIDO)
// Fosforo CRT — bleed cromatico en bordes brillantes. Original tenia solo
// uBleedAmount, se anadieron uMix (era 0.92), uThreshold (era 0.4/0.8),
// uGain (era 1.05) y uPhosphorDecay para que los 5 slots MIDI hagan cosas distintas.

uniform float uTime;
uniform float uBleedAmount;    // slot 3 — separacion RGB
uniform float uMix;            // slot 1 — reemplaza el 0.92 literal
uniform float uPhosphorDecay;  // slot 2 — nuevo: decay del trail de fosforo
uniform float uGain;           // slot 4 — reemplaza el 1.05 literal
uniform float uThreshold;      // slot 5 — reemplaza el 0.4 (0.8 = threshold+0.4)

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 color = texture(sTD2DInputs[0], uv);

    // Desplazamiento cromatico simulando convergencia analogica
    float red   = texture(sTD2DInputs[1], uv - vec2(uBleedAmount, 0.0)).r;
    float green = texture(sTD2DInputs[1], uv                       ).g;
    float blue  = texture(sTD2DInputs[1], uv + vec2(uBleedAmount, 0.0)).b;

    vec4 fb = vec4(red, green, blue, 1.0) * uPhosphorDecay;

    // gate por luminancia (solo lo brillante deja rastro fosforico)
    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    float mask = smoothstep(uThreshold, uThreshold + 0.4, luma);

    fragColor = TDOutputSwizzle(mix(color, fb * uGain, uMix * mask));
}
