// base42 · echo_fractal (APF 04 — verbatim)
// Hibrido: espiral cromatica que respira y responde al contenido.

uniform float uDecay;
uniform float uZoom;
uniform float uRotation;
uniform float uChannelSpread;
uniform float uDisplace;
uniform float uHueDrift;
uniform float uMix;

const vec3 LUMA = vec3(0.299, 0.587, 0.114);

vec2 transform(vec2 uv, float zoom, float rotation) {
    vec2  c  = uv - 0.5;
    float s  = sin(rotation);
    float co = cos(rotation);
    c = mat2(co, -s, s, co) * c;
    c *= (1.0 - zoom);
    return c + 0.5;
}

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

    vec2 grad   = lumaGradient(sTD2DInputs[1], uv, texel);
    vec2 perp   = vec2(-grad.y, grad.x);
    vec2 dispUV = perp * uDisplace;

    vec2 uvR = transform(uv + dispUV, uZoom * (1.0 + uChannelSpread), uRotation * (1.0 + uChannelSpread));
    vec2 uvG = transform(uv + dispUV, uZoom,                            uRotation);
    vec2 uvB = transform(uv + dispUV, uZoom * (1.0 - uChannelSpread), uRotation * (1.0 - uChannelSpread));

    float r = texture(sTD2DInputs[1], uvR).r;
    float g = texture(sTD2DInputs[1], uvG).g;
    float b = texture(sTD2DInputs[1], uvB).b;
    vec3  fb = vec3(r, g, b) * uDecay;

    vec3 hsv = TDRGBToHSV(fb);
    hsv.x = fract(hsv.x + uHueDrift);
    fb    = TDHSVToRGB(hsv);

    vec4 newFrame = texture(sTD2DInputs[0], uv);
    vec3 outRGB   = max(fb, newFrame.rgb * uMix);

    fragColor = TDOutputSwizzle(vec4(outRGB, 1.0));
}
