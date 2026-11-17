# led_salida — saca el mapeo LED a la pantalla del procesador, separado de la UI.
#   /perform     = UI de operacion (no se toca)
#   /salida_led  = ventana -> /project1/led/lienzo_led -> monitor del procesador LED
# Cadena en /project1/led:
#   master_banner -> fuente_led (o pixel map de prueba) -> [efectos ledfx_* en orden] -> lienzo_led_glsl -> lienzo_led
#                                                                                   \-> linea_led (vista en linea, UI)
#   lienzo_led: lienzo negro (Lienzow x Lienzoh = resolucion del monitor del procesador) con el mapeo pegado 1:1
#   en Posx, Posy (px desde arriba-izquierda).
# Pagina LED: Salida LED armada · Abrir / Cerrar ventana LED · Patron de prueba · Pixel map · Lienzo · X / Y ·
#   Monitor · Vista en la UI.
# Ventana: con monitor externo SIEMPRE ahi (pantalla completa, sin barra, encima, sin cursor, Esc no la cierra);
#   sin externo, ventana de prueba con barra en la lap (Esc la cierra).
# Armada (Abrir la arma, Cerrar la desarma): led_vigia cada 2 s y al arrancar el proyecto la abre / pasa al externo,
#   y si el externo se pierde la cierra y espera a que vuelva. Log en control/led_log.txt.
# MODO SHOW (show.Modoshow) apaga el patron de prueba. La UI (pestana SALIDA LED + chip) la pone ui.py.
# led_cadena.encadenar(): conecta los TOPs con tag 'ledfx' por su 'orden' (los ledfx_* la llaman al instalarse).
# Requiere led_mapeo. Modulo del boilerplate: modulos/led_salida.
import json, os

B = op('/project1/led')

SHADER = r'''// lienzo_led — pega la entrada 1:1 en (uPos.x, uPos.y) desde arriba-izquierda; lo demas negro
uniform vec4 uPos;
out vec4 fragColor;
void main() {
    ivec2 res = ivec2(uTDOutputInfo.res.zw);
    ivec2 tam = ivec2(uTD2DInfos[0].res.zw);
    ivec2 p = ivec2(gl_FragCoord.xy);
    ivec2 loc = ivec2(p.x - int(uPos.x), (res.y - 1 - p.y) - int(uPos.y));
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);
    if (loc.x >= 0 && loc.y >= 0 && loc.x < tam.x && loc.y < tam.y)
        col = texelFetch(sTD2DInputs[0], ivec2(loc.x, tam.y - 1 - loc.y), 0);
    col.a = 1.0;
    fragColor = TDOutputSwizzle(col);
}
'''

LINEA = r'''// linea_led — el mapeo apilado (fila de arriba primero) desenrollado: todos los tableros en una linea
uniform vec4 uGrid;   // x columnas, y filas, z px por tablero
out vec4 fragColor;
void main() {
    float COLS = max(uGrid.x, 1.0);
    float ROWS = max(uGrid.y, 1.0);
    float N = COLS * ROWS;
    vec2 uv = vUV.st;
    float idx = floor(uv.x * N);
    vec2 lu = vec2(fract(uv.x * N), uv.y);
    float c = mod(idx, COLS);
    float rTop = floor(idx / COLS);
    vec2 s = vec2((c + lu.x) / COLS, (ROWS - 1.0 - rTop + lu.y) / ROWS);
    vec3 col = texture(sTD2DInputs[0], s).rgb;
    float T = max(uGrid.z, 2.0);
    vec2 px = lu * T;                                     // guia de 1 px entre tableros
    float borde = step(px.x, 1.0) + step(T - 1.0, px.x);
    col = mix(col, vec3(0.35), clamp(borde, 0.0, 1.0) * 0.8);
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

CADENA = r'''# led_cadena — orden de los efectos LED (lo escribe modulos/led_salida; no editar aqui)
def encadenar():
    B = parent()
    fx = sorted([o for o in B.children if o.isTOP and 'ledfx' in o.tags],
                key=lambda o: (o.fetch('orden', 50, search=False), o.name))
    prev = B.op('fuente_led')
    for f in fx:
        f.inputConnectors[0].connect(prev)
        prev = f
    for n in ('lienzo_led_glsl', 'linea_led_glsl'):
        if B.op(n) is not None:
            B.op(n).inputConnectors[0].connect(prev)
    return [f.name for f in fx]
'''

VENTANA = r'''# led_ventana — coloca /salida_led: monitor externo si hay (show), si no ventana de prueba en la lap.
def _pon(w, nombre, valor):
    p = getattr(w.par, nombre, None)
    if p is not None:
        p.val = valor


