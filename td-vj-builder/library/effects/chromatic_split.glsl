// =============================================================
// CHROMATIC SPLIT - LITTLE JESUS (base44)
// =============================================================
// Separa los canales R y B del UV en direccion uAngle. Con
// feedback subsecuente acumula halos de color psicodelicos.
// =============================================================

// --- Uniforms (pagina Vectors del GLSL TOP) ---
uniform float uTime;
uniform vec2  uResolution;
uniform float uSplitR;     // 0..0.05  desplazamiento canal rojo
uniform float uSplitB;     // 0..0.05  desplazamiento canal azul
uniform float uAngle;      // 0..2pi   angulo de separacion (radianes)

out vec4 fragColor;

void main() {
    vec2 uv  = vUV.st;
    vec2 dir = vec2(cos(uAngle), sin(uAngle));

    vec2 uvR = uv + dir * uSplitR;
    vec2 uvB = uv - dir * uSplitB;

    float r = texture(sTD2DInputs[0], uvR).r;
    float g = texture(sTD2DInputs[0], uv).g;
    float b = texture(sTD2DInputs[0], uvB).b;

    fragColor = vec4(r, g, b, 1.0);
}
