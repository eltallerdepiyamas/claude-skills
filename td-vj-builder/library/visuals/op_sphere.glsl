// op_sphere.glsl — base11 · Esfera op-art (figura del moodboard Mercado Ads, 2026-10-08)
// Cada persona lleva una esfera de medias lunas blancas que RUEDA al caminar (giro = desplazamiento / radio)
// y además gira sola con Speed. Rescatada de _descartados/ con la paleta nueva. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600 (Tint)
uniform vec3  u_color2;      // blanco: el patrón op-art del moodboard
uniform vec3  u_color3;      // fondo negro

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–1   presencia de las esferas
uniform float u_speed;       // 2 velocidad  · 0–3   giro propio
uniform float u_twist;       // 3 distorsión · 0–1   torsión del patrón
uniform float u_tint;        // 4 color      · 0–1   patrón blanco → amarillo
uniform float u_cells;       // 5 firma      · 4–24  densidad del patrón

// extras
uniform float u_radius;      // radio de la esfera (m)

// tracking (tdvj_core.build_tracking): xy = posición 0..1, z = activa, w = id
uniform vec2  u_floor_m;
uniform vec4  u_p0;
uniform vec4  u_p1;
uniform vec4  u_p2;
uniform vec4  u_p3;
uniform vec4  u_p4;
uniform vec4  u_p5;
uniform vec4  u_p6;
uniform vec4  u_p7;

out vec4 fragColor;

#define MAXP 8

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

mat3 rotY(float a) { float c = cos(a), s = sin(a); return mat3(c, 0.0, -s, 0.0, 1.0, 0.0, s, 0.0, c); }
mat3 rotX(float a) { float c = cos(a), s = sin(a); return mat3(1.0, 0.0, 0.0, 0.0, c, s, 0.0, -s, c); }

// medias lunas en retícula lat/lon, diagonal alternada tipo tablero
float opPattern(vec3 n, float cells) {
    float lat = asin(clamp(n.y, -1.0, 1.0));
    float lon = atan(n.x, n.z) + u_twist * lat * 2.0;
    vec2 g = vec2(lon / 6.2831853 * cells * 2.0, lat / 3.1415927 * cells);
    vec2 id = floor(g);
    vec2 f = fract(g) - 0.5;
    vec2 dir = mod(id.x + id.y, 2.0) > 0.5 ? vec2(0.7071, 0.7071) : vec2(-0.7071, 0.7071);
    float sd = max(length(f) - 0.56, -dot(f, dir) - 0.08);   // medias lunas grandes: domina el blanco (moodboard)
    float aa = clamp(fwidth(sd), 1e-4, 0.08);   // clamp: evita la línea borrosa en la costura de atan
    return 1.0 - smoothstep(-aa, aa, sd);
}

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    vec3 bg = u_color3 + u_color1 * 0.06 * smoothstep(0.7, 0.0, vUV.t);   // resplandor amarillo abajo
    vec3 col = bg;
    float best = 1e9;
    float cells = floor(u_cells);
    float R = max(u_radius, 0.05) * (1.0 + 0.12 * clamp(u_bass, 0.0, 2.0));

    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 c = p.xy * A;
        float dist = length(q - c);
        if (dist > R + 2.0 * px || dist > best) continue;   // la esfera más cercana queda encima
        best = dist;

        vec2 d = (q - c) / R;
        float r = length(d);
        vec3 n0 = vec3(d, sqrt(max(0.0, 1.0 - r * r)));
        float spin = u_time * u_speed * 0.4 + p.w * 1.3;
        vec3 n = rotX(-c.y / R) * rotY(c.x / R + spin) * n0;

        float pat = opPattern(n, cells);
        vec3 ink = mix(u_color2, u_color1, u_tint) * (0.55 + 0.45 * n0.z);
        vec3 s = mix(u_color3, ink, pat);
        float edge = 1.0 - smoothstep(1.0 - 1.5 * px / R, 1.0, r);
        col = mix(bg, s, edge * u_intensity);
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
