# ledfx_eq — EQ DE BOCINAS: cada slice / tablero es una banda del espectro y se prende con ella (segunda capa).
# Con 12 bocinas = ecualizador de 12 bandas, de graves a agudos en el orden del XML (o al reves, o graves al centro).
# Cada banda con su propio autonivel (los agudos tambien se mueven) y caida suave (sin parpadeo).
# Modos: BRILLO (la bocina se prende con su banda; lo apagado queda en Fondo) · ANILLO (aro de luz que crece desde el
# centro de la bocina) · NIVEL (se llena de abajo hacia arriba, como un VU).
# Audio: Audio Spectrum (log, 128 puntos juntados en una banda por bocina) del audio mono del show (Eqfuente). Pagina EQ. Apagado por default.
# Origen: Casa Bacardi x Corona Capital (2026-11-20). Va en led_slices (o led_salida). Orden en la cadena 30.
exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())

SHADER = r'''// eq_led — cada bocina (slice / tablero) se prende con su banda del espectro
uniform vec4 uEq;      // x on · y modo (0 brillo, 1 anillo, 2 nivel) · z fondo · w intensidad
uniform vec4 uCfg;     // x orden (0 graves->agudos, 1 agudos->graves, 2 graves al centro)
uniform vec4 uTinta;
out vec4 fragColor;

void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uEq.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);      // indice: slice, cuantos, u, v
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    float N = max(m.g, 1.0);
    float i = m.r;
    float b = i;                                                           // posicion en el espectro 0..N-1
    if (uCfg.x > 1.5) b = abs(i - (N - 1.0) * 0.5) * 2.0;                  // graves al centro
    else if (uCfg.x > 0.5) b = N - 1.0 - i;
    int nb = textureSize(sTD2DInputs[2], 0).x;
    int k = int(clamp(floor(b / max(N - 1.0, 1.0) * float(nb - 1) + 0.5), 0.0, float(nb - 1)));
    float L = clamp(texelFetch(sTD2DInputs[2], ivec2(k, 0), 0).r, 0.0, 1.0);
    vec2 lu = m.ba;
    vec3 tinta = uTinta.rgb;
    vec3 col;
    int modo = int(uEq.y + 0.5);
    if (modo == 0) {                                       // BRILLO
        col = src.rgb * mix(uEq.z, 1.0, L) + tinta * L * L * 0.12 * uEq.w;
    } else if (modo == 1) {                                // ANILLO
        float r = length(lu - 0.5) * 2.0;
        float rad = 0.25 + 0.7 * L;
        float aro = exp(-pow((r - rad) / 0.045, 2.0)) * smoothstep(0.02, 0.15, L);
        col = src.rgb * mix(uEq.z, 1.0, L) + tinta * aro * uEq.w;
    } else {                                               // NIVEL (VU de abajo hacia arriba)
        float dentro = 1.0 - smoothstep(L - 0.01, L + 0.01, lu.y);
        float linea = exp(-abs(lu.y - L) * 90.0) * step(0.02, L);
        col = src.rgb * mix(uEq.z, 1.0, dentro) + tinta * (dentro * 0.10 + linea * 0.9) * uEq.w;
    }
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

SCRIPT = r'''# eq_bandas — 12 (o N) bandas del espectro con autonivel por banda y caida suave (lo escribe ledfx_eq)
import numpy as np


def onSetupParameters(scriptOp):
    return


def onCook(scriptOp):
    H = scriptOp.parent()
    a = scriptOp.inputs[0].numpyArray() if scriptOp.inputs else None
    if a is None or a.size == 0:
        scriptOp.clear()
        return
    full = np.abs(a[0]).astype('float32')                             # espectro log (128 puntos)
    t = H.op('slices')
    n = max(1, t.numRows - 1) if t is not None and t.numRows > 1 else 12  # una banda por bocina
    x = np.array([seg.mean() for seg in np.array_split(full, n)], dtype='float32')
    env = H.fetch('eq_env', None, search=False)
    pico = H.fetch('eq_pico', None, search=False)
    if env is None or env.size != n:
        env, pico = np.zeros(n, 'float32'), np.full(n, 1e-4, 'float32')
    sube, baja = 0.6, 1.0 - min(0.5, 1.0 / max(1.0, H.par.Eqcaida.eval() * 60.0))
    env = np.where(x > env, env + (x - env) * sube, env * baja)
    pico = np.maximum(pico * 0.9995, np.maximum(env, 1e-4))              # techo que baja lento (~1 min)
    H.store('eq_env', env)
    H.store('eq_pico', pico)
    y = np.clip((env / pico) * H.par.Eqganancia.eval(), 0.0, 1.0)
    y = np.clip((y - H.par.Eqpiso.eval()) / max(1e-3, 1.0 - H.par.Eqpiso.eval()), 0.0, 1.0)
    scriptOp.clear()
    scriptOp.numSamples = n
    c = scriptOp.appendChan('banda')
    c.vals = y.tolist()
    return