def colocar(abrir=True):
    w = op('/salida_led')
    B = parent()
    if w is None:
        return
    sec = externos()
    if sec:
        if int(B.par.Monitor.eval()) not in sec:
            B.par.Monitor = sec[0]
        m = monitors[int(B.par.Monitor.eval())]
        _pon(w, 'justifyoffsetto', 'specifymonitor')
        _pon(w, 'size', 'fill')
        _pon(w, 'borders', False)
        _pon(w, 'alwaysontop', True)
        _pon(w, 'cursorvisible', 'nocursor')
        _pon(w, 'closeescape', False)
        donde = 'monitor externo %d (%dx%d)' % (B.par.Monitor.eval(), m.width, m.height)
    else:
        m = monitors[0]
        k = min(1.0, 0.8 * m.width / max(1, B.par.Lienzow.eval()), 0.8 * m.height / max(1, B.par.Lienzoh.eval()))
        _pon(w, 'justifyoffsetto', 'primarymonitor')
        _pon(w, 'size', 'custom')
        _pon(w, 'winw', int(B.par.Lienzow.eval() * k))
        _pon(w, 'winh', int(B.par.Lienzoh.eval() * k))
        _pon(w, 'winoffsetx', 0)
        _pon(w, 'winoffsety', 0)
        _pon(w, 'borders', True)
        _pon(w, 'alwaysontop', False)
        _pon(w, 'cursorvisible', 'alwaysvisible')
        _pon(w, 'closeescape', True)
        donde = 'la lap, ventana de prueba %dx%d (no hay monitor externo)' % (w.par.winw.eval(), w.par.winh.eval())
    if abrir:
        if w.isOpen:
            w.par.winclose.pulse()
            run("op('/salida_led').par.winopen.pulse()", delayFrames=3)
        else:
            w.par.winopen.pulse()
    print('[salida_led] ' + donde)
    return donde


def log(txt):
    import time
    linea = time.strftime('%Y-%m-%d %H:%M:%S') + '  ' + txt
    print('[salida_led] ' + txt)
    try:
        with open(project.folder + '/control/led_log.txt', 'a', encoding='utf-8') as f:
            f.write(linea + chr(10))
    except Exception:
        pass


def externos():
    return [i for i, m in enumerate(monitors) if not m.isPrimary]


def modo_show(w):
    return not bool(w.par.borders.eval())      # sin bordes = puesta en el externo


def vigilar():
    """Cada 2 s (led_vigia). Con la salida ARMADA: si hay externo y la ventana no esta ahi, la pone;
    si el externo se pierde, la cierra y espera a que vuelva. La ventana de prueba en la lap no se toca."""
    B = parent()
    w = op('/salida_led')
    if w is None or not B.par.Ledarmada.eval():
        return
    sec = externos()
    if sec:
        if not w.isOpen:
            log('abre la salida LED en el externo (estaba cerrada)')
            colocar(True)
        elif not modo_show(w) or int(B.par.Monitor.eval()) not in sec:
            log('pasa la salida LED al externo')
            colocar(True)
    elif w.isOpen and modo_show(w):
        log('se perdio la pantalla externa: cierra y espera a que vuelva')
        w.par.winclose.pulse()


def estado():
    """(texto, nivel) para el chip de la UI. nivel: 0 apagada · 1 ok · 2 prueba / aviso · 3 sin senal"""
    B = parent()
    w = op('/salida_led')
    abierta = w is not None and w.isOpen
    en_ext = abierta and modo_show(w) and bool(externos())
    if B.par.Prueba.eval() and abierta:
        return ('LED · PRUEBA', 2)
    if B.par.Ledarmada.eval():
        if en_ext:
            return ('LED · AL AIRE', 1)
        if not externos():
            return ('LED · SIN PANTALLA', 3)
        return ('LED · ABRIENDO', 2)
    if abierta:
        return ('LED · PRUEBA LAP' if not en_ext else 'LED · NO ARMADA', 2)
    return ('LED · APAGADA', 0)
