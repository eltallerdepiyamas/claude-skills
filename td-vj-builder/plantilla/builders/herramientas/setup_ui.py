import json
# ─────────────────────────────────────────────────────────────
# setup_ui.py — UI de PERFORM (/project2/ui_perform, 1920x1080). Idempotente.
# Una columna por lo que el proyecto TENGA (si no hay FX, no hay columna FX):
#   ESCENA  -> el layout activo de escena_modular (su pagina Layout: 5 sliders + extras)
#   VISUAL  -> el visual activo (lo que sale por switch2; pagina Visual)
#   FX      -> el FX activo (lo que sale por switch23; pagina Filter)
#   SHOW    -> hub /project2/show: Color · Audio · Resolucion, con la salida final
# Cada columna: titulo con el nombre de lo activo · preview · parametros (se editan ahi mismo).
# Todo sigue solo a lo activo (expresiones): no hay que reconstruir al cambiar de escena / visual / FX;
# SI hay que correrlo otra vez cuando el proyecto gana o pierde visuales / FX (aparece la columna).
# La ventana de perform (/perform) apunta aqui. La UI anterior (container1, opviewer1-4,
# parameter1-4, button2 "Mode Switch" y su cadena) se va a /project2/_respaldo/ui_vieja.
# ─────────────────────────────────────────────────────────────
import os, glob, re
R = op('/project2')
ESC = '/project2/base17/escena_modular'
W, H = 1920, 1080
TOP_H, TITLE_H, PREV_H, GAP = 56, 44, 300, 10
TH_COLS = 4      # 4x2 por pagina: dos filas iguales
TH_PAG = 8       # con mas de 8, ESCENA se divide en paginas 1-8 / 9-16 (filas del Beatstep)
TH_TXT = 16
# FX GLOBALES de /project1: agregar aqui uno nuevo = pestana nueva en SHOW (hasta 5)
FX_GLOBALES = [('cb', 'CIRCUIT B.', '/project1/curcuitBending'), ('fb', 'FEEDBACK', '/project1/feedback_HSV1')]
TAB_H = 30
BG = (0.06, 0.06, 0.07)
COL = {'ESCENA': (0.18, 0.49, 0.88), 'VISUAL': (0.64, 0.23, 0.77), 'FX': (0.91, 0.45, 0.11), 'SHOW': (0.08, 0.72, 0.72), 'CAMARAS': (0.13, 0.70, 0.35)}
UI_VIEJA = ['container1', 'opviewer1', 'opviewer2', 'opviewer3', 'opviewer4',
            'parameter1', 'parameter2', 'parameter3', 'parameter4',
            'button2', 'null2']
# OJO: logic67 / logic68 / chopexec36 / chopexec37 NO van aqui: en shows con mas pads son cadenas de pads
# (p. ej. logic67 = pad de la fila 49 de table1 en Casa Bacardi). Mandarlas al respaldo rompe esos pads.


def tiene_pagina(rango, pagina):
    for n in rango:
        b = R.op('base%d' % n)
        if b is not None and any(p.name == pagina for p in b.customPages):
            return True
    return False


def secciones():
    s = []
    if op(ESC) is not None:
        e = "op('%s').op(op('%s').par.Modoescena.eval())" % (ESC, ESC)
        s.append(('ESCENA', e, 'Layout', "op('%s/master_video')" % ESC))
    if tiene_pagina(range(1, 17), 'Visual'):
        s.append(('VISUAL', "op('/project2/vis_knobs_lib').module.active_base()", 'Visual', "op('/project2/master_visuales')"))
    if tiene_pagina(list(range(18, 33)) + list(range(38, 46)), 'Filter'):
        s.append(('FX', "op('/project2/fx_knobs_lib').module.active_base()", 'Filter', "op('/project2/master_fx')"))
    if R.op('show') is not None:
        s.append(('SHOW', "op('/project2/show')", 'Correccion* Audio Resolucion', "op('/project1/color_final') or op('/project2/master_fx')"))
    return s


def setp(o, names, value, expr=False):
    """Pone el primer parametro que exista de `names` (los nombres cambian entre versiones de TD)."""
    for n in names:
        p = getattr(o.par, n, None)
        if p is not None:
            if expr:
                p.expr = value
            else:
                p.val = value
            return n
    return None


def panel(parent, tipo, name, x, y, w, h):
    o = parent.op(name) or parent.create(tipo, name)
    o.par.x, o.par.y, o.par.w, o.par.h = x, y, w, h
    return o


def color(o, rgb, alpha=1.0):
    for k, c in enumerate('rgb'):
        setp(o, ['bgcolor' + c], rgb[k])
    setp(o, ['bgalpha'], alpha)


