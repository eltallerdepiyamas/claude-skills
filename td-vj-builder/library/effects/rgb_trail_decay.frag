// base40 · rgb_trail_decay (APF 02 — verbatim)
// Decay y desfase independientes por canal RGB.

uniform float uDecayR;
uniform float uDecayG;
uniform float uDecayB;
uniform vec2  uOffsetR;
uniform vec2  uOffsetG;
uniform vec2  uOffsetB;
uniform float uMix;
uniform float uHueDrift;
uniform float uGain;

float nonLinearDecay(float x, float d) {
    return pow(clamp(x, 0.0, 1.0), 1.0 / max(d, 0.001));
}

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    float fbR = texture(sTD2DInputs[1], uv - uOffsetR).r;
    float fbG = texture(sTD2DInputs[1], uv - uOffsetG).g;
    float fbB = texture(sTD2DInputs[1], uv - uOffsetB).b;

    fbR = nonLinearDecay(fbR, uDecayR);
    fbG = nonLinearDecay(fbG, uDecayG);
    fbB = nonLinearDecay(fbB, uDecayB);

    vec3 fb = vec3(fbR, fbG, fbB);

    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    hsv.y = clamp(hsv.y * uGain, 0.0, 1.0);
    fb = TDHSVToRGB(hsv);

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
