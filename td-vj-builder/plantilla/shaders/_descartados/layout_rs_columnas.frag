// layout_rs_columnas.frag — "Partenón" · Little Jesus · Río Salvaje
// Columnas verticales de ancho distinto que cubren el cuadro, como la arquitectura del video de
// "Mala Onda" (Partenón de Zihuatanejo). Cada columna es una rendija sobre UNA cámara (las cámaras
// se reparten cíclicamente), con deriva vertical lenta y sombreado cilíndrico en el fuste.
// Entablamento oscuro arriba y abajo. Cámaras = sTD2DInputs[0..4].

uniform float uTime;
uniform vec2  uResolution;
uniform int   uCamCount;
uniform int   uCamfit;       // 0 Fill · 1 Fit · 2 Stretch
uniform float uCamAspect;

uniform float uShade;        // 1 intensidad · 0–1     sombreado cilíndrico de cada columna
uniform float uSpeed;        // 2 velocidad  · 0–1     deriva vertical (ciclos/s)
uniform float uWidthVar;     // 3 distorsión · 0–1     qué tan distintos son los anchos
uniform float uTone;         // 4 color      · 0–1     piedra cálida al sol
uniform float uColumns;      // 5 firma      · 3–12    número de columnas
uniform float uDrift;        // extra · 0–0.25   amplitud de la deriva vertical
uniform float uGap;          // extra · 0–24 px  separación oscura entre columnas
uniform vec3  uBgColor;      // sombra entre columnas y entablamento

out vec4 fragColor;

// ── ajuste de aspecto de cámara dentro de su celda (0 Fill · 1 Fit · 2 Stretch)
vec2 applyCamFit(vec2 cellUV, float camAspect, float cellAspect, int fitMode) {
    if (fitMode == 2) return cellUV;
    float scaleX = 1.0;
    float scaleY = 1.0;
    float ratio = cellAspect / camAspect;
    if (fitMode == 0) {
        if (ratio > 1.0) scaleY = ratio;
        else             scaleX = 1.0 / ratio;
    } else {
        if (ratio > 1.0) scaleX = 1.0 / ratio;
        else             scaleY = ratio;
    }
    vec2 c = cellUV - 0.5;
    c.x /= scaleX;
    c.y /= scaleY;
    return c + 0.5;
}

// cámara idx en una celda de cellW × cellH píxeles. Fill recorta; Fit deja negro fuera.
vec4 sampleCam(int idx, vec2 localUV, float cellW, float cellH) {
    float cellAspect = cellW / max(cellH, 0.0001);
    vec2 fitUV = applyCamFit(localUV, uCamAspect, cellAspect, uCamfit);
    if (uCamfit != 1) {
        fitUV = clamp(fitUV, 0.0, 1.0);
    } else if (fitUV.x < 0.0 || fitUV.x > 1.0 || fitUV.y < 0.0 || fitUV.y > 1.0) {
        return vec4(0.0, 0.0, 0.0, 1.0);
    }
    if (idx == 0) return texture(sTD2DInputs[0], fitUV);
    if (idx == 1) return texture(sTD2DInputs[1], fitUV);
    if (idx == 2) return texture(sTD2DInputs[2], fitUV);
    if (idx == 3) return texture(sTD2DInputs[3], fitUV);
    if (idx == 4) return texture(sTD2DInputs[4], fitUV);
    return vec4(0.0, 0.0, 0.0, 1.0);
}

// peso (ancho relativo) de la columna k
float colWeight(int k, float wv) {
    return 1.0 + wv * 1.4 * (0.5 + 0.5 * sin(float(k) * 2.1 + 0.7));
}

void main() {
    vec2 p = vUV.st;
    int n = clamp(uCamCount, 2, 5);
    int nCols = int(clamp(floor(uColumns + 0.5), 3.0, 12.0));

    // ancho total en "pesos" y columna a la que pertenece el pixel
    float total = 0.0;
    for (int k = 0; k < 12; k++) {
        if (k < nCols) total += colWeight(k, uWidthVar);
    }
    float x = p.x * total;
    float lastW = colWeight(nCols - 1, uWidthVar);
    int col = nCols - 1;
    float left = total - lastW;
    float wcol = lastW;
    float acc = 0.0;
    for (int k = 0; k < 12; k++) {
        if (k < nCols) {
            float w = colWeight(k, uWidthVar);
            if (x >= acc && x < acc + w) {
                col = k;
                left = acc;
                wcol = w;
            }
            acc += w;
        }
    }
    float local = clamp((x - left) / wcol, 0.0, 1.0);
    float colPx = wcol / total * uResolution.x;
    float edgePx = min(local, 1.0 - local) * colPx;
    float gapMask = smoothstep(uGap * 0.5, uGap * 0.5 + 1.5, edgePx);

    // cámara de esta columna + deriva vertical propia (la escala evita salirse del cuadro)
    int camIdx = col % n;
    float fc = float(col);
    float drift = uDrift * sin(6.28318 * uTime * uSpeed * (0.6 + 0.15 * mod(fc, 5.0)) + fc * 1.9);
    float v = 0.5 + (p.y - 0.5) * (1.0 - 2.0 * uDrift) + drift;
    vec3 c = sampleCam(camIdx, vec2(p.x, v), uResolution.x, uResolution.y).rgb;

    // fuste cilíndrico: claro al centro, oscuro hacia los bordes
    float cyl = cos((local - 0.5) * 3.14159);
    c *= mix(1.0, 0.30 + 0.70 * cyl, uShade);
    c = mix(c, c * vec3(1.10, 1.0, 0.86), uTone);

    vec3 outCol = mix(uBgColor, c, gapMask);

    // entablamento arriba y estilóbato abajo
    float bar = max(smoothstep(0.955, 0.962, p.y), 1.0 - smoothstep(0.040, 0.048, p.y));
    float line = (1.0 - smoothstep(0.0, 0.003, abs(p.y - 0.955)))
               + (1.0 - smoothstep(0.0, 0.003, abs(p.y - 0.045)));
    outCol = mix(outCol, uBgColor, bar);
    outCol += vec3(line * 0.10);

    fragColor = TDOutputSwizzle(vec4(outCol, 1.0));
}
