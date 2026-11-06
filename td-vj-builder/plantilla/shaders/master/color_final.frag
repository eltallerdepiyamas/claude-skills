// color_final.frag — MASTER A NEGRO (blackout) de toda la salida, al final de /project1.
// La correccion de color vive en cada camara en vivo: shaders/master/correccion_camara.frag
uniform float uMaster;       // 0-1
out vec4 fragColor;
void main() {
    vec4 c = texture(sTD2DInputs[0], vUV.st);
    fragColor = TDOutputSwizzle(vec4(c.rgb * clamp(uMaster, 0.0, 1.0), c.a));
}
