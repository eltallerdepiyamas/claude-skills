// base41 · liquid_light_show (APF 08 — EXTENDIDO)
// Oil & water — desplazamiento por luma. Original tenia solo uSpeed+uViscosity,
// se anadieron uMix (era 0.97 hardcoded), uOffsetScale (era 0.003) y uHueDrift
// para que los 5 slots MIDI controlen cosas distintas.

uniform float uTime;
uniform float uSpeed;         // slot 2
uniform float uViscosity;     // slot 3
uniform float uMix;           // slot 1 — reemplaza el 0.97 literal
uniform float uOffsetScale;   // slot 5 — reemplaza el 0.003 literal (firma: escala del oil)
uniform float uHueDrift;      // slot 4 — hue shift del feedback por frame

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;

    vec4 color = texture(sTD2DInputs[0], uv);

    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    float angle = luma * uViscosity + (uTime * uSpeed);
    vec2 offset = vec2(cos(angle), sin(angle)) * uOffsetScale;

    vec4 fb = texture(sTD2DInputs[1], uv + offset);

    // hue drift del feedback
    if (abs(uHueDrift) > 1e-5) {
        vec3 hsv = TDRGBToHSV(fb.rgb);
        hsv.x = fract(hsv.x + uHueDrift);
        fb.rgb = TDHSVToRGB(hsv);
    }

    fragColor = TDOutputSwizzle(mix(color, fb, uMix));
}
