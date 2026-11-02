// 2. CRT Edge Bleed - Austin Psych Fest
// Simula el rastro de fósforo y sangrado de color de un monitor analógico
uniform float uTime;
uniform float uBleedAmount;

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 color = texture(sTD2DInputs[0], uv);
    
    // Desplazamiento cromático para simular convergencia de color analógica
    float red = texture(sTD2DInputs[1], uv - vec2(uBleedAmount, 0.0)).r;
    float green = texture(sTD2DInputs[1], uv).g;
    float blue = texture(sTD2DInputs[1], uv + vec2(uBleedAmount, 0.0)).b;
    
    vec4 feedback = vec4(red, green, blue, 1.0);
    
    // Solo dejar pasar las partes brillantes para el rastro (Edge Enhancement)
    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    float mask = smoothstep(0.4, 0.8, luma);
    
    fragColor = mix(color, feedback * 1.05, 0.92 * mask);
}