// base24 · breath_zoom — el audio-reactivo del set
// Zoom y rotacion acumulativos = tunel que respira con el bajo.
// La respiracion es sin(uTime*uRate*TWO_PI) MAS la energia de audio,
// ambas pasadas por smoothstep. Nunca conectar la energia cruda al zoom.

uniform float uTime;
uniform vec2  uResolution;
uniform float uBreath;       // intensidad (slot 1)  — amplitud del zoom-respiracion
uniform float uRate;         // velocidad (slot 2)   — frecuencia de la respiracion
uniform float uSwirl;        // distorsion (slot 3)  — rotacion por frame acumulativa
uniform vec3  uTunnelTint;   // color (slot 4)       — tinte del tunel
uniform float uDecay;        // firma (slot 5)       — persistencia del feedback
uniform float uMix;          // extra                — cuanto de camara nueva se inyecta

out vec4 fragColor;

const float TAU = 6.28318530718;

void main() {
    vec2 uv = vUV.st;
    vec2 p = uv - 0.5;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    p.x *= aspect;

    // respiracion suavizada: sin(uTime*rate) pasado por smoothstep para evitar patada
    float phase = sin(uTime * uRate * TAU);
    float breath = smoothstep(-1.0, 1.0, phase) * uBreath;

    // zoom hacia adentro (efecto tunel)
    float z = 1.0 - breath;
    p *= z;

    // swirl acumulativo por frame
    float ca = cos(uSwirl), sa = sin(uSwirl);
    p = mat2(ca, -sa, sa, ca) * p;

    p.x /= aspect;
    vec2 fbUV = p + 0.5;

    vec3 fb = texture(sTD2DInputs[1], fbUV).rgb * uDecay;
    fb *= uTunnelTint * 1.2;

    vec3 cam = texture(sTD2DInputs[0], uv).rgb;

    vec3 result = mix(fb, cam, uMix);

    fragColor = TDOutputSwizzle(vec4(result, 1.0));
}