UI_LIB = '''# ui_lib — funciones de la UI de perform (lo escribe setup_ui.py; no editar aqui)
def cinco(o, pagina):
    """Nombres de los 5 sliders de rol (los primeros 5 numeros de la pagina, sin colores)."""
    if o is None:
        return ''
    pg = next((g for g in o.customPages if g.name == pagina), None)
    if pg is None:
        return ''
    names = [p.name for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA', 'XY', 'XYZ', 'UV', 'UVW', 'WH')]
    return ' '.join(names[:5]) or 'NADA'


def todos(o, pagina):
    """Todos los parametros de la pagina + los de Audio, menos la paleta del album (Color1-5)."""
    if o is None:
        return ''
    out = []
    for g in o.customPages:
        if g.name not in (pagina, 'Audio'):
            continue
        for p in g.pars:
            n = p.tupletName
            if n not in out and n not in ('Color1', 'Color2', 'Color3', 'Color4', 'Color5'):
                out.append(n)
    return ' '.join(out) or 'NADA'


FUNDIDO = 0.8        # segundos del fundido del boton BLACKOUT (a negro y de regreso)


def fundir_master(destino, seg=None):
    """Lleva show.Master a destino con una rampa suave, cuadro por cuadro."""
    p = op('/project2/show').par.Master
    a = float(p.eval())
    n = max(2, int((FUNDIDO if seg is None else seg) * project.cookRate))
    serie = parent().fetch('fundido_n', 0, search=False) + 1      # un fundido nuevo cancela al anterior
    parent().store('fundido_n', serie)
    for i in range(1, n + 1):
        t = i / float(n)
        t = t * t * (3.0 - 2.0 * t)
        run("if op('/project2/ui_perform').fetch('fundido_n', 0, search=False) == args[1]: op('/project2/show').par.Master = args[0]",
            a + (destino - a) * t, serie, delayFrames=i)


def sin_senal(i):
    """Camara i en vivo (dispositivo activo) pero sin cuadros entrando."""
    v = op('/project2/base17/escena_modular/cam' + str(i) + '_vivo')
    c = op('info_cam' + str(i))
    if v is None or c is None or not v.par.active.eval():
        return False
    return c['capture_fps'] < 1


def ndi_estado():
    """(texto, ok) de la salida NDI."""
    n = op('/project1/ndiout1')
    c = op('info_ndi')
    if n is None or c is None:
        return ('', True)
    if not n.par.active.eval():
        return ('NDI APAGADO', False)
    k = int(c['num_connected'])
    return ('NDI SIN RECEPTOR', False) if k < 1 else ('NDI OK  ·  ' + str(k), True)


def candado():
    """MODO SHOW puesto (show.Modoshow, builders/herramientas/setup_modo_show.py)."""
    p = getattr(op('/project2/show').par, 'Modoshow', None)
    return bool(p.eval()) if p is not None else False


def elegir(tipo, dato):
    if tipo in ('MODOSHOW', 'CANDADOAJ'):
        p = getattr(op('/project2/show').par, 'Modoshow' if tipo == 'MODOSHOW' else 'Candadoajustes', None)
        if p is not None:
            p.val = not p.eval()
            lib = op('/project2/show/modoshow_lib')
            if lib is not None:
                lib.module.aplicar()        # de inmediato (el parameterexecute lo repite, es idempotente)
        return
    if tipo == 'BLACKOUT':
        # fundido a negro; otro toque regresa al nivel que tenia (el candado nunca lo bloquea)
        p = op('/project2/show').par.Master
        if parent().fetch('en_negro', False, search=False) and p.eval() < 0.5:
            parent().store('en_negro', False)
            fundir_master(parent().fetch('master_antes', 1.0, search=False) or 1.0)
        else:
            if p.eval() > 0.02:
                parent().store('master_antes', p.eval())
            parent().store('en_negro', True)
            fundir_master(0.0)
        return
    if candado() and tipo in ('THUMBS', 'FUENTE', 'CAMFUENTE'):
        return      # con candado: ni recapturar thumbs (congela) ni cambiar fuentes
    if tipo == 'ESCENA':
        op('%s').par.Modoescena = dato
    elif tipo == 'VISUAL':
        op('/project2/switch2').par.index = int(dato)
    elif tipo == 'FX':
        op('/project2/switch23').par.index = int(dato)
    elif tipo == 'FUENTE':
        e = op('%s')
        e.par.Fuente = dato
        for i in range(1, 7):
            getattr(e.par, 'Fuente%%d' %% i).val = 'global'
    elif tipo == 'CAMFUENTE':
        i, m = dato.split(':')
        getattr(op('%s').par, 'Fuente' + i).val = m
    elif tipo == 'CAM':
        op('%s').par.Menu2 = dato
    elif tipo == 'TAB':
        tab(*dato.split(':'))
    elif tipo == 'RESET':
        resetear(activo(dato))
    elif tipo == 'THUMBS':
        return actualizar_thumbs()
    elif tipo == 'RESETFB':
        return resetear_feedbacks()
    elif tipo == 'PAG':
        parent().store('pag_escena', int(dato))
        paginar()


def activo(tipo):
    if tipo == 'ESCENA':
        e = op('%s')
        return e.op(e.par.Modoescena.eval())
    lib = 'vis_knobs_lib' if tipo == 'VISUAL' else 'fx_knobs_lib'
    return op('/project2/' + lib).module.active_base()


def resetear(c):
    """Sliders del activo a su default + reloj y feedback a cero."""
    if c is None:
        return
    for pg in c.customPages:
        if pg.name in ('Layout', 'Visual', 'Filter'):
            for p in pg.pars:
                if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA') and p.mode == ParMode.CONSTANT:
                    p.val = p.default
    f = c.op('tdvj_fase')
    if f is not None:
        f.par.resetpulse.pulse()
    for t in c.findChildren(type=feedbackTOP):
        t.par.resetpulse.pulse()


def tab(grupo, clave):
    pre = 'tab_%%s_' %% grupo
    for c in parent().children:
        for t in c.tags:
            if t.startswith(pre):
                c.par.display = t == pre + clave
                c.par.enable = t == pre + clave     # oculto = no recibe clicks
    for c in parent().children:
        if c.isCOMP and c.name.startswith('btn_tab_%%s_' %% grupo):
            k = 1.0 if c.name == 'btn_tab_%%s_%%s' %% (grupo, clave) else 0.3
            r, g, b = {'media': (0.18, 0.49, 0.88), 'show': (0.08, 0.72, 0.72)}[grupo]
            c.par.bgcolorr, c.par.bgcolorg, c.par.bgcolorb = r * k, g * k, b * k
    ondas()
    paginar()


def actualizar_thumbs():
    # Vuelve a capturar cada thumb como se ve ahorita, sin reconstruir nada.
    n = 0
    for c in parent().children:
        if c.isCOMP and c.name.startswith('th_') and c.fetch('fuente', None, search=False):
            o = op(c.fetch('fuente'))
            if o is not None:
                o.cook(force=True)
                o.save(project.folder + '/' + c.fetch('ruta'))
                c.op('img_p/img').par.reloadpulse.pulse()
                n += 1
    return n


def resetear_feedbacks():
    # Busca todos los Feedback TOP cada vez: los que se creen despues entran solos.
    n = 0
    for r in (op('/project1'), op('/project2')):
        for o in r.findChildren(type=feedbackTOP):
            if '/_respaldo' not in o.path:
                o.par.resetpulse.pulse()
                n += 1
    return n


def paginar():
    # Paginas de thumbs de ESCENA: solo se ve la activa, y solo con la pestana ESCENA abierta.
    u = parent()
    if u.op('btn_pag_1') is None or u.op('prev_escena') is None:
        return
    p = u.fetch('pag_escena', 1, search=False)
    vis = bool(u.op('prev_escena').par.display.eval())
    for c in u.children:
        if c.isCOMP and c.name.startswith(('th_escena_', 'lab_escena_')):
            on = vis and int(c.name.rsplit('_', 1)[1]) // 8 + 1 == p
            c.par.display = on
            c.par.enable = on
    for n in (1, 2):
        k = 1.0 if n == p else 0.3
        b = u.op('btn_pag_%%d' %% n)
        b.par.bgcolorr, b.par.bgcolorg, b.par.bgcolorb = 0.18 * k, 0.49 * k, 0.88 * k


def ondas():
    # Interruptor del hub (Audio > Ver onda y analisis): oculta las vistas y da su lugar a los parametros.
    u = parent()
    pc = u.op('par_show_hub')
    if pc is None or u.op('onda') is None:
        return
    prendido = bool(op('/project2/show').par.Vermonitor.eval())
    ver = prendido and bool(pc.par.display.eval())
    for n in ('onda', 'bandas'):
        u.op(n).par.display = ver
        u.op(n).par.enable = ver
    pc.par.h = pc.fetch('h_con' if prendido else 'h_sin')


def tipo_escena(o):
    if o is None:
        return '-'
    return 'SINGLE CAM' if 'tdvj_fam_singlecam' in o.tags else 'MULTIVIEW'


def nombre(o):
    """Como se llama lo activo: la escena por su etiqueta del menu; lo demas por su nombre."""
    if o is None:
        return '-'
    esc = op('%s')
    if o.parent() == esc and hasattr(esc.par, 'Modoescena'):
        m = esc.par.Modoescena
        if o.name in m.menuNames:
            return m.menuLabels[list(m.menuNames).index(o.name)].upper()
    return o.fetch('nombre', o.name, search=False).upper()
''' % ((ESC,)*6)


