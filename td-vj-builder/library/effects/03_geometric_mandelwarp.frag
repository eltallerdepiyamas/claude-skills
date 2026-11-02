// 3. Geometric Mandelwarp - Austin Psych Fest
// Feedback fractal basado en rotación y escala infinita
uniform float uTime;
uniform float uRotation;
uniform float uScale;

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 color = texture(sTD2DInputs[0], uv);
    
    // Transformación de coordenadas de feedback
    vec2 centeredUV = uv - 0.5;
    float s = sin(uRotation);
    float c = cos(uRotation);
    mat2 rot = mat2(c, -s, s, c);
    
    vec2 warpedUV = (centeredUV * rot) * uScale + 0.5;
    vec4 feedback = texture(sTD2DInputs[1], warpedUV);
    
    // Inversión rítmica de color (Solarización)
    if(length(feedback.rgb) > 0.95) feedback.rgb = 1.0 - feedback.rgb;
    
    fragColor = mix(color, feedback, 0.95);
}