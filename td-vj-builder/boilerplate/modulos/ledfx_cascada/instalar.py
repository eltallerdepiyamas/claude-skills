# ledfx_cascada — CASCADA DE TIEMPO: cada bocina ensena el visual unos cuadros despues que la anterior, asi el
# movimiento corre de bocina en bocina como un eco (time glitch ordenado). Va PRIMERO en la cadena (orden 5): el eco es
# del visual limpio y los demas efectos (chaser, barrido, EQ, onda) van encima, sin retraso.
# Como: historia (Texture 3D de la salida de slices, los ultimos cuadros) -> Time Machine con un mapa por bocina
# (cascada_mapa: cuanto atras mira cada una) -> cascada_led (mezcla con lo vivo).
# Orden del retraso: en orden (A-1 sin retraso, la ultima la mas atrasada) · desde el centro · desde los extremos · al azar.
# Pagina Cascada. Apagado por default (apagado guarda solo 2 cuadros: casi no gasta). Memoria: (bocinas - 1) x Retraso + 2
# cuadros de la salida (1920x1080, 8 bits): con 12 bocinas y 2 cuadros, 24 cuadros ~ 200 MB de GPU.
# Origen: Casa Bacardi x Corona Capital (2026-11-20). Va en led_slices (o led_salida).
exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())

MAPA = r'''// cascada_mapa — cuanto atras mira cada bocina (blanco = ahora, negro = lo mas atrasado del Time Machine)
uniform vec4 uCas;     // x orden (0 orden, 1 centro, 2 extremos, 3 azar)
out vec4 fragColor;
float hash(float a) { return fract(sin(a * 12.9898) * 43758.5453); }
void main() {
    vec4 m = texelFetch(sTD2DInputs[0], ivec2(gl_FragCoord.xy), 0);
    if (m.r < -0.5) { fragColor = vec4(1.0); return; }
    float N = max(m.g, 2.0);
    float i = m.r;
    float c = (N - 1.0) * 0.5;
    int o = int(uCas.x + 0.5);
    float f;                                               // 0 = sin retraso, 1 = el maximo
    if (o == 1) f = abs(i - c) / c;
    else if (o == 2) f = 1.0 - abs(i - c) / c;
    else if (o == 3) f = floor(hash(i + 1.0) * (N - 1.0) + 0.5) / (N - 1.0);
    else f = i / (N - 1.0);
    fragColor = vec4(vec3(1.0 - f), 1.0);
}
'''

SHADER = r'''// cascada_led — el visual atrasado por bocina (entrada 2) mezclado con el vivo (entrada 0)
uniform vec4 uCas;     // x on · y mezcla
out vec4 fragColor;
void main() {
    vec4 vivo = texture(sTD2DInputs[0], vUV.st);
    if (uCas.x < 0.5) { fragColor = TDOutputSwizzle(vec4(vivo.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(vivo.rgb, 1.0)); return; }
    vec3 atras = texture(sTD2DInputs[2], vUV.st).rgb;
    fragColor = TDOutputSwizzle(vec4(mix(vivo.rgb, atras, uCas.y), 1.0));
}
'''

H, MODO = host()
if H is None:
    print('[fallo] ledfx_cascada: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    pg = pagina(H, 'Cascada')
    par(H, pg, 'Toggle', 'Cascadaon', 'Cascada de tiempo prendida', False)
    menu(H, pg, 'Cascadaorden', 'El retraso va', ['orden', 'centro', 'extremos', 'azar'],
         ['En orden (A-1 primero)', 'Del centro a los extremos', 'De los extremos al centro', 'Al azar (fijo)'], 'orden')
    par(H, pg, 'Int', 'Cascadaretraso', 'Cuadros entre bocinas', 2, (1, 4))
    par(H, pg, 'Float', 'Cascadamezcla', 'Mezcla (0 vivo, 1 todo eco)', 1.0, (0.0, 1.0))
    secciones(H, 'Cascada', [('Hcascada', 'CASCADA DE TIEMPO', ['Cascadaon', 'Cascadaorden']),
                             ('Hcaslook', 'COMO SE VE', ['Cascadaretraso', 'Cascadamezcla'])])

    dat = nuevo(H, textDAT, 'cascada_led_pixel', 400, 650)
    dat.text = SHADER
    g = nuevo(H, glslTOP, 'cascada_led', 400, 500)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 1
    g.par.vec0name = 'uCas'
    g.par.vec0valuex.expr = 'int(parent().par.Cascadaon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Cascadamezcla'
    cadena = registrar(H, g, 5, 'Cascadaon', 'Cascadaorden', 'CASCADA')

    # historia de lo que entra a la cascada (la salida de los slices sin efectos) y el Time Machine
    hist = nuevo(H, texture3dTOP, 'cascada_hist', 400, 800)
    hist.inputConnectors[0].connect(g.inputs[0])
    hist.par.active.expr = ''
    hist.par.active.mode = ParMode.CONSTANT
    hist.par.active = True                  # siempre con historia (apagada el Time Machine se queja); apagado = 2 cuadros
    hist.par.cachesize.expr = ("2 if not parent().par.Cascadaon else "
                               "(max(2, (int(op('slices').numRows) - 2) * int(parent().par.Cascadaretraso) + 2) "
                               "if op('slices') is not None else 32)")
    if getattr(hist.par, 'format', None) is not None:
        hist.par.format = 'rgba8fixed'
    mdat = nuevo(H, textDAT, 'cascada_mapa_pixel', 600, 950)
    mdat.text = MAPA
    mapa = nuevo(H, glslTOP, 'cascada_mapa', 600, 800)
    mapa.par.pixeldat = mdat.name
    mapa.inputConnectors[0].connect(H.op('indice') or g.inputs[0])
    mapa.par.outputresolution = 'useinput'
    mapa.seq.vec.numBlocks = 1
    mapa.par.vec0name = 'uCas'
    mapa.par.vec0valuex.expr = 'parent().par.Cascadaorden.menuIndex'
    tm = nuevo(H, timemachineTOP, 'cascada_tiempo', 800, 800)
    tm.inputConnectors[0].connect(hist)
    tm.inputConnectors[1].connect(mapa)
    tm.par.blackoffset.expr = "-(max(2, int(op('slices').numRows) - 1) - 1) * int(parent().par.Cascadaretraso) if op('slices') is not None else -22"
    tm.par.whiteoffset = 0
    g.inputConnectors[2].connect(tm)
    g.cook(force=True)
    print('[ok] ledfx_cascada en %s | cadena %s | historia %s cuadros | errores: %s' % (
        H.path, cadena, hist.par.cachesize.eval(), g.errors() or tm.errors() or mapa.errors() or 'ninguno'))
