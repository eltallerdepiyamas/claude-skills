// base23 · retrato_focal
// Nitido en el centro, disolucion acuarela hacia afuera. La periferia acumula,
// asi que la acuarela se va formando sola durante la rola.
// Diff con nucleo_frio: aquel deforma con gradiente de luma (direccional);
// este difunde con noise omnidireccional y desatura (acuarela sin direccion).

uniform float uTime;
uniform vec2  uResolution;
uniform float uSoftness;      // intensidad (slot 1)
uniform float uFlow;          // velocidad (slot 2)
uniform float uSpread;        // distorsion (slot 3)  — magnitud del offset omnidireccional
uniform float uDesat;         // color (slot 4)       — desaturacion de la periferia
uniform float uFocusRadius;   // firma (slot 5)       — radio del nucleo enfocado
uniform float uFocusSoft;     // extra
uniform float uDecay;         // extra

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

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

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }
vec3 desatMix(vec3 c, float a) { return mix(c, vec3(luma(c)), a); }

void main() {
    vec2 uv = vUV.st;

    float dist = length(uv - 0.5);
    float outsideMask = smoothstep(uFocusRadius - uFocusSoft, uFocusRadius + uFocusSoft, dist);

    // acuarela: offset por noise omnidireccional (sin direccion, a diferencia
    // del gradiente de luma que usa nucleo_frio)
    float t = uTime * 0.3;
    vec2 offN = vec2(
        noise(uv * 5.0 + vec2(t, 0.0)) - 0.5,
        noise(uv * 5.0 + vec2(0.0, t) + 3.7) - 0.5
    ) * uSpread;
    // + flow lento
    offN += vec2(noise(uv * 2.0 + uTime * uFlow * 20.0) - 0.5) * uFlow * 3.0;

    vec3 fb = texture(sTD2DInputs[1], uv + offN * outsideMask).rgb * uDecay;
    fb = desatMix(fb, uDesat);

    vec3 cam = texture(sTD2DInputs[0], uv).rgb;

    // dentro: camara pura; fuera: mezcla feedback difundido + camara
    vec3 accumulated = mix(fb, cam, 1.0 - uSoftness);
    vec3 result = mix(cam, accumulated, outsideMask);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
