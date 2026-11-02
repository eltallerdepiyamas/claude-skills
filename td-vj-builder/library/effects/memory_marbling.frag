// base39 · memory_marbling (APF 07 — verbatim)
// Marmol: domain warping recursivo, espirales.

uniform float uWarp1;
uniform float uWarp2;
uniform float uShear;
uniform float uChromaWarp;
uniform float uDecay;
uniform float uMix;
uniform float uContrast;

vec2 rotate2D(vec2 v, float a) {
    float s = sin(a);
    float co = cos(a);
    return mat2(co, -s, s, co) * v;
}

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    vec3 probe1 = texture(sTD2DInputs[1], uv).rgb;
    vec2 disp1  = (probe1.rb - 0.5);

    vec2 uv2 = uv + rotate2D(disp1, uShear) * uWarp1;

    vec3 probe2 = texture(sTD2DInputs[1], uv2).rgb;
    vec2 disp2  = (probe2.rb - 0.5);

    vec2 finalUV = uv2 + rotate2D(disp2, -uShear) * uWarp2;

    vec2 warpDir = rotate2D(disp2, -uShear);
    vec2 perp    = vec2(-warpDir.y, warpDir.x);

    float r = texture(sTD2DInputs[1], finalUV + perp * uChromaWarp).r;
    float g = texture(sTD2DInputs[1], finalUV).g;
    float b = texture(sTD2DInputs[1], finalUV - perp * uChromaWarp).b;

    vec3 fb = vec3(r, g, b);
    fb = (fb - 0.5) * uContrast + 0.5;
    fb *= uDecay;

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = mix(fb, newFrame.rgb, uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
