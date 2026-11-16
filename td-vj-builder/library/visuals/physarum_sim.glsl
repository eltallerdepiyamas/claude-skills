// physarum_sim.glsl: un paso de Physarum euleriano (recetario 9; referente Sage Jenson, "Physarum").
// En vez de agentes sueltos, cada celda guarda la MASA de agentes y su direccion. u_pass 0 = sentir el rastro
// con 3 sensores (izq / frente / der) y girar hacia el mas fuerte / u_pass 1 = mover la masa un paso
// (reparto bilineal: conserva la masa, asi se junta en venas), depositar, difundir 3x3 y decaer.
// Estado rgba32float: r = rastro, g = masa, ba = direccion unitaria. Se encadena girar/mover N veces por cuadro.
uniform float u_pass;        // 0 girar / 1 mover
uniform float u_time;
uniform float u_paso;        // celdas por paso (0..1; mas de 1 rompe el reparto 3x3)
uniform float u_giro;        // angulo de giro (rad)
uniform float u_sensor;      // angulo de los sensores (rad): ramificacion
uniform float u_dist;        // distancia de los sensores (px de la simulacion)
uniform float u_deposito;    // rastro que deja cada unidad de masa
uniform float u_decay;       // cuanto queda del rastro por paso (<1)
uniform float u_kick;        // empuja la masa hacia afuera desde el centro (la red respira)
uniform float u_jitter;      // ruido angular (agudos)
out vec4 fragColor;

ivec2 SZ;
ivec2 IJ;
vec4 at(ivec2 ij) { return texelFetch(sTD2DInputs[0], (ij + SZ) % SZ, 0); }   // con vuelta en los bordes
float hash21(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
float sentir(float a) {
    vec2 o = vec2(cos(a), sin(a)) * u_dist;
    return at(IJ + ivec2(floor(o + 0.5))).r;
}

void main() {
    SZ = textureSize(sTD2DInputs[0], 0);
    IJ = ivec2(gl_FragCoord.xy);
    vec4 c = at(IJ);
    float rnd = hash21(vec2(IJ) + vec2(fract(u_time * 0.731) * 917.0, fract(u_time * 0.377) * 613.0));

    if (u_pass < 0.5) {
        // ---- sentir y girar
        float L = length(c.ba);
        float ang = L > 1e-4 ? atan(c.a, c.b) : rnd * 6.2831853;
        if (c.r < 1e-4) ang = rnd * 6.2831853;            // sin rastro: rumbo al azar (arranque y zonas vacias)
        float fF = sentir(ang);
        float fL = sentir(ang + u_sensor);
        float fR = sentir(ang - u_sensor);
        if (fF >= fL && fF >= fR) {
            // sigue derecho
        } else if (fF < fL && fF < fR) {
            ang += (rnd - 0.5) * 2.0 * u_giro;
        } else if (fL > fR) {
            ang += u_giro;
        } else {
            ang -= u_giro;
        }
        ang += (hash21(vec2(IJ.yx) + rnd * 31.0) - 0.5) * u_jitter;
        vec2 nd = vec2(cos(ang), sin(ang));
        // kick: la masa sale hacia afuera desde el centro y la red se vuelve a armar
        vec2 rel = vec2(IJ) - vec2(SZ) * 0.5;
        float rl = length(rel);
        // solo la punta del kick y suave: con 0.85 continuo la masa se iba a los bordes y la pantalla quedaba vacia
        float empuje = smoothstep(0.6, 1.0, u_kick) * 0.25;
        if (rl > 1.0) nd = normalize(mix(nd, rel / rl, empuje) + vec2(1e-5, 0.0));
        fragColor = vec4(c.r, c.g, nd);
    } else {
        // ---- mover (reparto bilineal desde los 8 vecinos), depositar, difundir
        float m = 0.0, mvec = 0.0, tr = 0.0;
        vec2 h = vec2(0.0);
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                vec4 n = at(IJ + ivec2(dx, dy));
                tr += n.r;
                mvec += n.g;
                vec2 dir = n.ba;
                vec2 cae = vec2(float(dx), float(dy)) + dir * u_paso;   // donde cae la masa del vecino (relativo a esta celda)
                vec2 w2 = max(1.0 - abs(cae), 0.0);
                float w = w2.x * w2.y * n.g;
                m += w;
                h += w * dir;
            }
        }
        m = mix(m, mvec / 9.0, 0.03);                       // un poco de presion: la masa no colapsa en un punto
        vec2 nd = length(h) > 1e-5 ? normalize(h) : (length(c.ba) > 1e-4 ? normalize(c.ba) : vec2(1.0, 0.0));
        tr = tr / 9.0 * u_decay + u_deposito * m;
        fragColor = vec4(clamp(tr, 0.0, 60.0), clamp(m, 0.0, 200.0), nd);
    }
}
