// slit_scan.glsl: pinta con la paleta la salida del Time Machine (sTD2DInputs[0], en grises).
uniform float u_time;
uniform vec2  u_res;
uniform float u_bass;
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
    float l = texture(sTD2DInputs[0], uv).r;
    vec3 tono = mix(u_color1, u_color2, u_tono);
    vec3 col = tono * l * 0.85 + mix(tono, vec3(1.0), 0.3) * pow(clamp(l, 0.0, 1.5), 4.0) * 0.25;
    col = u_color3 + col * u_intensity;
    fragColor = TDOutputSwizzle(vec4(max(col, 0.0), 1.0));
}
