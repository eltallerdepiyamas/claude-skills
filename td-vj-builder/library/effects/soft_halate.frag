// base19 · soft_halate — look base
// Halación de película: las altas luces sangran color cálido alrededor
// y el aura persiste unos frames. Suaviza sin destruir.

uniform float uTime;
uniform vec2  uResolution;
uniform float uHalation;    // intensidad (slot 1)  — cuánto aura se suma sobre la cámara
uniform float uBleedSpeed;  // velocidad (slot 2)   — rotación del muestreo radial
uniform float uSpread;      // distorsión (slot 3)  — radio del sangrado
uniform float uWarmth;      // color (slot 4)       — cuánto tinte cálido tiñe el aura
uniform float uThreshold;   // firma (slot 5)       — umbral de extracción de altas luces
uniform float uDecay;       // extra                — persistencia del aura en feedback
uniform vec3  uTint;        // extra                — tinte cálido (naranja/ámbar por default)

out vec4 fragColor;

const float TAU = 6.28318530718;

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main() {
    vec2 uv = vUV.st;

    vec3 camera = texture(sTD2DInputs[0], uv).rgb;

    // extraer altas luces y expandirlas radialmente — acumular con max() para no oscurecer
    float rot = uTime * uBleedSpeed * 0.35;
    vec3 halation = vec3(0.0);
    const int SAMPLES = 6;
    for (int i = 0; i < SAMPLES; i++) {
        float a = float(i) / float(SAMPLES) * TAU + rot;
        vec2 off = vec2(cos(a), sin(a)) * uSpread;
        vec3 sc = texture(sTD2DInputs[0], uv + off).rgb;
        float hi = smoothstep(uThreshold, 1.0, luma(sc));
        halation = max(halation, sc * hi);
    }
    // tinte cálido
    vec3 tinted = halation * uTint * 1.4;
    halation = mix(halation, tinted, uWarmth);

    // feedback con max() — el aura persiste, no se oscurece
    vec3 feedback = texture(sTD2DInputs[1], uv).rgb;
    vec3 aura = max(halation, feedback * uDecay);

    // composición: cámara + aura escalada por uHalation
    vec3 result = camera + aura * uHalation;

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
