# led_slices/ui.py — la salida de slices desde TD en la UI de perform. Idempotente.
# La corre modulos.py (ui) al final de setup_ui.py, despues de led_salida/ui.py si esta (toma el preview y el chip).
#   - Pestana SLICES en la columna SHOW: el preview pasa a /project1/slices/out_slices (lo que saldria por TD)
#     y abajo las paginas de /project1/slices (Salida · Chaser · Barrido · Slices).
#   - Chip de la barra (btn_led_estado) = SALIDA DESDE TD: solo hay un monitor externo y solo una salida de TD
#     se puede armar (LED o slices). Ensena la que este armada o abierta; si ninguna, "TD · APAGADA".
#     Toca = pestana SLICES (o SALIDA LED si la que esta activa es la LED).
U = op('/project2/ui_perform')
C = op('/project1/slices')
SHOW_RGB = (0.25, 0.78, 0.85)

LIB = '''# slices_ui_lib — pestana SLICES y chip SALIDA TD (lo escribe modulos/led_slices/ui.py; no editar aqui)
def slices_on():
    p = parent().op('par_show_slices')
    return p is not None and bool(p.par.display.eval())


def top():
    if slices_on():
        return op('/project1/slices/out_slices')
    l = parent().op('led_ui_lib')
    return l.module.top() if l is not None else op('/project1/spout_cuadrado')


def rect(i):
    l = parent().op('led_ui_lib')
    if not slices_on() and l is not None:
        return l.module.rect(i)
    x, y, w, h = parent().op('prev_show').fetch('box')
    t = top()
    a = (t.width / max(1.0, float(t.height))) if t is not None else 16.0 / 9.0
    ww, hh = (h * a, h) if w / float(h) > a else (w, w / a)
    return int([x + (w - ww) / 2.0, y + (h - hh) / 2.0, ww, hh][i])


def _estado():
    s = op('/project1/slices/slices_ventana')
    l = op('/project1/led/led_ventana')
    es = s.module.estado() if s is not None else ('SLICES · ?', 0)
    el = l.module.estado() if l is not None else ('LED · APAGADA', 0)
    if es[1] > 0:
        return es, 'slices'
    if el[1] > 0:
        return el, 'led'
    return ('TD · APAGADA', 0), 'slices'


def chip_txt():
    return _estado()[0][0].replace('SLICES · ', 'TD · ').replace('LED · ', 'TD LED · ')     # corto: cabe en la pastilla


TINTA = ((0.60, 0.61, 0.64), (0.19, 0.82, 0.35), (1.0, 0.62, 0.04), (1.0, 0.27, 0.23))


def chip_tinta(k):
    return TINTA[_estado()[0][1]][k]


def chip_click():
    parent().op('ui_lib').module.tab('show', _estado()[1])
'''


def copia(src, nombre):
    o = U.op(nombre)
    if o is not None:
        o.destroy()
    o = U.copy(src, name=nombre)
    for t in list(o.tags):
        o.tags.remove(t)
    return o


if U is None or C is None or U.op('btn_tab_show_hub') is None or U.op('prev_show') is None:
    print('[--] led_slices/ui: falta la UI o /project1/slices')
