// ovalos.glsl — base12 · Arco de óvalos (figura del moodboard Mercado Ads, 2026-10-08)
// Alrededor de cada persona gira un anillo de óvalos amarillos translúcidos que se voltean como monedas:
// redondos al frente del arco, cada vez más delgados hacia la cola. Al centro, una esfera lila chica
// con degradado (acento de marca ~5%). Reemplaza a _descartados/petal_bloom. Generativo puro.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform vec3  u_color1;      // amarillo  #FFE600 (óvalos)
uniform vec3  u_color2;      // lila      #AB86FF (esfera central)
uniform vec3  u_color3;      // fondo negro

// 5 macros en orden de rol
uniform float u_intensity;   // 1 intensidad · 0–2    brillo general
uniform float u_speed;       // 2 velocidad  · 0–3    giro del anillo
uniform float u_flip;        // 3 distorsión · 0–1    cuánto se adelgazan los óvalos hacia la cola
uniform float u_core;        // 4 color      · 0–1    esfera lila al centro (0 = sin acento)
uniform float u_count;       // 5 firma      · 6–24   número de óvalos

// extras
uniform float u_radius;      // radio del anillo (m)
uniform float u_arc;         // fracción del círculo que cubre el arco (0.3–1)

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
#define MAXOV 24
#define TAU 6.2831853

// espacio de trabajo: metros con el aspecto de la pantalla (alto = u_floor_m.y) → formas redondas
vec2 aspectM() { return vec2(u_floor_m.y * u_res.x / u_res.y, u_floor_m.y); }

void main() {
    vec2 A = aspectM();
    vec2 q = vUV.st * A;
    float px = u_floor_m.y / u_res.y;
    vec4 P[MAXP] = vec4[MAXP](u_p0, u_p1, u_p2, u_p3, u_p4, u_p5, u_p6, u_p7);

    vec3 col = u_color3 + u_color1 * 0.05 * smoothstep(0.7, 0.0, vUV.t);   // resplandor amarillo abajo
    int n = int(clamp(u_count, 6.0, float(MAXOV)));
    float R = max(u_radius, 0.1);

    for (int i = 0; i < MAXP; i++) {
        vec4 p = P[i];
        if (p.z < 0.5) continue;
        vec2 c = p.xy * A;
        vec2 dq = q - c;
        if (length(dq) > R * 1.6) continue;
        float head = u_time * u_speed * 0.5 + p.w * 2.1;   // ángulo del frente del arco

        // cola primero, frente al final → el frente queda encima (como en el video)
        for (int k = MAXOV - 1; k >= 0; k--) {
            if (k >= n) continue;
            float s = float(k) / float(n - 1);              // 0 frente … 1 cola
            float th = head - s * clamp(u_arc, 0.3, 1.0) * TAU * 0.92;
            vec2 dir = vec2(cos(th), sin(th));
            vec2 tng = vec2(-dir.y, dir.x);
            vec2 l = dq - dir * R;
            vec2 loc = vec2(dot(l, dir), dot(l, tng));      // x = radial (eje largo), y = tangencial

            float a = R * 0.42 * mix(1.0, 0.8, s);
            float turn = smoothstep(0.25, 1.0, s) * u_flip;
            float wob = 0.9 + 0.1 * sin(u_time * 2.0 + float(k) * 0.7 + p.w);
            float b = a * max(mix(1.0, 0.07, turn) * wob, 0.05);
            float e = length(loc / vec2(a, b));
            float aa = fwidth(e) * 1.2 + 1e-4;
            float fill = 1.0 - smoothstep(1.0 - aa, 1.0, e);
            if (fill <= 0.0) continue;

            float g = clamp(loc.y / b, -1.0, 1.0);          // degradado de lado a lado: oscuro → brillante
            vec3 oc = mix(u_color1 * 0.12, u_color1, smoothstep(-0.9, 0.9, g));
            float rim = smoothstep(1.0 - 5.0 * aa, 1.0 - aa, e) * fill;
            oc += mix(u_color1, vec3(1.0), 0.6) * rim * 0.45;
            float alpha = fill * mix(0.85, 0.6, s);         // translúcidos: se ven los traslapes
            col = mix(col, oc * u_intensity, alpha);
        }

        // esfera lila con degradado (claro a la izquierda → oscuro a la derecha), como en el moodboard
        float rc = R * 0.3;
        float dc = length(dq);
        if (u_core > 0.0 && dc < rc + 2.0 * px) {
            float sh = smoothstep(rc * 0.9, -rc * 0.9, dq.x);
            vec3 lc = u_color2 * mix(0.3, 1.0, sh);
            float m = 1.0 - smoothstep(rc - 1.5 * px, rc, dc);
            col = mix(col, lc * u_intensity, m * u_core);
        }
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