'''

H, MODO = host()
if H is None:
    print('[fallo] ledfx_eq: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    pg = pagina(H, 'EQ')
    par(H, pg, 'Toggle', 'Eqon', 'EQ de bocinas prendido', False)
    menu(H, pg, 'Eqmodo', 'Como se ve', ['brillo', 'anillo', 'nivel'],
         ['Brillo (la bocina se prende)', 'Anillo que crece', 'Nivel (VU de abajo arriba)'], 'brillo')
    menu(H, pg, 'Eqorden', 'Bandas', ['graves', 'agudos', 'centro'],
         ['Graves -> agudos (en orden)', 'Agudos -> graves', 'Graves al centro'], 'graves')
    par(H, pg, 'Float', 'Eqfondo', 'Fondo (lo apagado)', 0.25, (0.0, 1.0))
    par(H, pg, 'Float', 'Eqint', 'Intensidad de la luz', 1.0, (0.0, 2.0))
    menu(H, pg, 'Eqtinta', 'Tinta', ['a', 'b', 'blanco'], ['Color A (paleta)', 'Color B (paleta)', 'Blanco'], 'a')
    par(H, pg, 'Float', 'Eqganancia', 'Ganancia', 1.0, (0.3, 3.0))
    par(H, pg, 'Float', 'Eqpiso', 'Piso (debajo no prende)', 0.15, (0.0, 0.8))
    par(H, pg, 'Float', 'Eqcaida', 'Caida (s)', 0.25, (0.05, 1.5))
    if not hasattr(H.par, 'Eqfuente'):
        pg.appendCHOP('Eqfuente', label='Audio (mono)')
        H.par.Eqfuente = '/project2/audio/audio_gain' if op('/project2/audio/audio_gain') else ''
    secciones(H, 'EQ', [('Heq', 'EQ DE BOCINAS', ['Eqon', 'Eqmodo', 'Eqorden']),
                        ('Heqlook', 'COMO SE VE', ['Eqfondo', 'Eqint', 'Eqtinta']),
                        ('Heqaudio', 'AUDIO', ['Eqganancia', 'Eqpiso', 'Eqcaida', 'Eqfuente'])])

    sel = nuevo(H, selectCHOP, 'eq_audio', 1200, 600)
    sel.par.chops.expr = 'parent().par.Eqfuente'
    esp = nuevo(H, audiospectrumCHOP, 'eq_espectro', 1400, 600)
    esp.inputConnectors[0].connect(sel)
    esp.par.mode = 'visual'
    esp.par.frequencylog = 1.0
    om = esp.par.outputmenu
    om.val = next((n for n in om.menuNames if 'manual' in n.lower()), om.eval())
    esp.par.outlength.expr = ''
    esp.par.outlength.mode = ParMode.CONSTANT
    esp.par.outlength = 128                 # minimo del CHOP; eq_bandas lo junta en una banda por bocina
    sc_dat = nuevo(H, textDAT, 'eq_bandas_cb', 1600, 750)
    sc_dat.text = SCRIPT
    sc = nuevo(H, scriptCHOP, 'eq_bandas', 1600, 600)
    sc.par.callbacks = sc_dat
    sc.inputConnectors[0].connect(esp)
    tex = nuevo(H, choptoTOP, 'eq_tex', 1800, 600)
    tex.par.chop = sc
    if getattr(tex.par, 'dataformat', None) is not None:
        tex.par.dataformat = 'r'
    if getattr(tex.par, 'format', None) is not None:
        tex.par.format = 'r32float'
    H.unstore('eq_env')
    H.unstore('eq_pico')

    dat = nuevo(H, textDAT, 'eq_led_pixel', 1800, 450)
    dat.text = SHADER
    g = nuevo(H, glslTOP, 'eq_led', 1800, 300)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 3
    g.par.vec0name = 'uEq'
    g.par.vec0valuex.expr = 'int(parent().par.Eqon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Eqmodo.menuIndex'
    g.par.vec0valuez.expr = 'parent().par.Eqfondo'
    g.par.vec0valuew.expr = 'parent().par.Eqint'
    g.par.vec1name = 'uCfg'
    g.par.vec1valuex.expr = 'parent().par.Eqorden.menuIndex'
    g.par.vec2name = 'uTinta'
    tinta_exprs(g, 'vec2', 'Eqtinta')
    cadena = registrar(H, g, 30, 'Eqon', 'Eqmodo', 'EQ')
    g.inputConnectors[2].connect(tex)
    if MODO == 'slices':
        orden_paginas(H, ['Salida', 'Efectos', 'Capa', 'Chaser', 'Barrido', 'EQ', 'Onda', 'Cascada', 'Giro', 'Respira', 'Slices', 'LED', 'Banner'])
    g.cook(force=True)
    print('[ok] ledfx_eq en %s | cadena %s | bandas %d | errores: %s' % (
        H.path, cadena, esp.numSamples, g.errors() or sc.errors() or 'ninguno'))
