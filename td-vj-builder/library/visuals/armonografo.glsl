// armonografo.glsl: plumas que dibujan curvas de armonografo 3D (suma de pendulos) que giran lento;
// la estela larga (feedback) deja el dibujo como de laser. Las razones de frecuencia se desafinan
// poco a poco (Distorsion) y el dibujo cambia de forma sin cortes. sTD2DInputs[0] = cuadro anterior.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_low;
uniform float u_high;
uniform float u_kick;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;        // 3 distorsion: desafinacion de los pendulos (forma)
uniform float u_tono;
uniform float u_firma;       // 5 firma: numero de plumas
uniform float u_estela;      // extra: cuanto dura el trazo
uniform float u_paso;        // segundos de este cuadro (absTime.stepSeconds): tramo continuo a cualquier fps
out vec4 fragColor;

vec3 pluma(float t, float k) {
    float d = u_warp * 0.02 * sin(u_time * 0.03 + k);
    vec3 f1 = vec3(2.0, 3.0, 5.0) + vec3(0.003, -0.002, 0.004) + d;
    vec3 f2 = vec3(3.0, 2.0, 4.0) + vec3(-0.001, 0.002, 0.001) - d;
    vec3 ph = vec3(0.0, 1.57, 0.7) + k * vec3(0.9, 0.4, 1.3);
    return 0.55 * sin(f1 * t + ph) + 0.35 * sin(f2 * t * 1.003 + ph.yzx);
}

vec2 proyecta(vec3 q, float ang) {
    float c = cos(ang), s = sin(ang);
    q.xz = mat2(c, -s, s, c) * q.xz;
    float c2 = cos(0.35), s2 = sin(0.35);
    q.yz = mat2(c2, -s2, s2, c2) * q.yz;
    return q.xy * (1.6 / (2.6 + q.z));
}

float segmento(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-8), 0.0, 1.0);
    return length(pa - ba * h);
}

void main() {
    vec2 uv = vUV.st;
    float asp = u_res.x / u_res.y;
    vec2 p = vec2((uv.x - 0.5) * asp, uv.y - 0.5) * 2.0;
    float lo = clamp(max(u_bass, u_low), 0.0, 2.0);
    float hi = clamp(u_high, 0.0, 2.0);
    float k = clamp(u_kick, 0.0, 1.0);
    float t = u_time * (0.4 + 1.2 * u_speed);
    // se dibujan los ultimos 4 cuadros (con traslape): si TD se salta un cuadro el trazo no se corta
    float dt = (0.4 + 1.2 * u_speed) * clamp(u_paso, 0.004, 0.1) * 4.0;
    float ang = u_time * 0.07;
    float N = floor(clamp(u_firma, 1.0, 6.0));
    float px = 2.0 / u_res.y;
    float w = px * (0.9 + 0.8 * lo + 1.2 * k);
    float L = 0.0, cabeza = 0.0;
    for (int i = 0; i < 6; i++) {
        float fi = float(i);
        if (fi >= N) break;
        vec2 prev = proyecta(pluma(t - dt, fi), ang);
        for (int s = 1; s <= 16; s++) {                      // el tramo, en 16 pedazos
            vec2 cur = proyecta(pluma(t - dt + dt * float(s) / 16.0, fi), ang);
            float d = segmento(p, prev, cur);
            L += 1.0 - smoothstep(w * 0.5, w * 1.5, d);
            prev = cur;
        }
        float dh = length(p - prev);
        cabeza += exp(-dh * dh / (px * px * (10.0 + 30.0 * k)));
    }
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 nuevo = (tono * min(L, 1.0) * (0.7 + 0.5 * lo) + mix(tono, vec3(1.0), 0.45) * cabeza * (0.6 + 0.6 * hi)) * u_intensity;
    vec3 prevc = texture(sTD2DInputs[0], uv).rgb;
    vec3 col = max(prevc * u_estela, nuevo);
    col = min(col + u_color3, vec3(1.4));
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
