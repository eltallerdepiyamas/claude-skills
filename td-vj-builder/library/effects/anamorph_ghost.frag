// base22 · anamorph_ghost
// Un fantasma estirado en horizontal y desenfocado flota detras de la imagen.
// El fantasma es el frame anterior, no una copia del actual.

uniform float uTime;
uniform vec2  uResolution;
uniform float uGhost;        // intensidad (slot 1)
uniform float uGhostDecay;   // velocidad (slot 2)   — persistencia del fantasma
uniform float uStretch;      // distorsion (slot 3)  — factor de estiramiento horizontal
uniform vec3  uGhostTint;    // color (slot 4)
uniform float uOffsetX;      // firma (slot 5)       — offset lateral del fantasma
uniform float uBlur;         // extra                — box blur horizontal (5 muestras)

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec3 cam = texture(sTD2DInputs[0], uv).rgb;

    // UV del fantasma: estirado en X y con offset lateral
    vec2 gUV = vec2((uv.x - 0.5 - uOffsetX) / max(uStretch, 0.01) + 0.5, uv.y);

    // Box blur horizontal de 5 muestras (barato, mas cheap que gaussiano)
    vec3 ghost = vec3(0.0);
    ghost += texture(sTD2DInputs[1], gUV + vec2(-2.0 * uBlur, 0.0)).rgb;
    ghost += texture(sTD2DInputs[1], gUV + vec2(-1.0 * uBlur, 0.0)).rgb;
    ghost += texture(sTD2DInputs[1], gUV).rgb;
    ghost += texture(sTD2DInputs[1], gUV + vec2( 1.0 * uBlur, 0.0)).rgb;
    ghost += texture(sTD2DInputs[1], gUV + vec2( 2.0 * uBlur, 0.0)).rgb;
    ghost /= 5.0;

    ghost *= uGhostDecay * uGhostTint * 1.3;

    // camara al frente, fantasma detras
    vec3 result = max(cam, ghost * uGhost);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
