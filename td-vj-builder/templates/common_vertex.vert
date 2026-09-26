// Vertex shader pass-through estándar de TouchDesigner para GLSL TOP.
//
// Pasa las coordenadas UV del quad fullscreen al fragment shader y
// proyecta la posición del vértice al espacio de proyección final.
// Equivalente al vertex shader que TD inserta automáticamente cuando
// no se especifica uno custom.
//
// Uso: asignarlo al parámetro "Vertex Shader" del GLSL TOP cuando se
// necesite un vertex shader explícito (ej. para shaders compartidos
// entre TOPs o para servir de base a derivaciones).

void main()
{
    // TDInstanceTexCoord: aplica transform por instancia si lo hay.
    vec3 texcoord = TDInstanceTexCoord(uv[0]);
    vUV.st = texcoord.st;

    // TDPos() devuelve la posición del vértice; TDSOPToProj la proyecta.
    gl_Position = TDSOPToProj(TDPos());
}
