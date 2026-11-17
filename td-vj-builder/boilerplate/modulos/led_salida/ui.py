# led_salida/ui.py — pestana SALIDA LED en la columna SHOW de la UI de perform + chip de estado. Idempotente.
# La corre modulos.py (ui) al final de setup_ui.py, y modulos.py al instalar led_salida si ya hay UI.
#   - Pestana SALIDA LED: el preview de SHOW pasa a la salida LED, con dos vistas:
#       FILAS x COLUMNAS = lienzo_led (lo que recibe el procesador)
#       EN LINEA         = linea_led (todos los tableros como cuelgan)
#     (led.Vistaui guarda la vista; prueba y efectos LED se ven aqui tambien)
#     Abajo: todas las paginas de /project1/led (LED · efectos · Banner).
#   - El preview se ajusta a la proporcion de lo que muestra (16:9 show, filas x columnas, tira en linea).
#   - Chip LED en la barra de arriba: gris apagada · verde al aire · ambar prueba · rojo sin pantalla.
# Requiere led_mapeo y led_salida, y la UI de setup_ui.py (/project2/ui_perform).

U = op('/project2/ui_perform')
B = op('/project1/led')
SHOW_RGB = (0.08, 0.72, 0.72)

LIB = '''# led_ui_lib — pestana LED de la UI (lo escribe modulos/led_salida/ui.py; no editar aqui)
BOX = %r     # x, y, w, h del preview de SHOW


def led_on():
    p = parent().op('par_show_led')
    return p is not None and bool(p.par.display.eval())


def top():
    B = op('/project1/led')
    if B is None or not led_on():
        return op('/project1/ndiout1')
    return B.op('lienzo_led') if B.par.Vistaui.eval() == 'filas' else B.op('linea_led')


def rect(i):
    t = top()
    a = (t.width / max(1.0, float(t.height))) if t is not None else 16.0 / 9.0
    x, y, w, h = BOX
    if w / float(h) > a:
        ww, hh = h * a, h
    else:
        ww, hh = w, w / a
    return int([x + (w - ww) / 2.0, y + (h - hh) / 2.0, ww, hh][i])


def vista(dato):
    op('/project1/led').par.Vistaui = dato


CHIP = ((0.25, 0.25, 0.27), (0.10, 0.50, 0.25), (0.85, 0.55, 0.05), (0.85, 0.10, 0.10))


def _estado():
    m = op('/project1/led/led_ventana')
    return m.module.estado() if m is not None else ('LED · ?', 0)


def chip_txt():
    return _estado()[0]


def chip_rgb(k):
    return CHIP[_estado()[1]][k]
'''


def copia(src, nombre):
    o = U.op(nombre)
    if o is not None:
        o.destroy()
    o = U.copy(src, name=nombre)
    for t in list(o.tags):
        o.tags.remove(t)
    return o


if U is None or B is None or B.op('linea_led') is None or U.op('btn_tab_show_hub') is None:
    print('[--] led_salida/ui: no hay UI (/project2/ui_perform) o falta led_salida; nada que hacer')
