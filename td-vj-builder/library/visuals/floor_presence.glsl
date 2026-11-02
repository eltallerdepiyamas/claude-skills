// floor_presence.glsl — visual de prueba para piso LED interactivo 7 x 5 m
// Generativo puro (no usa u_input). Reacciona a hasta 8 posiciones de tracking.
// Cada persona = aura tipo metaball (se fusionan al acercarse) + ondas que salen de ella.
// Capa de calibracion (u_debug): reticula de 1 m, borde del area activa y
// marcador exacto SIN warp en cada posicion, para juzgar precision y estabilidad.

uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // aura A
uniform vec3  u_color2;      // aura B + reticula
uniform vec3  u_color3;      // fondo

// 5 macros en orden de rol
uniform float u_glow;        // 1 intensidad: presencia de aura/ondas
uniform float u_speed;       // 2 velocidad: ondas y warp
uniform float u_warp;        // 3 distorsion: deformacion organica del campo
uniform float u_hue_shift;   // 4 color: rotacion de tono de la paleta por persona
uniform float u_radius;      // 5 firma: radio de influencia por persona (metros)

// extras
uniform float u_debug;       // capa de calibracion 0..1
uniform vec2  u_floor_m;     // tamano real del piso en metros (7, 5)

// personas: xy = posicion normalizada 0..1, z = activa (0/1), w = id
uniform vec4 u_p0;
uniform vec4 u_p1;
uniform vec4 u_p2;
uniform vec4 u_p3;
uniform vec4 u_p4;
uniform vec4 u_p5;
uniform vec4 u_p6;
uniform vec4 u_p7;

out vec4 fragColor;

#define MAXP 8

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i),                 hash21(i + vec2(1.0, 0.0)), u.x),
               mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}

vec3 hueRotate(vec3 c, float h) {
    vec3 hsv = TDRGBToHSV(c);
    hsv.x = fract(hsv.x + h);
    return TDHSVToRGB(hsv);
}

void main() {
    vec2 uv = vUV.st;
    vec2 m  = uv * u_floor_m;                 // trabajamos en metros
    float t = u_time * u_speed;

    // warp de dominio organico (max ~0.6 m), solo afecta aura y ondas
    vec2 w = vec2(noise(m * 0.8 + vec2(t * 0.15, 0.0)),
                  noise(m * 0.8 + vec2(5.2, -t * 0.12))) - 0.5;
    vec2 mw = m + w * u_warp * 1.2;

    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    float energy = clamp(u_bass, 0.0, 2.0);
    float r = max(u_radius, 0.05) * (1.0 + 0.25 * smoothstep(0.0, 1.0, energy));

    float field  = 0.0;
    vec3  tint   = vec3(0.0);
    float wsum   = 0.0;
    float ripple = 0.0;
    float marker = 0.0;

    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;

        vec2 pm = p.xy * u_floor_m;
        float d = length(mw - pm);

        // campo metaball: se suma entre personas -> fusion al acercarse
        float k = (r * r) / (d * d + 0.0025);
        field += k;

        // color estable por ID: si el tracking cambia IDs, el color "salta" (util para detectarlo)
        // cada persona es Color1 o Color2 (sin tonos intermedios: con amarillo/azul ML la mezcla da verdes)
        vec3 c = mix(u_color1, u_color2, step(0.5, fract(p.w * 0.618034)));
        c = hueRotate(c, u_hue_shift);
        tint += c * k;
        wsum += k;

        // ondas concentricas saliendo de cada persona
        float phase = d * 6.0 - t * 3.0 + p.w * 1.7;
        ripple += (0.5 + 0.5 * sin(phase)) * exp(-d / (r * 2.5))
                * smoothstep(r * 0.6, r * 1.2, d);

        // marcador exacto sin warp: anillo de 18 cm + punto central
        float dm = length(m - pm);
        marker += smoothstep(0.03, 0.0, abs(dm - 0.18)) + smoothstep(0.05, 0.0, dm);
    }

    vec3 blob = (wsum > 0.0) ? tint / wsum : u_color1;
    float body = smoothstep(0.8, 1.2, field);     // cuerpo solido de la fusion
    float halo = 1.0 - exp(-field * 0.6);         // resplandor suave alrededor

    vec3 col = u_color3;

    // capa de calibracion: reticula de 1 m + borde del area activa
    vec2 g = abs(fract(m + 0.5) - 0.5);
    float mpp = u_floor_m.x / max(u_res.x, 1.0);  // metros por pixel
    float line = smoothstep(mpp * 1.5, 0.0, min(g.x, g.y));
    vec2 e = min(m, u_floor_m - m);
    float border = smoothstep(mpp * 3.0, 0.0, min(e.x, e.y));
    col += u_color2 * (line * 0.35 + border) * u_debug;

    // aura + ondas
    col += blob * halo * 0.6 * u_glow;
    col  = mix(col, blob * (1.0 + 0.5 * energy), body * clamp(u_glow, 0.0, 1.0));
    col += blob * ripple * 0.35 * u_glow;

    // marcadores exactos encima de todo
    col = mix(col, vec3(1.0), clamp(marker, 0.0, 1.0) * u_debug);

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