def nombre_de_base(b):
    """Nombre legible del visual / FX: sale del archivo de su builder (setup_base2_destellos.py -> Destellos)."""
    for g in glob.glob(project.folder + '/builders/*/setup_%s_*.py' % b.name):
        n = os.path.basename(g)[:-3].split('_', 2)[2].replace('_', ' ').title()
        b.store('nombre', n)
        return n
    return b.name


def pad_de(tabla_fila):
    t = R.op('table1')
    if t is None or tabla_fila >= t.numRows:
        return ''
    m = re.match(r'ch(\d+)n(\d+)', t[tabla_fila, 0].val)
    return 'ch%s n%s' % m.groups() if m else ''


def canal_pad(nombre, k):
    """Entrada k del switch -> 'canal-pad' real del Beatstep (segun table1; pads 1-8 arriba, 9-16 abajo)."""
    if nombre == 'VISUAL':
        return '10-%d' % (k + 1) if k < 8 else ('11-%d' % (k - 7) if k < 16 else '')
    if k < 8:
        return '10-%d' % (k + 9)
    return '11-%d' % (k + 4) if k < 13 else ('11-%d' % (k - 4) if k < 16 else '')


def banco(nombre):
    """[(id, etiqueta, dato, TOP, expresion de activo, pad)] de lo que se puede elegir."""
    out = []
    if nombre == 'ESCENA':
        e = op(ESC)
        for i, (n, l) in enumerate(zip(e.par.Modoescena.menuNames, e.par.Modoescena.menuLabels)):
            if e.op(n) is not None:
                pad = '9-%d' % (i + 1) if i < 16 else ''      # canal-pad del Beatstep (1-8 arriba, 9-16 abajo)
                out.append((n, l, n, e.op(n).op('out1'), "op('%s').par.Modoescena == '%s'" % (ESC, n), pad))
    else:
        vis = nombre == 'VISUAL'
        sw, pag = (R.op('switch2'), 'Visual') if vis else (R.op('switch23'), 'Filter')
        if not vis:                     # entrada 0 de switch23 = escena limpia: apagar el FX
            out.append(('fx_off', 'SIN FX', 0, op(ESC).op('master_video'), "op('%s').par.index == 0" % sw.path, canal_pad('FX', 0)))
        for k in range(len(sw.inputs)):
            b = R.op('vis_knobs_lib' if vis else 'fx_knobs_lib').module.resolve(sw.inputs[k])
            if b is not None and any(p.name == pag for p in b.customPages):
                out.append((b.name, nombre_de_base(b), k, b.op('out1'), "op('%s').par.index == %d" % (sw.path, k), canal_pad(nombre, k)))
    return out


def marco(ui, name, x, y, w, h, top_expr, activo, rgb):
    """Thumb con marco del color de su grupo: tenue, y brillante cuando esta activo. Click en el marco."""
    c = panel(ui, containerCOMP, name, x, y, w, h)
    for k, ch in enumerate('rgb'):
        getattr(c.par, 'bgcolor' + ch).expr = '%g * (1.0 if %s else 0.22)' % (rgb[k], activo)
    c.par.bgalpha = 1
    d = c.create(containerCOMP, 'img_p')
    d.par.x, d.par.y, d.par.w, d.par.h = 3, 3, w - 6, h - 6
    return c, d


