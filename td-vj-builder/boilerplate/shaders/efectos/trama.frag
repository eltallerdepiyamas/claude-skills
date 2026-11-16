// trama.frag — base18 · Trama (Rio Salvaje): puntos de impresion (halftone) con la paleta del album.
uniform float uTime;
uniform vec2  uResolution;
uniform float uEnergy;
uniform float uMezcla;       // 1 intensidad · limpio <-> trama
uniform float uSpeed;        // 2 velocidad  · la trama deriva
uniform float uAngulo;       // 3 distorsion · angulo de la trama
uniform float uTinte;        // 4 color      · 0 color de la imagen · 1 color del album
uniform float uPunto;        // 5 firma      · tamano del punto (px)
uniform vec3  uTinta;
uniform vec3  uPapel;
out vec4 fragColor;
void main() {
    vec2 uv = vUV.st;
    vec4 src = texture(sTD2DInputs[0], uv);
    float tam = max(uPunto, 2.0);
    float a = uAngulo, c = cos(a), s = sin(a);
    mat2 R = mat2(c, -s, s, c);
    vec2 g = R * (uv * uResolution) / tam + uTime * uSpeed;
    vec2 f = fract(g) - 0.5;
    vec2 centro = (floor(g) + 0.5 - uTime * uSpeed) * tam;
    vec3 m = texture(sTD2DInputs[0], (transpose(R) * centro) / uResolution).rgb;
    float l = dot(m, vec3(0.2126, 0.7152, 0.0722));
    float r = sqrt(clamp(l + uEnergy * 0.2, 0.0, 1.0)) * 0.7;
    float punto = 1.0 - smoothstep(r - 0.05, r + 0.05, length(f));
    vec3 col = mix(uPapel, mix(m, uTinta, uTinte), punto);
    fragColor = TDOutputSwizzle(vec4(mix(src.rgb, col, uMezcla), 1.0));
}
