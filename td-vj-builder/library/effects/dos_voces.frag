// base21 · dos_voces
// Dos lecturas del feedback con decay distinto y tinte propio cada una,
// ligeramente espejadas. Las dos vocalistas. Una capa recuerda mas que la otra.

uniform float uTime;
uniform vec2  uResolution;
uniform float uBlend;         // intensidad (slot 1)
uniform float uDecayFast;     // velocidad (slot 2)   — decay de la capa A
uniform float uMirrorShift;   // distorsion (slot 3)  — offset horizontal de espejo
uniform float uTintSplit;     // color (slot 4)       — cuanto tine cada capa
uniform float uDecaySlow;     // firma (slot 5)       — decay de la capa B (diferencia = firma)
uniform vec3  uTintA;         // extra
uniform vec3  uTintB;         // extra

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec3 cam = texture(sTD2DInputs[0], uv).rgb;

    // Capa A: espejo a la derecha, decay rapido, tinte A
    vec2 uvA = vec2(uv.x + uMirrorShift, uv.y);
    vec3 fbA = texture(sTD2DInputs[1], uvA).rgb * uDecayFast;
    fbA = mix(fbA, fbA * uTintA * 1.5, uTintSplit);

    // Capa B: espejo a la izquierda, decay lento, tinte B
    vec2 uvB = vec2(uv.x - uMirrorShift, uv.y);
    vec3 fbB = texture(sTD2DInputs[1], uvB).rgb * uDecaySlow;
    fbB = mix(fbB, fbB * uTintB * 1.5, uTintSplit);

    vec3 combined = max(fbA, fbB);

    // uBlend: cuanta camara nueva vs. las dos capas de memoria
    vec3 result = mix(combined, max(combined, cam), uBlend);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