def thumbs(ui, nombre, x, ytop, cw):
    """Banco de imagenes capturadas (no en vivo: asi no cocinan las escenas apagadas). Click = elegir."""
    items = banco(nombre)
    if not items:
        return ytop
    os.makedirs(project.folder + '/control/thumbs', exist_ok=True)
    tw = (cw - (TH_COLS - 1) * 4) // TH_COLS
    th = tw * 9 // 16
    alto = th + TH_TXT + 4
    # solo ESCENA se pagina (1-8 / 9-16); VISUAL y FX enseñan todas sus filas, una debajo de otra
    pag = TH_PAG if nombre == 'ESCENA' else 10 ** 6
    off = 30 if len(items) > pag else 0
    if off:
        wb = (cw - 4) // 2
        for n, txt in ((1, '1 - 8'), (2, '9 - 16')):
            b = texto(ui, 'btn_pag_%d' % n, x + (n - 1) * (wb + 4), ytop - 26, wb, 26, txt, COL[nombre], 13)
            b.store('tipo', 'PAG')
            b.store('dato', n)
    for i, (fid, label, dato, top, activo, pad) in enumerate(items):
        ruta = 'control/thumbs/%s.jpg' % fid
        if top is not None:
            top.cook(force=True)
            top.save(project.folder + '/' + ruta)
        pi = i % pag
        px, py = x + (pi % TH_COLS) * (tw + 4), ytop - off - (pi // TH_COLS + 1) * alto
        c, d = marco(ui, 'th_%s_%d' % (nombre.lower(), i), px, py + TH_TXT, tw, th, None, activo, COL[nombre])
        if top is not None:
            c.store('fuente', top.path)
            c.store('ruta', ruta)
        img = d.create(moviefileinTOP, 'img')
        img.par.file = ruta
        img.par.outputresolution = 'eighth'   # thumbs ligeros
        d.par.top = img.path
        c.store('tipo', nombre)
        c.store('dato', dato)
        texto(ui, 'lab_%s_%d' % (nombre.lower(), i), px, py, tw, TH_TXT, (label.upper() + '   ' + pad).strip(), (0.1, 0.1, 0.11), 10)
    filas = (min(len(items), pag) + TH_COLS - 1) // TH_COLS
    return ytop - off - filas * alto - 6


def texto(ui, name, x, y, w, h, txt, rgb, size=16, expr=False):
    t = panel(ui, textCOMP, name, x, y, w, h)
    setp(t, ['text'], txt, expr=expr)
    # REGLA DE LA UI (de LJ): un texto siempre se lee. Si no cabe en su ancho, baja la letra y se parte en
    # renglones, nunca se corta. El Text COMP solo parte renglones con Type = 'multiline'; scaletofit es la
    # ultima red: si aun asi no cabe en el panel, encoge la letra.
    setp(t, ['type'], 'multiline')
    setp(t, ['wordwrap'], True)
    setp(t, ['scaletofit'], 'onlyshrink')
    chico = max(9, int(round(size * 0.72)))
    for n in ('fontsizex', 'fontsize'):
        q = getattr(t.par, n, None)
        if q is not None:
            q.expr = ("%d if max([len(r) for r in str(me.par.text.eval()).split(chr(10))] or [0]) * %g <= me.par.w - 10 else %d"
                      % (size, size * 0.62, chico))
            break
    setp(t, ['fontbold', 'bold'], True)
    color(t, rgb)
    return t


def imagen(ui, name, x, y, w, h, top_expr):
    """Preview sin marco de viewer: container con el TOP."""
    c = panel(ui, containerCOMP, name, x, y, w, h)
    c.par.top.expr = top_expr
    color(c, (0.0, 0.0, 0.0))
    return c


def tagear(tag, ops):
    for o in ops:
        o.tags.add(tag)


def _preview_expr(cw):
    """Devuelve expresiones (w_expr, h_expr, x_expr_fmt) para que el preview de la UI respete
    DINAMICAMENTE el aspect del canvas del show (W/H del hub). Al cambiar W/H desde la pestaña
    Resolucion, el preview se adapta solo sin necesidad de reconstruir la UI."""
    max_h = PREV_H - 8
    max_w = cw - 16
    asp = "(op('/project2/show').par.W / max(op('/project2/show').par.H, 1))"
    # ancho = min(max_w, max_h * aspect); alto = min(max_h, max_w / aspect).
    w_expr = "int(min(%d, %d * %s))" % (max_w, max_h, asp)
    h_expr = "int(min(%d, %d / max(%s, 0.1)))" % (max_h, max_w, asp)
    return w_expr, h_expr


def _bind_preview_dims(cont, base_x, ytop, cw, w_expr, h_expr):
    """Ata w, h, x (centrado horizontal) e y (fondeado abajo) del container a expresiones."""
    cont.par.w.expr = w_expr
    cont.par.h.expr = h_expr
    cont.par.x.expr = "%d + (%d - me.par.w) / 2" % (base_x, cw)
    cont.par.y.expr = "%d - me.par.h" % ytop


def contenido(ui, nombre, x, ytop, cw, opexpr, pagina, prev, tag, tipo_expr):
    """preview -> thumbs -> barra 'que es' + RESET -> parametros (todo lo de un tab)."""
    antes = set(ui.children)
    w_expr, h_expr = _preview_expr(cw)
    # placeholder; luego las expr las ajustan
    cont = imagen(ui, 'prev_' + nombre.lower(), x, ytop - (PREV_H - 8), cw, PREV_H - 8, prev)
    _bind_preview_dims(cont, x, ytop, cw, w_expr, h_expr)
    y = thumbs(ui, nombre, x, ytop - PREV_H - 6, cw)
    rgb = COL[nombre]
    texto(ui, 'tipo_' + nombre.lower(), x, y - 34, cw - 130, 34, tipo_expr, tuple(c * 0.4 for c in rgb), 15, expr=True)
    b = texto(ui, 'btn_reset_' + nombre.lower(), x + cw - 124, y - 34, 124, 34, 'RESET', (0.55, 0.12, 0.12), 15)
    b.store('tipo', 'RESET')
    b.store('dato', nombre)
    pc = panel(ui, parameterCOMP, 'par_' + nombre.lower(), x, GAP, cw, y - 34 - GAP - 4)
    setp(pc, ['op'], opexpr, expr=True)
    setp(pc, ['pagescope'], pagina + ' Audio')
    setp(pc, ['pagenames'], True)      # pestanas nativas: sus parametros / Audio
    setp(pc, ['parscope'], "op('ui_lib').module.todos(%s, '%s')" % (opexpr, pagina), expr=True)
    setp(pc, ['builtin'], False)
    setp(pc, ['custom'], True)
    setp(pc, ['header'], False)
    if tag:
        tagear(tag, [o for o in ui.children if o not in antes and o.isCOMP])


def pestanas(ui, grupo, x, y, cw, tabs, rgb):
    w = cw // len(tabs)
    for i, (k, label) in enumerate(tabs):
        b = texto(ui, 'btn_tab_%s_%s' % (grupo, k), x + i * w, y, w - 2, TAB_H, label, rgb, 14)
        b.store('tipo', 'TAB')
        b.store('rgb', tuple(rgb))
        b.store('dato', '%s:%s' % (grupo, k))


def camaras(ui, x, ytop, cw, tag):
    """Monitores: click = pone esa camara en Camara Unica. Debajo, su fuente a la mano. Nombres editables abajo."""
    E = op(ESC)
    pg = next(p for p in E.customPages if p.name == 'Camaras')
    for i in range(1, 7):
        if not hasattr(E.par, 'Nombre%d' % i):
            pg.appendStr('Nombre%d' % i, label='Nombre Cam %d' % i)[0].val = 'Cam %d' % i
    lista = []
    v = COL['CAMARAS']
    # lo que sale al aire, siempre a la vista
    ph = 170
    pw = ph * 16 // 9
    pv = imagen(ui, 'prev_cams', x + (cw - pw) // 2, ytop - ph, pw, ph, "op('%s/master_video')" % ESC)
    asp = "(op('/project2/show').par.W / max(op('/project2/show').par.H, 1))"      # mismo aspecto que la salida
    _bind_preview_dims(pv, x, ytop, cw, "int(min(%d, %d * %s))" % (cw - 16, ph, asp),
                       "int(min(%d, %d / max(%s, 0.1)))" % (ph, cw - 16, asp))
    lista.append(pv)
    ytop -= ph + 6
    # toda la fuente a la vez
    w = cw // 3
    for k, (m, l) in enumerate((('solido', 'TODAS SOLIDOS'), ('stock', 'TODAS VIDEOS'), ('vivo', 'TODAS EN VIVO'))):
        b = texto(ui, 'btn_fuente_%s' % m, x + k * w, ytop - 28, w - 2, 28, l, v, 12)
        for j, ch in enumerate('rgb'):
            getattr(b.par, 'bgcolor' + ch).expr = "%g * (1.0 if op('%s').par.Fuente == '%s' else 0.3)" % (v[j], ESC, m)
        b.store('tipo', 'FUENTE'); b.store('dato', m)
        lista.append(b)
    tw = (cw - 8) // 3
    th = tw * 9 // 16
    alto = th + 20 + 24 + 8
    y0 = ytop - 34
    # solo las camaras que existen en este show (show.Hay{N}, pestana Dispositivos; sin ella, las 6)
    SH = op('/project2/show')
    def _hay(i):
        p = getattr(SH.par, 'Hay%d' % i, None) if SH is not None else None
        return True if p is None else bool(p.eval())
    activas = [i for i in range(1, 7) if _hay(i)]
    filas = max(1, (len(activas) + 2) // 3)
    for n, i in enumerate(activas):
        px, py = x + (n % 3) * (tw + 4), y0 - (n // 3 + 1) * alto
        # borde encendido = la Camara unica elegida (la que ven las escenas de una camara), este la escena que este
        act = "(op('%s').par.Menu2 == 'CAM_%d')" % (ESC, i)
        c, d = marco(ui, 'th_cam_%d' % i, px, py + 44, tw, th, None, act, v)
        d.par.top.expr = "op('%s/CAM_%d')" % (ESC, i)
        c.store('tipo', 'CAM'); c.store('dato', 'CAM_%d' % i)
        lista.append(c)
        av = texto(ui, 'aviso_cam%d' % i, px + 6, py + 44 + th // 2 - 16, tw - 12, 32, 'SIN SEÑAL', (0.85, 0.10, 0.10), 15)
        av.par.display.expr = "op('ui_lib').module.sin_senal(%d)" % i
        setp(av, ['layer'], 5)
        lista.append(av)
        lista.append(texto(ui, 'mon_txt%d' % i, px, py + 24, tw, 20, "op('%s').par.Nombre%d.eval().upper()" % (ESC, i), (0.1, 0.1, 0.11), 12, expr=True))
        fw = tw // 3
        sw = "op('%s/cam%d_fuente')" % (ESC, i)
        for k, (m, l) in enumerate((('solido', 'SOL'), ('stock', 'VID'), ('vivo', 'VIVO'))):
            b = texto(ui, 'btn_cam%d_%s' % (i, m), px + k * fw, py, fw - 1, 22, l, v, 10)
            for j, ch in enumerate('rgb'):
                getattr(b.par, 'bgcolor' + ch).expr = "%g * (1.0 if %s.par.index == %d else 0.22)" % (v[j], sw, k)
            b.store('tipo', 'CAMFUENTE'); b.store('dato', '%d:%s' % (i, m))
            lista.append(b)
    ybajo = y0 - filas * alto - 6
    pc = panel(ui, parameterCOMP, 'par_cams', x, GAP, cw, ybajo - GAP)      # un panel, pestanas nativas arriba
    setp(pc, ['op'], "op('%s')" % ESC, expr=True)
    setp(pc, ['pagescope'], 'Camaras Slots')
    setp(pc, ['pagenames'], True)
    # Nombre / Lugares solo de las camaras que existen (el MULTIVIEW lee SLOT_1..Int)
    _noms = ' '.join('Nombre%d' % i for i in activas) or 'Nombre1'
    _slots = ' '.join('Slot%d' % i for i in range(1, len(activas) + 1)) or 'Slot1'
    setp(pc, ['parscope'], _noms + ' Int Menu2 Camfit Vivoprendido ' + _slots + ' Rotar*')
    setp(pc, ['builtin'], False)
    setp(pc, ['custom'], True)
    setp(pc, ['header'], False)
    lista.append(pc)
    tagear(tag, lista)


def solo_visuales():
    p = project.folder + '/proyecto.json'
    return os.path.exists(p) and not json.load(open(p, encoding='utf-8')).get('modulos', {}).get('escena_modular', True)


def build():
    global TH_COLS
    solo = solo_visuales()
    if solo:
        TH_COLS = 8      # VISUAL ocupa dos columnas: 2 filas de 8, como los pads
    ui = R.op('ui_perform') or R.create(containerCOMP, 'ui_perform')
    ui.par.w, ui.par.h = W, H
    ui.comment = 'UI de perform · builders/herramientas/setup_ui.py'
    color(ui, BG)
    for c in list(ui.children):
        if c.valid:
            c.destroy()
    lib = ui.create(textDAT, 'ui_lib')
    lib.text = UI_LIB
    lib.nodeX, lib.nodeY = -400, 0
    # estado de las camaras en vivo y de la salida NDI (los leen sin_senal / ndi_estado de ui_lib)
    if op(ESC) is not None:
        for i in range(1, 7):
            ic = ui.create(infoCHOP, 'info_cam%d' % i)
            ic.par.op = '%s/cam%d_vivo' % (ESC, i)
            ic.nodeX, ic.nodeY = -400, -150 * i
    ic = ui.create(infoCHOP, 'info_ndi')
    ic.par.op = '/project1/ndiout1'
    ic.nodeX, ic.nodeY = -400, -150 * 7
    # orden preferido al principio; lo que no esta en la lista (MIDI, Ensayo, futuras) queda al final en su orden
    _order_pref = ('Correccion de color', 'Paleta', 'Audio', 'Resolucion', 'MIDI', 'Ensayo')
    _show = R.op('show')
    _first = [n for n in _order_pref if any(g.name == n for g in _show.customPages)]
    _rest = [g.name for g in _show.customPages if g.name not in _first]
    _show.sortCustomPages(*(_first + _rest))
    hay_fx = tiene_pagina(list(range(18, 33)), 'Filter')
    cw = (W - GAP * 4) // 3
    estado = ("'%s'"
              " + {9: '   ·   BEATSTEP CH 9: ESCENAS', 10: '   ·   BEATSTEP CH 10: VISUALES / FX', 11: '   ·   BEATSTEP CH 11: VISUALES / FX'}.get(int(op('/project2/bs_canal')['canal']), '')"
              " + ('   ·   MASTER EN NEGRO' if op('/project2/show').par.Master < 0.98 else '')"
              " + ('   ·   GRABANDO' if ((op('%s') is not None and op('%s').par.Rec) or getattr(op('/project2/show').par, 'Rec', 0)) else '')"
              % (project.name.replace('.toe', ''), ESC, ESC))
    BW = 200      # botones de la barra: EXTRAS · MODO SHOW · ACTUALIZAR THUMBS · RESET FEEDBACK
    texto(ui, 'titulo', 0, H - TOP_H, W - 4 * (BW + 10) - 100, TOP_H, estado, (0.1, 0.1, 0.11), 20, expr=True)
    # FPS: verde a la velocidad del proyecto, se va a rojo conforme baja (60 % o menos = rojo)
    fps = "(1.0 / max(absTime.stepSeconds, 0.001))"
    t3 = texto(ui, 'bar_fps', W - 4 * (BW + 10) - 94, H - TOP_H + 4, 84, TOP_H - 8, "str(int(round(%s))) + ' FPS'" % fps,
               (0.1, 0.4, 0.2), 15, expr=True)
    salud = "max(0.0, min(1.0, (%s / project.cookRate - 0.6) / 0.35))" % fps
    for k, ch in enumerate('rgb'):
        getattr(t3.par, 'bgcolor' + ch).expr = '%g + (%g - %g) * %s' % ((0.85, 0.10, 0.10)[k], (0.10, 0.50, 0.25)[k], (0.85, 0.10, 0.10)[k], salud)
    # EXTRAS: con el candado puesto decide si tambien se bloquean los ajustes del soundcheck (Candadoajustes).
    # Naranja = bloqueados; sin MODO SHOW se ve apagado.
    caj = "bool(getattr(op('/project2/show').par, 'Candadoajustes', 0))"
    cand = "bool(getattr(op('/project2/show').par, 'Modoshow', 0))"
    b = texto(ui, 'btn_candadoaj', W - 4 * (BW + 10), H - TOP_H + 4, BW, TOP_H - 8,
              "'PARAMETROS EXTRAS' + chr(10) + ('BLOQUEADOS' if %s else 'LIBRES')" % caj, (0.25, 0.25, 0.27), 13, expr=True)
    for k, (on, off) in enumerate(((0.85, 0.25), (0.45, 0.25), (0.10, 0.27))):
        getattr(b.par, 'bgcolor' + 'rgb'[k]).expr = '(%g if %s else %g) * (1.0 if %s else 0.45)' % (on, caj, off, cand)
    b.store('tipo', 'CANDADOAJ')
    b.store('dato', '')
    # MODO SHOW (candado): rojo = puesto (setup_modo_show.py)
    b = texto(ui, 'btn_modoshow', W - 3 * (BW + 10), H - TOP_H + 4, BW, TOP_H - 8,
              "'MODO SHOW  ·  CANDADO' if %s else 'MODO SHOW'" % cand, (0.25, 0.25, 0.27), 15, expr=True)
    for k, (on, off) in enumerate(((0.80, 0.25), (0.10, 0.25), (0.10, 0.27))):
        getattr(b.par, 'bgcolor' + 'rgb'[k]).expr = '%g if %s else %g' % (on, cand, off)
    b.store('tipo', 'MODOSHOW')
    b.store('dato', '')
    b = texto(ui, 'btn_thumbs', W - 2 * (BW + 10), H - TOP_H + 4, BW, TOP_H - 8, 'ACTUALIZAR THUMBS', (0.25, 0.25, 0.27), 15)
    for k, ch in enumerate('rgb'):          # apagado con candado: no hace nada
        getattr(b.par, 'bgcolor' + ch).expr = '%g if %s else %g' % (0.10, cand, (0.25, 0.25, 0.27)[k])
    b.store('tipo', 'THUMBS')
    b.store('dato', '')
    b = texto(ui, 'btn_resetfb', W - (BW + 10), H - TOP_H + 4, BW, TOP_H - 8, 'RESET FEEDBACK', (0.55, 0.12, 0.12), 15)
    b.store('tipo', 'RESETFB')
    b.store('dato', '')
    top = H - TOP_H - GAP
    x1, x2, x3 = GAP, GAP * 2 + cw, GAP * 3 + 2 * cw
    y0 = top - TITLE_H - TAB_H - 8
    # VISUAL
    vis = "op('ui_lib').module.activo('VISUAL')"
    cv = cw * 2 + GAP if solo else cw
    texto(ui, 'tit_visual', x1, top - TITLE_H, cv, TITLE_H, 'VISUAL', tuple(c * 0.55 for c in COL['VISUAL']), 20)
    contenido(ui, 'VISUAL', x1, y0, cv, vis, 'Visual', "op('/project2/master_visuales')", None,
              "'VISUAL  ·  ' + op('ui_lib').module.nombre(%s)" % vis)
    tabs = []
    if not solo:
        # ESCENA / FX / CAMARAS
        esc = "op('ui_lib').module.activo('ESCENA')"
        fx = "op('ui_lib').module.activo('FX')"
        texto(ui, 'tit_escena', x2, top - TITLE_H, cw, TITLE_H, 'ESCENA', tuple(c * 0.55 for c in COL['ESCENA']), 20)
        tabs = ([('fx', 'FX')] if hay_fx else []) + [('escena', 'ESCENA'), ('cams', 'CAMARAS')]
        pestanas(ui, 'media', x2, top - TITLE_H - TAB_H - 4, cw, tabs, COL['ESCENA'])
        contenido(ui, 'ESCENA', x2, y0, cw, esc, 'Layout', "op('%s/master_video')" % ESC, 'tab_media_escena',
                  "op('ui_lib').module.tipo_escena(%s) + '  ·  ' + op('ui_lib').module.nombre(%s)" % (esc, esc))
        if hay_fx:
            contenido(ui, 'FX', x2, y0, cw, fx, 'Filter', "op('/project2/master_fx')", 'tab_media_fx',
                      "'FX  ·  ' + op('ui_lib').module.nombre(%s)" % fx)
        camaras(ui, x2, y0, cw, 'tab_media_cams')
    # SHOW
    hay_audio_vivo = getattr(R.op('show').par, 'Autonivel', None) is not None      # setup_audio_global.py
    # titulo de SHOW = estado de la salida NDI (rojo si esta apagada o nadie la recibe)
    nd = "op('ui_lib').module.ndi_estado()"
    ts = texto(ui, 'tit_show', x3, top - TITLE_H, cw, TITLE_H, "'SHOW   ·   ' + (%s[0] or 'salida final')" % nd,
               tuple(c * 0.55 for c in COL['SHOW']), 20, expr=True)
    for k, ch in enumerate('rgb'):
        getattr(ts.par, 'bgcolor' + ch).expr = '%g if %s[1] else %g' % (COL['SHOW'][k] * 0.55, nd, (0.85, 0.10, 0.10)[k])
    pestanas(ui, 'show', x3, top - TITLE_H - TAB_H - 4, cw,
             [('hub', 'CONTROLES')] + ([('audio', 'AUDIO EN VIVO')] if hay_audio_vivo else [])
             + [(k, l) for k, l, _ in FX_GLOBALES], COL['SHOW'])
    w_expr, h_expr = _preview_expr(cw)
    cont_show = imagen(ui, 'prev_show', x3, y0 - (PREV_H - 8), cw, PREV_H - 8, "op('/project1/ndiout1')")
    _bind_preview_dims(cont_show, x3, y0, cw, w_expr, h_expr)
    ys = y0 - PREV_H - 6
    # emergencia, siempre a la vista: BLACKOUT (fundido de 0.8 s a negro; otro toque regresa)
    negro = "(op('/project2/show').par.Master < 0.5)"
    b = texto(ui, 'btn_blackout', x3, ys - 46, cw, 46, "'EN NEGRO  ·  TOCA PARA VOLVER' if %s else 'BLACKOUT'" % negro,
              (0.45, 0.10, 0.10), 17, expr=True)
    b.par.bgcolorr.expr = '0.95 if %s else 0.45' % negro
    b.store('tipo', 'BLACKOUT')
    b.store('dato', '')
    ys -= 52
    # AUDIO EN VIVO: onda y bandas + lo que se toca por track (Autonivel · Reaccion · Suavizado · Gain)
    if hay_audio_vivo:
        a1 = panel(ui, opviewerCOMP, 'onda_vivo', x3, ys - 120, cw, 116)
        setp(a1, ['opviewer'], "op('/project2/audio/audio_gain')", expr=True)
        a2 = panel(ui, opviewerCOMP, 'bandas_vivo', x3, ys - 196, cw, 72)
        setp(a2, ['opviewer'], "op('/project2/audio/master_audio')", expr=True)
        ya = ys - 200 - 14
        bloques = []
        grupos = [('reaccion', 'Sepreaccion Autonivel Reaccion Suavizado', 4), ('nivel', 'Sepnivel Audiogain*', 2)]
        if getattr(R.op('show').par, 'Golpesens', None) is not None:       # Paleta Audio (si el show la tiene)
            grupos.append(('golpes', 'Sepgolpes Golpesens', 2))
        for clave, scope, filas in grupos:
            hb = filas * 23 + 8
            pa = panel(ui, parameterCOMP, 'par_show_audio_' + clave, x3, ya - hb, cw, hb)
            setp(pa, ['op'], "op('/project2/show')", expr=True)
            setp(pa, ['pagescope'], 'Audio')
            setp(pa, ['parscope'], scope)
            setp(pa, ['pagenames'], False)
            setp(pa, ['builtin'], False)
            setp(pa, ['custom'], True)
            setp(pa, ['header'], False)
            bloques.append(pa)
            ya -= hb + 30
        tagear('tab_show_audio', [a1, a2] + bloques)
    for k, opx, pag, alto in (('hub', "op('/project2/show')", '*', ys - 200),) + tuple((k, "op('%s')" % r, '*', ys) for k, _, r in FX_GLOBALES):
        pc = panel(ui, parameterCOMP, 'par_show_' + k, x3, GAP, cw, alto - GAP)
        setp(pc, ['op'], opx, expr=True)
        setp(pc, ['pagescope'], pag)
        setp(pc, ['pagenames'], k == 'hub')      # pestanas nativas dentro del panel
        setp(pc, ['builtin'], False)
        setp(pc, ['custom'], True)
        setp(pc, ['header'], False)
        pc.tags.add('tab_show_' + k)
        pc.store('h_con', alto - GAP)
        pc.store('h_sin', ys - GAP)
    w1 = panel(ui, opviewerCOMP, 'onda', x3, ys - 120, cw, 116)
    setp(w1, ['opviewer'], "op('/project2/audio/audio_gain')", expr=True)
    w2 = panel(ui, opviewerCOMP, 'bandas', x3, ys - 196, cw, 72)
    setp(w2, ['opviewer'], "op('/project2/audio/master_audio')", expr=True)
    tagear('tab_show_hub', [w1, w2])
    vx = ui.create(parameterexecuteDAT, 'onda_toggle')
    vx.par.op = '/project2/show'
    vx.par.pars = 'Vermonitor'
    vx.par.valuechange = True
    vx.text = chr(10).join(['def onValueChange(par, prev):', "    op('ui_lib').module.ondas()", '    return', ''])
    px = ui.create(panelexecuteDAT, 'th_click')
    px.par.panels = 'th_*/img_p btn_*'     # el click lo recibe la imagen, no el marco
    px.par.panelvalue = 'lselect'
    px.par.offtoon = True
    px.par.ontooff = False
    px.par.valuechange = False
    px.text = chr(10).join(['def onOffToOn(panelValue):', '    c = panelValue.owner',
                            "    c = c.parent() if c.name == 'img_p' else c",
                            # defensivo (1): si el panel no tiene 'tipo' almacenado, lo ignoramos.
                            # Esto protege de btn_* externos (p. ej. selector de camara) que no tienen contrato.
                            "    tipo = c.fetch('tipo', '', search=False)",
                            "    if not tipo:", "        return",
                            # defensivo (2): si el panel está en una pestaña inactiva (enable=False /
                            # display=False), ignoramos. Esto evita que un thumb de FX dispare acciones
                            # sobre thumbs de MULTIVIEW subyacentes y viceversa.
                            "    try:",
                            "        if not bool(c.par.enable.eval()): return",
                            "        if not bool(c.par.display.eval()): return",
                            "    except Exception:", "        pass",
                            "    op('ui_lib').module.elegir(tipo, c.fetch('dato', '', search=False))", '    return', ''])
    m = lib.module
    if not solo:
        m.tab('media', 'escena')
    m.tab('show', 'hub')
    return ui, tabs


def perform(ui):
    w = op('/perform') or op('/').create(windowCOMP, 'perform')
    w.par.winop = ui.path
    setp(w, ['winw'], W)
    setp(w, ['winh'], H)
    # La UI mide 1920x1080 en pixeles reales. Con la escala de Windows (125 %, 150 %) y 'usedpiscale'
    # se dibuja mas grande que el monitor y se corta arriba y a la derecha: se abre nativa y sin bordes.
    setp(w, ['dpiscaling'], 'native')
    setp(w, ['borders'], False)
    setp(w, ['justifyh'], 'left')
    setp(w, ['justifyv'], 'top')
    return w


def respaldo_ui_vieja():
    ops = [R.op(n) for n in UI_VIEJA if R.op(n) is not None]
    if not ops:
        return []
    r = R.op('_respaldo')
    d = r.op('ui_vieja') or r.create(baseCOMP, 'ui_vieja')
    d.copyOPs(ops)
    d.allowCooking = False
    out = [o.name for o in ops]
    for o in ops:
        o.destroy()
    return out


ui, secs = build()
if R.fetch('tdvj_ui_pendiente', False, search=False):      # la UI ya esta al dia: cancela la recarga pendiente
    R.unstore('tdvj_ui_pendiente')
w = perform(ui)
print('[ok] %s · pestanas centro: %s' % (ui.path, [t[1] for t in secs]))
print('[ok] UI vieja al respaldo:', respaldo_ui_vieja())

# Pestanas de thumbs por canal del Beatstep (BANCOS de ui_bancos.py): van encima de lo construido arriba
_p = project.folder + '/builders/herramientas/ui_bancos.py'
if os.path.exists(_p):
    exec(compile(open(_p, encoding='utf-8').read(), _p, 'exec'), dict(globals(), __file__=_p))
