// hald_lookup.frag — aplica un Hald CLUT (3D LUT) con interpolacion trilinear.
//
// Layout del Hald generado por ffmpeg (haldclutsrc=L):
//   imagen de N x N px con N = L*L*L  (L=8 → 512x512, L=6 → 216x216)
//   para cada pixel k = y*N + x (raster order):
//     r_idx = k mod K
//     g_idx = (k / K) mod K
//     b_idx = k / (K*K)             con K = L*L  (colores por dim)
//
// Inverso (dado (r_idx, g_idx, b_idx), encontrar el pixel):
//   x = (g_idx mod L) * K + r_idx
//   y = b_idx * L + floor(g_idx / L)
//
// La textura DEBE usar filtro 'nearest' (el shader ya samplea pixel-perfecto; con
// 'linear' los pixeles vecinos no son colores vecinos, salen artefactos).
//
// sTD2DInputs[0] = camara en vivo
// sTD2DInputs[1] = Hald CLUT
// uLevel         = L

uniform float uLevel;
uniform float uMezcla;       // intensidad del LUT (0–1)

out vec4 fragColor;

vec3 haldSample(sampler2D lut, float r_i, float g_i, float b_i, float L) {
    float K = L * L;
    float N = L * K;
    float gLow  = mod(g_i, L);
    float gHigh = floor(g_i / L);
    float x = gLow * K + r_i;
    float y = b_i * L + gHigh;
    // TD lee texturas con Y-up; el layout de ffmpeg es Y-down. Invertimos la Y.
    vec2 uv = vec2(x + 0.5, N - y - 0.5) / N;
    return texture(lut, uv).rgb;
}

vec3 haldLookup(vec3 color, sampler2D lut, float L) {
    float K = L * L;
    vec3 c = clamp(color, 0.0, 1.0) * (K - 1.0);
    vec3 cf = floor(c);
    vec3 cc = min(cf + 1.0, K - 1.0);
    vec3 fr = c - cf;

    // 8 esquinas (trilinear)
    vec3 c000 = haldSample(lut, cf.r, cf.g, cf.b, L);
    vec3 c100 = haldSample(lut, cc.r, cf.g, cf.b, L);
    vec3 c010 = haldSample(lut, cf.r, cc.g, cf.b, L);
    vec3 c110 = haldSample(lut, cc.r, cc.g, cf.b, L);
    vec3 c001 = haldSample(lut, cf.r, cf.g, cc.b, L);
    vec3 c101 = haldSample(lut, cc.r, cf.g, cc.b, L);
    vec3 c011 = haldSample(lut, cf.r, cc.g, cc.b, L);
    vec3 c111 = haldSample(lut, cc.r, cc.g, cc.b, L);

    vec3 c00 = mix(c000, c100, fr.r);
    vec3 c10 = mix(c010, c110, fr.r);
    vec3 c01 = mix(c001, c101, fr.r);
    vec3 c11 = mix(c011, c111, fr.r);
    vec3 c0  = mix(c00,  c10,  fr.g);
    vec3 c1  = mix(c01,  c11,  fr.g);
    return     mix(c0,   c1,   fr.b);
}

void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    vec3 looked = haldLookup(src.rgb, sTD2DInputs[1], uLevel);
    // uMezcla: 0 = camara tal cual · 1 = LUT completo (show.Lutmezcla, "LUT intensidad")
    fragColor = vec4(mix(src.rgb, looked, clamp(uMezcla, 0.0, 1.0)), src.a);
}