'''


def nuevo(comp, tipo, nombre, x, y):
    o = comp.op(nombre)
    if o is None:
        o = comp.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def pon(o, nombre, valor):
    p = getattr(o.par, nombre, None)
    if p is None:
        print('[aviso] %s no tiene %s' % (o.path, nombre))
        return False
    p.val = valor
    return True


def config_proyecto():
    ruta = project.folder + '/proyecto.json'
    try:
        return json.load(open(ruta, encoding='utf-8')).get('led', {}) if os.path.exists(ruta) else {}
    except Exception:
        return {}


if B is None or B.op('master_banner') is None:
    print('[fallo] falta /project1/led: instala antes led_mapeo')
else:
    cfg = config_proyecto()
    pg = next((p for p in B.customPages if p.name == 'LED'), None) or B.appendCustomPage('LED')
    ancho = B.par.Columnas.eval() * B.par.Tablero.eval()
    alto = B.par.Filas.eval() * B.par.Tablero.eval()
    for nombre, etiqueta, default in (('Lienzow', 'Lienzo ancho', cfg.get('lienzo_w', ancho)),
                                      ('Lienzoh', 'Lienzo alto', cfg.get('lienzo_h', alto)),
                                      ('Posx', 'Banner X', cfg.get('x', 0)), ('Posy', 'Banner Y', cfg.get('y', 0))):
        if not hasattr(B.par, nombre):
            pg.appendInt(nombre, label=etiqueta)
            getattr(B.par, nombre).default = default
            getattr(B.par, nombre).val = default
    B.par.Lienzow.normMax = B.par.Lienzoh.normMax = 3840
    B.par.Posx.normMax = B.par.Posy.normMax = 1920
    if not hasattr(B.par, 'Prueba'):
        pg.appendToggle('Prueba', label='Patron de prueba (pixel map)')
    if not hasattr(B.par, 'Pixelmap'):
        pg.appendFile('Pixelmap', label='Pixel map')
        B.par.Pixelmap.val = cfg.get('pixelmap', '')
    if not hasattr(B.par, 'Monitor'):
        pg.appendInt('Monitor', label='Monitor LED')
    B.par.Monitor.default = 1
    if B.par.Monitor.eval() == 0:
        B.par.Monitor.val = 1      # 0 = principal (UI); la LED va al secundario
    B.par.Monitor.normMax = 4
    if not hasattr(B.par, 'Abrirled'):
        pg.appendPulse('Abrirled', label='Abrir ventana LED')
        pg.appendPulse('Cerrarled', label='Cerrar ventana LED')
    if not hasattr(B.par, 'Ledarmada'):
        pg.appendToggle('Ledarmada', label='Salida LED armada')
        B.par.Ledarmada.default = False
    if not hasattr(B.par, 'Vistaui'):
        pg.appendMenu('Vistaui', label='Vista en la UI')
    B.par.Vistaui.menuNames = ['filas', 'linea']
    B.par.Vistaui.menuLabels = ['Filas x columnas (procesador)', 'En linea (como cuelga)']
    pg.sort(*[n for n in ('Ledarmada', 'Abrirled', 'Cerrarled', 'Prueba', 'Pixelmap', 'Lienzow', 'Lienzoh',
                          'Posx', 'Posy', 'Monitor', 'Vistaui') if hasattr(B.par, n)])

    pm = nuevo(B, moviefileinTOP, 'prueba_pixelmap', 600, 450)
    pm.par.file.expr = 'parent().par.Pixelmap'
    sw = nuevo(B, switchTOP, 'fuente_led', 800, 300)
    sw.inputConnectors[0].connect(B.op('master_banner'))
    sw.inputConnectors[1].connect(pm)
    sw.par.index.expr = '1 if parent().par.Prueba else 0'
    dat = nuevo(B, textDAT, 'lienzo_led_pixel', 1200, 100)
    dat.text = SHADER
    g = nuevo(B, glslTOP, 'lienzo_led_glsl', 1400, 300)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'custom'
    g.par.resolutionw.expr = 'parent().par.Lienzow'
    g.par.resolutionh.expr = 'parent().par.Lienzoh'
    g.par.inputfiltertype = 'nearest'
    g.seq.vec.numBlocks = 1
    g.par.vec0name = 'uPos'
    g.par.vec0valuex.expr = 'parent().par.Posx'
    g.par.vec0valuey.expr = 'parent().par.Posy'
    n = nuevo(B, nullTOP, 'lienzo_led', 1600, 300)
    n.inputConnectors[0].connect(g)
    o = nuevo(B, outTOP, 'out_led', 1800, 300)   # para ver el lienzo (y la prueba) en el nodo
    o.inputConnectors[0].connect(n)

    # vista EN LINEA para la UI: lo mismo que va al LED, desenrollado
    ld = nuevo(B, textDAT, 'linea_led_pixel', 1200, 700)
    ld.text = LINEA
    lg = nuevo(B, glslTOP, 'linea_led_glsl', 1400, 600)
    lg.par.pixeldat = ld.name
    lg.par.outputresolution = 'custom'
    lg.par.resolutionw.expr = 'parent().par.Columnas * parent().par.Filas * parent().par.Tablero'
    lg.par.resolutionh.expr = 'parent().par.Tablero'
    lg.par.inputfiltertype = 'nearest'
    lg.seq.vec.numBlocks = 1
    lg.par.vec0name = 'uGrid'
    lg.par.vec0valuex.expr, lg.par.vec0valuey.expr, lg.par.vec0valuez.expr = (
        'parent().par.Columnas', 'parent().par.Filas', 'parent().par.Tablero')
    ln = nuevo(B, nullTOP, 'linea_led', 1600, 600)
    ln.inputConnectors[0].connect(lg)

    cad = nuevo(B, textDAT, 'led_cadena', 1000, 100)
    cad.text = CADENA
    cadena = cad.module.encadenar()

    mod = nuevo(B, textDAT, 'led_ventana', 1400, -100)
    mod.text = VENTANA
    ex = nuevo(B, parameterexecuteDAT, 'led_pulsos', 1600, -100)
    ex.par.op = B.path
    ex.par.pars = 'Abrirled Cerrarled'
    ex.par.valuechange = False
    ex.par.onpulse = True
    ex.text = ("def onPulse(par):\n"
               "    B = par.owner\n"
               "    if par.name == 'Abrirled':\n"
               "        B.par.Ledarmada = True\n"
               "        mod('led_ventana').colocar(True)\n"
               "    else:\n"
               "        B.par.Ledarmada = False\n"
               "        w = op('/salida_led')\n"
               "        if w is not None:\n"
               "            w.par.winclose.pulse()\n"
               "    return\n")
    md = nuevo(B, monitorsDAT, 'led_monitores', 1400, -250)
    dx = nuevo(B, datexecuteDAT, 'led_monitores_exec', 1600, -250)
    dx.par.dat = md.name
    dx.par.tablechange = True
    dx.text = ("def onTableChange(dat):\n"
               "    m = mod('led_ventana')\n"
               "    w = op('/salida_led')\n"
               "    if parent().par.Ledarmada.eval():\n"
               "        m.vigilar()\n"
               "    elif w is not None and w.isOpen:\n"
               "        m.colocar(True)\n"
               "    return\n")
    vg = nuevo(B, executeDAT, 'led_vigia', 1800, -100)
    vg.par.framestart = True
    vg.par.start = True
    vg.text = ("def onStart():\n"
               "    run(\"op('/project1/led/led_ventana').module.vigilar()\", delayFrames=60)\n"
               "    return\n\n"
               "def onFrameStart(frame):\n"
               "    if frame % 60 == 0:\n"
               "        mod('led_ventana').vigilar()\n"
               "    return\n")
    if op('/project2/show') is not None and hasattr(op('/project2/show').par, 'Modoshow'):
        cx = nuevo(B, parameterexecuteDAT, 'led_candado', 1800, 50)
        cx.par.op = '/project2/show'
        cx.par.pars = 'Modoshow'
        cx.par.valuechange = True
        cx.text = ("def onValueChange(par, prev):\n"
                   "    if par.eval() and parent().par.Prueba.eval():\n"
                   "        parent().par.Prueba = False\n"
                   "        mod('led_ventana').log('MODO SHOW: patron de prueba apagado')\n"
                   "    return\n")

    # ventana, junto a /perform (que no se toca)
    w = op('/salida_led') or op('/').create(windowCOMP, 'salida_led')
    per = op('/perform')
    if per is not None:
        w.nodeX, w.nodeY = per.nodeX, per.nodeY - 150
    w.comment = 'Salida a la pantalla LED (procesador). La UI es /perform. modulos/led_salida'
    pon(w, 'winop', n.path)
    if hasattr(w.par, 'monitor'):
        w.par.monitor.expr = "op('%s').par.Monitor" % B.path
    if hasattr(w.par, 'dpiscaling'):
        pon(w, 'dpiscaling', 'native')
    pon(w, 'interact', False)
    B.par.opviewer = './lienzo_led'      # el nodo muestra lo que sale al LED
    mod.module.colocar(False)            # deja la ventana lista para lo que hay conectado ahora
    print('[ok] led_salida: /salida_led -> %s | lienzo %dx%d en (%d,%d) | monitor %d de %d | cadena %s' % (
        n.path, B.par.Lienzow.eval(), B.par.Lienzoh.eval(), B.par.Posx.eval(), B.par.Posy.eval(),
        B.par.Monitor.eval(), len(monitors), cadena or '(sin efectos)'))
    for x in (pm, g, lg):
        e = x.errors() or x.warnings()
        if e and not (x is pm and not B.par.Pixelmap.eval()):
            print('[aviso]', x.name, e)
    # legibilidad: secciones con titulo (modulos/secciones.py)
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    secciones(B, 'LED', [('Hledsalida', 'Salida al LED', ['Ledarmada', 'Abrirled', 'Cerrarled']),
                         ('Hledprueba', 'Prueba de pantalla', ['Prueba', 'Pixelmap']),
                         ('Hledlienzo', 'Procesador: lienzo y posicion', ['Lienzow', 'Lienzoh', 'Posx', 'Posy', 'Monitor']),
                         ('Hledui', 'Vista en la UI', ['Vistaui'])])
    orden_paginas(B, ['LED', 'Chaser', 'Barrido', 'Banner'])
    B.par.Posx.label, B.par.Posy.label = 'X (px desde la izquierda)', 'Y (px desde arriba)'
