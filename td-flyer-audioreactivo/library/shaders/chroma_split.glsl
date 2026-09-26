// flyer_loop_chroma.glsl
// Aberracion cromatica / RGB split para el flyer animado.
// Separa los canales R y B a lo largo de un angulo que bambolea lento (loop suave).
// uOffset (px) lo empuja el audio (banda alta) desde el builder.
// Entrada: sTD2DInputs[0] (NUNCA declarar uniform sampler2D para inputs de TD).

out vec4 fragColor;

uniform vec2  uResolution;   // resolucion del TOP (px)
uniform float uOffset;       // separacion de canales en pixeles
uniform float uTime;         // absTime.seconds
uniform float uWobble;       // velocidad del bamboleo del angulo

void main()
{
    vec2 uv = vUV.st;
    vec2 px = 1.0 / uResolution;            // 1 pixel en UV

    // El angulo gira lento -> el split "respira" en vez de quedarse fijo.
    float ang = uTime * uWobble;
    vec2  dir = vec2(cos(ang), sin(ang)) * uOffset * px;

    // Rojo se va por un lado, azul por el otro, verde queda anclado.
    float r = texture(sTD2DInputs[0], uv + dir).r;
    float g = texture(sTD2DInputs[0], uv      ).g;
    float b = texture(sTD2DInputs[0], uv - dir).b;
    float a = texture(sTD2DInputs[0], uv      ).a;

    fragColor = TDOutputSwizzle(vec4(r, g, b, a));
}
