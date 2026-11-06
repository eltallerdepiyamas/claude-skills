// correccion_camara.frag — correccion de lo que muestra cada camara: camN_fuente -> CAM_N (este GLSL) -> SLOT_N.
// Controles: /project2/show -> Correccion de color. Solidos, videos y en vivo si pasan; marcos y fondos de los layouts no.
uniform float uBrillo;       // 0-2    1 = sin cambio
uniform float uContraste;    // 0.5-1.5 1 = sin cambio
uniform float uNegros;       // 0-0.3  lo que quede debajo se va a negro
uniform float uSaturacion;   // 0-2    0 = blanco y negro · 1 = sin cambio
uniform float uBypass;       // 1 = camara tal cual
out vec4 fragColor;
void main() {
    vec4 c = texture(sTD2DInputs[0], vUV.st);
    if (uBypass > 0.5) { fragColor = TDOutputSwizzle(c); return; }
    vec3 rgb = c.rgb * uBrillo;
    rgb = (rgb - 0.5) * uContraste + 0.5;
    float k = clamp(uNegros, 0.0, 0.95);
    rgb = max((rgb - k) / (1.0 - k), 0.0);
    float l = dot(rgb, vec3(0.2126, 0.7152, 0.0722));
    rgb = max(mix(vec3(l), rgb, uSaturacion), 0.0);
    fragColor = TDOutputSwizzle(vec4(rgb, c.a));
}
