// =============================================================
// INVERT PULSE - LITTLE JESUS (base42)
// =============================================================
// Inversion parcial del color modulada por un pulso sin/square.
// Con feedback alto y pulso lento genera patrones negativos
// organicos. Con pulso rapido es un strobo de inversion.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform float uInvertAmt;    // 0..1   cuanto se invierte (1 = total)
uniform float uPulseSpeed;   // 0.1..10  velocidad del pulso
uniform float uPulseShape;   // 0 = sine suave, >=0.5 = square duro

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 col = texture(sTD2DInputs[0], uv);

    float pulse = sin(uTime * uPulseSpeed) * 0.5 + 0.5;  // 0..1
    if (uPulseShape > 0.5) pulse = step(0.5, pulse);     // square wave

    vec4 inverted = vec4(1.0 - col.rgb, col.a);
    fragColor = mix(col, inverted, pulse * uInvertAmt);
}