else:
    hub = U.op('btn_tab_show_hub')
    b = copia(hub, 'btn_tab_show_slices')
    b.par.text = 'SLICES'
    b.store('tipo', 'TAB')
    b.store('dato', 'show:slices')
    b.store('rgb', SHOW_RGB)
    orden = ['hub', 'audio', 'piloto', 'led', 'slices']
    tabs = [U.op('btn_tab_show_' + k) for k in orden if U.op('btn_tab_show_' + k) is not None]
    tabs += [c for c in U.children if c.isPanel and c.name.startswith('btn_tab_show_') and c not in tabs]
    x3 = hub.par.x.eval()
    cw = 626 if U.op('tit_show') is None else int(U.op('tit_show').par.w.eval())
    w = cw // len(tabs)
    for i, t in enumerate(tabs):
        t.par.x, t.par.w = x3 + i * w, w - 2

    lib = U.op('slices_ui_lib') or U.create(textDAT, 'slices_ui_lib')
    lib.text = LIB
    lib.nodeX, lib.nodeY = -400, -300
    pv = U.op('prev_show')
    if pv.fetch('box', None, search=False) is None:
        pv.store('box', (pv.par.x.eval(), pv.par.y.eval(), pv.par.w.eval(), pv.par.h.eval()))
    pv.par.top.expr = "op('slices_ui_lib').module.top()"
    for i, n in enumerate(('x', 'y', 'w', 'h')):
        getattr(pv.par, n).expr = "op('slices_ui_lib').module.rect(%d)" % i

    # parametros de /project1/slices debajo de BLACKOUT (Salida y efectos primero: lo que se toca en show)
    bo = U.op('btn_blackout')
    ytop = bo.par.y.eval() - 6
    pp = copia(U.op('par_show_led') or U.op('par_show_piloto') or U.op('par_show_hub'), 'par_show_slices')
    pp.par.x, pp.par.y, pp.par.w, pp.par.h = x3, 10, cw, ytop - 10
    pp.par.op.expr = "op('/project1/slices')"
    pp.par.pagescope = '*'
    pp.par.pagenames = True
    if hasattr(pp.par, 'parscope'):
        pp.par.parscope.expr = ''
        pp.par.parscope = '*'
    pp.tags.add('tab_show_slices')
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    orden_paginas(C, ['Salida', 'Efectos', 'Capa', 'Chaser', 'Barrido', 'EQ', 'Onda', 'Cascada', 'Giro', 'Respira', 'Slices', 'LED', 'Banner'])

    # chip SALIDA TD. Con led_salida: toma su chip (btn_led_estado) y ensena la que este activa de las dos.
    # Sin led_salida: chip propio (btn_slices_estado) en el lugar libre de la barra (barra_x) y la recorre.
    ch = U.op('btn_led_estado')
    if ch is None:
        plantilla = U.op('btn_piloto') or U.op('btn_thumbs')
        viejo = U.op('btn_slices_estado')
        if viejo is not None:                     # ya tenia lugar: se queda ahi (re-correr no lo recorre encima de GUARDAR)
            x = viejo.par.x.eval()
        else:
            bx = U.fetch('barra_x', None, search=False)
            if bx is None:
                bx = min(c.par.x.eval() for c in (U.op('btn_piloto'), U.op('btn_salida'), plantilla) if c is not None)
            x = bx - 168
            U.store('barra_x', x)
        ch = copia(plantilla, 'btn_slices_estado')
        ch.par.x, ch.par.w = x, 160
        for k, c in enumerate('rgb'):
            p = getattr(ch.par, 'bgcolor' + c)
            p.expr = ''
            p.mode = ParMode.CONSTANT
            p.val = (0.17, 0.17, 0.18)[k]
    ch.par.text.expr = "'●  ' + op('slices_ui_lib').module.chip_txt() if absTime.frame >= 0 else ''"
    for k, c in enumerate('rgb'):
        getattr(ch.par, 'fontcolor' + c).expr = "op('slices_ui_lib').module.chip_tinta(%d) if absTime.frame >= 0 else 0.6" % k
    ch.store('tipo', 'CHIPSLICES')
    ch.store('dato', '')
    # clics del modulo (convencion del boilerplate: Text DAT uimod_<nombre> con elegir(tipo, dato) -> True)
    um = U.op('uimod_led_slices') or U.create(textDAT, 'uimod_led_slices')
    um.nodeX, um.nodeY = -400, -450
    um.text = '\n'.join(['# clics de led_slices en la UI (lo escribe modulos/led_slices/ui.py)',
                         'def elegir(tipo, dato):', "    if tipo == 'CHIPSLICES':",
                         "        op('slices_ui_lib').module.chip_click()", '        return True', '    return False', ''])
    ul = U.op('ui_lib')
    ul.module.tab('show', 'hub')
    print('[ok] pestanas SHOW:', [t.par.text.eval() for t in tabs], '| chip:', lib.module.chip_txt())
