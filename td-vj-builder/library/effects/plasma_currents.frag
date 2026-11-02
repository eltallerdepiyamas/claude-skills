// base44 · plasma_currents (APF 05 — verbatim)
// Filamentos: corriente + presion, plasma solar.

uniform float uCurrent;
uniform float uPressure;
uniform float uDecay;
uniform float uChromaFlow;
uniform float uContrast;
uniform float uMix;
uniform float uTime;

const vec3 LUMA = vec3(0.299, 0.587, 0.114);

vec2 lumaGradient(sampler2D tex, vec2 uv, vec2 texel) {
    float lx1 = dot(texture(tex, uv + vec2(texel.x, 0.0)).rgb, LUMA);
    float lx2 = dot(texture(tex, uv - vec2(texel.x, 0.0)).rgb, LUMA);
    float ly1 = dot(texture(tex, uv + vec2(0.0, texel.y)).rgb, LUMA);
    float ly2 = dot(texture(tex, uv - vec2(0.0, texel.y)).rgb, LUMA);
    return vec2(lx1 - lx2, ly1 - ly2);
}

out vec4 fragColor;

void main() {
    vec2 uv    = vUV.st;
    vec2 texel = 1.0 / vec2(textureSize(sTD2DInputs[1], 0));

    vec2 grad = lumaGradient(sTD2DInputs[1], uv, texel);
    vec2 perp = vec2(-grad.y, grad.x);

    float t = uTime * 0.17;
    vec2 baseDrift = vec2(sin(t), cos(t * 1.31)) * 0.0007;

    vec2 flowBase = perp * uCurrent + grad * uPressure + baseDrift;
    vec2 flowR = flowBase * (1.0 + uChromaFlow);
    vec2 flowG = flowBase;
    vec2 flowB = flowBase * (1.0 - uChromaFlow);

    float r = texture(sTD2DInputs[1], uv + flowR).r;
    float g = texture(sTD2DInputs[1], uv + flowG).g;
    float b = texture(sTD2DInputs[1], uv + flowB).b;

    vec3 fb = vec3(r, g, b);
    fb = (fb - 0.5) * uContrast + 0.5;
    fb *= uDecay;

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
