// base45 · spectral_mitosis (APF 06 — verbatim)
// Mitosis: division cromatica SOLO en los bordes (content-driven).

uniform float uSplit;
uniform float uAngleSpread;
uniform float uDecay;
uniform float uBreathe;
uniform float uMix;
uniform float uHueDrift;
uniform float uTime;

const vec3 LUMA = vec3(0.299, 0.587, 0.114);

vec2 lumaGradient(sampler2D tex, vec2 uv, vec2 texel) {
    float lx1 = dot(texture(tex, uv + vec2(texel.x, 0.0)).rgb, LUMA);
    float lx2 = dot(texture(tex, uv - vec2(texel.x, 0.0)).rgb, LUMA);
    float ly1 = dot(texture(tex, uv + vec2(0.0, texel.y)).rgb, LUMA);
    float ly2 = dot(texture(tex, uv - vec2(0.0, texel.y)).rgb, LUMA);
    return vec2(lx1 - lx2, ly1 - ly2);
}

vec2 rotate2D(vec2 v, float a) {
    float s = sin(a);
    float co = cos(a);
    return mat2(co, -s, s, co) * v;
}

out vec4 fragColor;

void main() {
    vec2 uv    = vUV.st;
    vec2 texel = 1.0 / vec2(textureSize(sTD2DInputs[1], 0));

    vec2  grad = lumaGradient(sTD2DInputs[1], uv, texel);
    float gmag = length(grad);
    vec2  dir  = (gmag > 1e-4) ? grad / gmag : vec2(1.0, 0.0);

    float scale = uSplit * gmag;
    vec2 dR = rotate2D(dir,  uAngleSpread) * scale;
    vec2 dG = dir * scale;
    vec2 dB = rotate2D(dir, -uAngleSpread) * scale;

    float breath = 1.0 + sin(uTime * 0.6) * uBreathe * 0.012;
    vec2 centered = uv - 0.5;
    vec2 uvBreath = centered * breath + 0.5;

    float r = texture(sTD2DInputs[1], uvBreath + dR).r;
    float g = texture(sTD2DInputs[1], uvBreath + dG).g;
    float b = texture(sTD2DInputs[1], uvBreath + dB).b;

    vec3 fb = vec3(r, g, b) * uDecay;

    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    fb = TDHSVToRGB(hsv);

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
