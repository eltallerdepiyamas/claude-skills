// base38 · liquid_memory (APF 03 — verbatim)
// Deformacion siguiendo isolineas de luminancia del feedback.

uniform float uDisplace;
uniform float uDecay;
uniform float uFlow;
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
    vec2 drift = vec2(sin(uTime * 0.3), cos(uTime * 0.21)) * uFlow;
    vec2 fbUV = uv + perp * uDisplace + drift;

    vec4 fb = texture(sTD2DInputs[1], fbUV);
    fb.rgb  = (fb.rgb - 0.5) * uContrast + 0.5;
    fb.rgb *= uDecay;

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec4 color    = mix(fb, newFrame, uMix);

    fragColor = TDOutputSwizzle(color);
}
