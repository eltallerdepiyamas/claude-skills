// =============================================================
// DISPLACEMENT WAVE - LITTLE JESUS (base39)
// =============================================================
// Distorsion UV con ondas sinusoidales animadas en X y Y.
// Sin feedback -- warp puro. Efecto de agua / tela.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform float uWaveAmt;     // 0.015  amplitud del desplazamiento
uniform float uWaveFreqX;   // 8.0    frecuencia de la onda en X
uniform float uWaveFreqY;   // 6.0    frecuencia de la onda en Y
uniform float uSpeed;       // 0.5    velocidad de animacion

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    // Onda X depende de la posicion Y; onda Y depende de la posicion X.
    // Frecuencias temporales distintas (uSpeed vs uSpeed*0.7) -> no se
    // sincronizan, el agua nunca se ve repetitivo.
    float dx = sin(uv.y * uWaveFreqY + uTime * uSpeed)       * uWaveAmt;
    float dy = cos(uv.x * uWaveFreqX + uTime * uSpeed * 0.7) * uWaveAmt;

    vec2 warpedUV = uv + vec2(dx, dy);
    fragColor = texture(sTD2DInputs[0], warpedUV);
}
