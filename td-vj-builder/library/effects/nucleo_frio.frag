// base18 · nucleo_frio — look base
// El centro del frame no acumula feedback; los bordes sí.
// La cara queda limpia y legible mientras alrededor se convierte en pintura líquida.

uniform float uTime;
uniform vec2  uResolution;
uniform float uAccum;        // intensidad (slot 1)  — cuánto feedback se acumula en bordes
uniform float uDrift;        // velocidad (slot 2)   — deriva lenta del feedback
uniform float uWarp;         // distorsión (slot 3)  — magnitud del warp por gradiente
uniform float uChroma;       // color (slot 4)       — separación cromática en el feedback
uniform float uCoreRadius;   // firma (slot 5)       — radio del núcleo limpio (cara)
uniform float uCoreSoft;     // extra                — suavidad del borde del núcleo
uniform vec3  uTint;         // extra                — tinte cálido del feedback acumulado

out vec4 fragColor;

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

// gradiente de luminancia del feedback (cruz de 4 muestras)
vec2 lumaGrad(vec2 uv, vec2 px) {
    float lL = luma(texture(sTD2DInputs[1], uv - vec2(px.x, 0.0)).rgb);
    float lR = luma(texture(sTD2DInputs[1], uv + vec2(px.x, 0.0)).rgb);
    float lD = luma(texture(sTD2DInputs[1], uv - vec2(0.0, px.y)).rgb);
    float lU = luma(texture(sTD2DInputs[1], uv + vec2(0.0, px.y)).rgb);
    return vec2(lR - lL, lU - lD);
}

void main() {
    vec2 uv = vUV.st;
    vec2 px = 1.0 / max(uResolution, vec2(1.0));

    // máscara: 0 en el centro, 1 en los bordes
    float dist = length(uv - 0.5);
    float edgeMask = smoothstep(uCoreRadius - uCoreSoft, uCoreRadius + uCoreSoft, dist);

    // warp offset: gradiente de luminancia del feedback, solo en los bordes
    vec2 grad = lumaGrad(uv, px);
    vec2 drift = vec2(sin(uTime * 0.13), cos(uTime * 0.17)) * uDrift;
    vec2 warpOffset = (grad * uWarp + drift) * edgeMask;

    // muestreo del feedback con chroma split
    vec2 chOff = vec2(uChroma, 0.0);
    float fbR = texture(sTD2DInputs[1], uv + warpOffset + chOff).r;
    float fbG = texture(sTD2DInputs[1], uv + warpOffset).g;
    float fbB = texture(sTD2DInputs[1], uv + warpOffset - chOff).b;
    vec3 feedback = vec3(fbR, fbG, fbB) * uTint;

    // cámara
    vec3 camera = texture(sTD2DInputs[0], uv).rgb;

    // mezcla: centro = cámara pura; bordes = feedback acumulado con pizca de cámara fresca
    vec3 accumulated = feedback * uAccum + camera * (1.0 - uAccum);
    vec3 result = mix(camera, accumulated, edgeMask);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
