// reaccion.glsl: pinta la reaccion-difusion (sTD2DInputs[0], g = V) como relieve con contorno.
// Patrones organicos tipo coral / laberinto que crecen; el kick siembra nuevos focos.
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
uniform float u_high;
uniform vec3  u_color1;
uniform vec3  u_color2;
uniform vec3  u_color3;
uniform float u_intensity;
uniform float u_speed;
uniform float u_warp;
uniform float u_tono;
uniform float u_firma;
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec2 px = uTD2DInfos[0].res.xy;
    float v  = texture(sTD2DInputs[0], uv).g;
    float vx = texture(sTD2DInputs[0], uv + vec2(px.x, 0)).g - texture(sTD2DInputs[0], uv - vec2(px.x, 0)).g;
    float vy = texture(sTD2DInputs[0], uv + vec2(0, px.y)).g - texture(sTD2DInputs[0], uv - vec2(0, px.y)).g;
    vec3 n = normalize(vec3(-vx * 6.0, -vy * 6.0, 1.0));
    float luz = clamp(dot(n, normalize(vec3(-0.4, 0.5, 0.75))), 0.0, 1.0);
    float masa = smoothstep(0.12, 0.32, v);
    float contorno = 1.0 - smoothstep(0.0, 0.035, abs(v - 0.2));
    float brillo = pow(luz, 12.0) * masa;
    vec3 tono = mix(u_color1, u_color2, u_tono);
    float hi = clamp(u_high, 0.0, 2.0);
    vec3 col = tono * masa * (0.18 + 0.35 * luz)
             + tono * contorno * (0.8 + 0.4 * clamp(u_bass, 0.0, 1.5))
             + mix(tono, vec3(1.0), 0.3) * brillo * (0.35 + 0.4 * hi);
    col = u_color3 + col * u_intensity;
    vec2 q = uv - 0.5;
    col *= 1.0 - 0.6 * dot(q, q);
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
