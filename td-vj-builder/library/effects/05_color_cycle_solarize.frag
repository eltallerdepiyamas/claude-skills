// 5. Color Cycle Solarize - Austin Psych Fest
// Inversión de color basada en brillo y ciclos de matiz
uniform float uTime;
uniform float uThreshold;

out vec4 fragColor;

// Helper para rotación de color
vec3 hueShift(vec3 color, float shift) {
    vec3 k = vec3(0.57735, 0.57735, 0.57735);
    float cosAngle = cos(shift);
    return color * cosAngle + cross(k, color) * sin(shift) + k * dot(k, color) * (1.0 - cosAngle);
}

void main() {
    vec2 uv = vUV.st;
    vec4 color = texture(sTD2DInputs[0], uv);
    vec4 feedback = texture(sTD2DInputs[1], uv);
    
    // Ciclo de color psicodélico
    feedback.rgb = hueShift(feedback.rgb, uTime * 0.5);
    
    // Efecto Solarize
    float luma = dot(feedback.rgb, vec3(0.299, 0.587, 0.114));
    if(luma > uThreshold) {
        feedback.rgb = 1.0 - feedback.rgb;
    }
    
    fragColor = mix(color, feedback, 0.98);
}