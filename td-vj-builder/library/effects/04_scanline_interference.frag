// 4. Scanline Interference - Austin Psych Fest
// Interferencia de RF y distorsión sinusoidal tipo VHS/Sintetizador de Video
uniform float uTime;
uniform float uFrequency;
uniform float uAmplitude;

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    
    // Distorsión horizontal basada en ondas
    float wave = sin(uv.y * uFrequency + uTime) * uAmplitude;
    vec2 waveUV = vec2(uv.x + wave, uv.y);
    
    vec4 color = texture(sTD2DInputs[0], uv);
    vec4 feedback = texture(sTD2DInputs[1], waveUV);
    
    // Simular ruido de scanline
    float noise = fract(sin(dot(uv + uTime, vec2(12.9898, 78.233))) * 43758.5453);
    feedback.rgb += noise * 0.05;
    
    fragColor = mix(color, feedback, 0.94);
}