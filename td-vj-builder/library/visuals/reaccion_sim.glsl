// reaccion_sim.glsl: un paso de reaccion-difusion Gray-Scott. r = U, g = V (rgba32float).
// Se encadena 4 veces por cuadro dentro de base46/red. u_seed = (x, y, radio, cantidad) siembra V.
uniform float u_patron;      // 0 mitosis · 0.5 coral · 1 laberinto
uniform float u_bass;
uniform float u_warp;        // variacion del patron a lo ancho de la pantalla
uniform float u_dt;
uniform vec4  u_seed;
out vec4 fragColor;

ivec2 SZ;
vec2 at(ivec2 ij) { return texelFetch(sTD2DInputs[0], (ij + SZ) % SZ, 0).rg; }   // con vuelta en los bordes

void main() {
    vec2 uv = vUV.st;
    SZ = textureSize(sTD2DInputs[0], 0);
    ivec2 ij = ivec2(gl_FragCoord.xy);
    vec2 c = at(ij);
    vec2 lap = -c
        + 0.2  * (at(ij + ivec2(1, 0)) + at(ij - ivec2(1, 0)) + at(ij + ivec2(0, 1)) + at(ij - ivec2(0, 1)))
        + 0.05 * (at(ij + ivec2(1, 1)) + at(ij - ivec2(1, 1)) + at(ij + ivec2(1, -1)) + at(ij + ivec2(-1, 1)));
    float p = clamp(u_patron + u_warp * (uv.x - 0.5) * 0.8, 0.0, 1.0);
    // 0 mitosis (focos que se dividen) · 0.5 coral · 1 laberinto
    float f = p < 0.5 ? mix(0.0367, 0.0545, p * 2.0) : mix(0.0545, 0.029, p * 2.0 - 1.0);
    float k = p < 0.5 ? mix(0.0649, 0.0635, p * 2.0) : mix(0.0635, 0.057, p * 2.0 - 1.0);
    f += 0.0008 * clamp(u_bass, 0.0, 1.5);
    // si k < sqrt(f)/2 - f existe un estado lleno estable y todo se vuelve una mancha: nunca cruzar ese borde
    k = max(k, sqrt(f) * 0.5 - f + 0.0015);
    float U = c.r, V = c.g;
    float uvv = U * V * V;
    U += u_dt * (1.0 * lap.r - uvv + f * (1.0 - U));
    V += u_dt * (0.5 * lap.g + uvv - (f + k) * V);
    float asp = float(SZ.x) / float(SZ.y);
    vec2 d = (uv - u_seed.xy) * vec2(asp, 1.0);
    if (u_seed.w > 0.0 && dot(d, d) < u_seed.z * u_seed.z) V = max(V, u_seed.w);
    fragColor = vec4(clamp(U, 0.0, 1.0), clamp(V, 0.0, 1.0), 0.0, 1.0);
}