else:
    # 2 · boton de pestana LED (copia del de CONTROLES) y reparto parejo de las pestanas
    hub = U.op('btn_tab_show_hub')
    b = copia(hub, 'btn_tab_show_led')
    b.par.text = 'SALIDA LED'
    b.store('tipo', 'TAB')
    b.store('dato', 'show:led')
    b.store('rgb', SHOW_RGB)
    orden = ['hub', 'audio', 'piloto', 'led']
    tabs = [U.op('btn_tab_show_' + k) for k in orden if U.op('btn_tab_show_' + k) is not None]
    tabs += [c for c in U.children if c.isPanel and c.name.startswith('btn_tab_show_') and c not in tabs]   # FX nuevos al final
    pv = U.op('prev_show')
    x3 = hub.par.x.eval()
    prev_box = pv.fetch('box', None, search=False)
    if prev_box is None:
        prev_box = (pv.par.x.eval(), pv.par.y.eval(), pv.par.w.eval(), pv.par.h.eval())
        pv.store('box', prev_box)
    cw = 626 if U.op('tit_show') is None else int(U.op('tit_show').par.w.eval())
    w = cw // len(tabs)
    for i, t in enumerate(tabs):
        t.par.x, t.par.w = x3 + i * w, w - 2

    # 3 · libreria y preview que sigue a la pestana / vista
    lib = U.op('led_ui_lib') or U.create(textDAT, 'led_ui_lib')
    lib.text = LIB % (tuple(int(v) for v in prev_box),)
    lib.nodeX, lib.nodeY = -400, -150
    pv.par.top.expr = "op('led_ui_lib').module.top()"
    for i, n in enumerate(('x', 'y', 'w', 'h')):
        getattr(pv.par, n).expr = "op('led_ui_lib').module.rect(%d)" % i

    # 4 · botones de vista + parametros del banner (debajo de BLACKOUT, como las otras pestanas)
    bo = U.op('btn_blackout')
    ytop = bo.par.y.eval() - 6
    bw = cw // 2
    hecho = []
    for i, (k, label) in enumerate((('filas', 'FILAS x COLUMNAS'), ('linea', 'EN LINEA'))):
        v = copia(hub, 'btn_ledvista_' + k)
        v.par.text = label
        v.par.x, v.par.y, v.par.w, v.par.h = x3 + i * bw, ytop - 34, bw - 2, 34
        for j, ch in enumerate('rgb'):
            getattr(v.par, 'bgcolor' + ch).expr = ("%g * (1.0 if op('/project1/led').par.Vistaui == '%s' else 0.3)"
                                                   % (SHOW_RGB[j], k))
        v.store('tipo', 'LEDVISTA')
        v.store('dato', k)
        hecho.append(v)
    pp = copia(U.op('par_show_piloto') or U.op('par_show_hub'), 'par_show_led')
    pp.par.x, pp.par.y, pp.par.w, pp.par.h = x3, 10, cw, ytop - 34 - 6 - 10
    pp.par.op.expr = "op('/project1/led')"
    pp.par.pagescope = '*'
    pp.par.pagenames = True
    if hasattr(pp.par, 'parscope'):
        pp.par.parscope.expr = ''
        pp.par.parscope = '*'
    hecho.append(pp)
    for o in hecho:
        o.tags.add('tab_show_led')

    # 5 · ui_lib: el click de LEDVISTA (setup_ui.py ya lo trae; esto es para una UI armada antes)
    ul = U.op('ui_lib')
    if "'LEDVISTA'" not in ul.text:
        ul.text = ul.text.replace("    elif tipo == 'TAB':",
                                  "    elif tipo == 'LEDVISTA':\n        op('led_ui_lib').module.vista(dato)\n    elif tipo == 'TAB':", 1)

    # 6 · chip de estado LED en la barra de arriba (gris apagada · verde al aire · ambar prueba · rojo sin
    #     pantalla). Toca = abre la pestana SALIDA LED. Se evalua cada cuadro: la ventana no es un parametro.
    plantilla = U.op('btn_piloto') or U.op('btn_thumbs')
    tit = U.op('titulo')
    cx = plantilla.par.x.eval() - 170
    ch = copia(plantilla, 'btn_led_estado')
    ch.par.x, ch.par.w = cx, 160
    ch.par.text.expr = "op('led_ui_lib').module.chip_txt() if absTime.frame >= 0 else ''"
    for k, c in enumerate('rgb'):
        getattr(ch.par, 'bgcolor' + c).expr = "op('led_ui_lib').module.chip_rgb(%d) if absTime.frame >= 0 else 0" % k
    ch.store('tipo', 'TAB')
    ch.store('dato', 'show:led')
    if tit is not None:
        tit.par.w = min(tit.par.w.eval(), cx - 10 - tit.par.x.eval())

    # deja la UI en CONTROLES, como al abrir
    ul.module.tab('show', 'hub')
    print('[ok] pestanas SHOW:', [t.par.text.eval() for t in tabs])
    print('[ok] preview caja', prev_box, '| vista', B.par.Vistaui.eval())
