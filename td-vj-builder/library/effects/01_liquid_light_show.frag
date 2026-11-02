// 1. Liquid Light Show - Austin Psych Fest
// Simula proyecciones de aceite y agua (Oil & Water)
uniform float uTime;
uniform float uSpeed;
uniform float uViscosity;

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    
    // sTD2DInputs[0] = Video Original
    // sTD2DInputs[1] = Feedback Loop
    vec4 color = texture(sTD2DInputs[0], uv);
    
    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    float angle = luma * uViscosity + (uTime * uSpeed);
    vec2 offset = vec2(cos(angle), sin(angle)) * 0.003;
    
    vec4 feedback = texture(sTD2DInputs[1], uv + offset);
    
    fragColor = mix(color, feedback, 0.97);
}