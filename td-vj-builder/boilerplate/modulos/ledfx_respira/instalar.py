# ledfx_respira — RESPIRACION: la luz de las bocinas sube y baja con el compas (BPM detectado). Pulso sin strobe.
# Formas: SUAVE (sube y baja en curva) · LATIDO (sube rapido en el 1 y se va apagando) · OLA (la respiracion corre de
# bocina en bocina: un ciclo cruza todas). Fondo = lo mas bajo que llega (nunca a negro si no se quiere).
# Pagina Respira. Apagado por default. Sin audio_tempo usa 120 BPM. Va al final de la cadena (orden 50).
# Origen: Casa Bacardi x Corona Capital (2026-11-20). Va en led_slices (o led_salida).
exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())

SHADER = r'''// respira_led — la luz sube y baja con el compas
uniform vec4 uRes;     // x on · y forma (0 suave, 1 latido, 2 ola) · z fondo · w fase (ciclos)
out vec4 fragColor;
void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uRes.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    int forma = int(uRes.y + 0.5);
    float ph = uRes.w;
    if (forma == 2) ph -= m.r / max(m.g, 1.0);           // la ola cruza todas las bocinas en un ciclo
    float f = fract(ph);
    float nivel;
    if (forma == 1) nivel = smoothstep(0.0, 0.05, f) * exp(-f * 4.5);   // latido (ataque de 5 %: sin strobe)
    else nivel = 0.5 - 0.5 * cos(6.2831853 * f);                        // suave
    fragColor = TDOutputSwizzle(vec4(src.rgb * mix(uRes.z, 1.0, nivel), 1.0));
}
'''

LIB = r'''# respira_lib — fase de la respiracion (lo escribe modulos/ledfx_respira; no editar aqui)
H = parent()


def fase():
    cada = max(1, int(H.par.Respiracada.eval()))
    t = op('/project2/audio/tempo/tempo_lib')
    if t is not None:
        return t.module.fase() / cada
    return absTime.seconds * 2.0 / cada          # sin tempo: 120 BPM
'''

H, MODO = host()
if H is None:
    print('[fallo] ledfx_respira: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    pg = pagina(H, 'Respira')
    par(H, pg, 'Toggle', 'Respiraon', 'Respiracion prendida', False)
    menu(H, pg, 'Respiraforma', 'Forma', ['suave', 'latido', 'ola'],
         ['Suave (sube y baja)', 'Latido (en el 1 y se apaga)', 'Ola (corre por las bocinas)'], 'suave')
    par(H, pg, 'Int', 'Respiracada', 'Un ciclo cada (tiempos; 4 = un compas)', 4, (1, 16))
    par(H, pg, 'Float', 'Respirafondo', 'Fondo (lo mas bajo)', 0.35, (0.0, 1.0))
    secciones(H, 'Respira', [('Hrespira', 'RESPIRACION', ['Respiraon', 'Respiraforma']),
                             ('Hresritmo', 'RITMO Y NIVEL', ['Respiracada', 'Respirafondo'])])
    lib = nuevo(H, textDAT, 'respira_lib', 2400, 750)
    lib.text = LIB
    dat = nuevo(H, textDAT, 'respira_led_pixel', 2400, 450)
    dat.text = SHADER
    g = nuevo(H, glslTOP, 'respira_led', 2400, 300)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 1
    g.par.vec0name = 'uRes'
    g.par.vec0valuex.expr = 'int(parent().par.Respiraon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Respiraforma.menuIndex'
    g.par.vec0valuez.expr = 'parent().par.Respirafondo'
    g.par.vec0valuew.expr = "op('respira_lib').module.fase() if absTime.frame >= 0 else 0"
    cadena = registrar(H, g, 50, 'Respiraon', 'Respiraforma', 'RESPIRA')
    g.cook(force=True)
    print('[ok] ledfx_respira en %s | cadena %s | errores: %s' % (H.path, cadena, g.errors() or 'ninguno'))
