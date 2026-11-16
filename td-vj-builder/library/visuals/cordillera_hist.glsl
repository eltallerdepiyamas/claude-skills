// cordillera_hist.glsl: memoria del audio. Textura de 1 x 128; cada cuadro todo sube una fila
// y la fila 0 guarda el audio de ahora (low, mid, high, kick). La usa cordillera.glsl.
uniform vec4 u_now;
out vec4 fragColor;
void main() {
    float h = uTD2DInfos[0].res.w;
    if (vUV.t * h < 1.0)
        fragColor = u_now;
    else
        fragColor = texture(sTD2DInputs[0], vUV.st - vec2(0.0, 1.0 / h));
}
