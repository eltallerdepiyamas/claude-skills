// atractor.glsl: atractor extrano de Clifford acumulado en feedback (recetario 14; ref. Max Cooper, Anadol: nubes de puntos finos).
// Cada cuadro cada pixel suma la densidad de los N puntos nuevos de la orbita (otros cada cuadro) y el cuadro anterior
// decae lento: con los segundos se dibujan cientos de miles de puntos finos sobre negro. Kick = cambia de rama (en la orbita)
// y aviva los puntos nuevos; bajos = deforman la figura despacio.
// sTD2DInputs[0] = puntos de este cuadro (base52/red/out1, N x 1) / sTD2DInputs[1] = cuadro anterior.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;
uniform float u_tono;
uniform float u_firma;       // 5 firma: atractor (rama base; lo usa la orbita)
uniform float u_estela;      // extra: cuanto queda del cuadro anterior
out vec4 fragColor;
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5);
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * u_speed;
    p = rot(-t * 0.015) * p;                                  // giro muy lento de toda la figura
    vec2 escala = vec2(0.56, 0.44);

    int n = textureSize(sTD2DInputs[0], 0).x;
    float pxs = 1.0 / u_res.y;
    float r2 = pxs * pxs * 0.9;                               // punto de ~1 px
    float acc = 0.0, vel = 0.0;
    for (int i = 0; i < 512; i++) {
        if (i >= n) break;
        vec4 o = texelFetch(sTD2DInputs[0], ivec2(i, 0), 0);
        vec2 d = p - o.xy * escala;
        float e = dot(d, d) / r2;
        if (e < 5.0) {
            float w = exp(-e);
            acc += w;
            vel += w * o.z;
        }
    }
    vel = acc > 1e-4 ? vel / acc : 0.0;

    vec3 tinta = mix(u_color1, u_color2, u_tono);
    vec3 prev = texture(sTD2DInputs[1], uv).rgb * clamp(u_estela, 0.0, 0.995);
    float brillo = 0.55 * u_intensity * (0.7 + 0.4 * lo + 1.2 * k);
    // puntos rapidos (saltos largos) un poco mas cerca del blanco
    vec3 nuevo = mix(tinta, vec3(1.0), 0.15 + 0.35 * clamp(vel * 1.5, 0.0, 1.0) * (0.6 + 0.4 * hi)) * acc * brillo;
    vec3 col = min(prev + nuevo, vec3(0.85));
    fragColor = TDOutputSwizzle(vec4(max(col, u_color3), 1.0));
}
