# ui_bancos.py - mapa de pads del Beatstep y paginas de thumbs por canal. Idempotente.
# Sin MCP, en el Textport: exec(open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read())
# BANCOS es la fuente unica: de ahi salen table1, los pads, los thumbs de la UI, las luces y el Stream Deck
# (control/bancos.json -> gen_companion.py / gen_companion_xl.py).
# Cada canal tiene 16 lugares: 8 arriba (pads 1-8, notas 45-52) y 8 abajo (pads 9-16, notas 37-44).
# Cada pestana de la UI es un canal completo: 2 filas de 8, como los pads (pensado para shows de solo
# visuales: la columna VISUAL a dos columnas de ancho, modulos.escena_modular = false).
# Agregar o mover un visual = editar BANCOS y correr este script. setup_ui.py lo corre al final.
#
# PLANTILLA: BANCOS viene vacio -> este script no toca nada (table1, pads y luces quedan de fabrica).
# Portado de Casa Bacardi x Corona Capital (2026-11-15): solo la logica, sin sus visuales.
import json, os, re

# (nombre, entrada de switch2, TOP fuente del thumb); None = pad libre
GRUPOS = {9: 'OTROS', 10: 'VISUALES', 11: 'LOGOS'}      # cada canal es de un solo tipo (= pagina del Stream Deck)
BANCOS = {
    # Ejemplo (canal 10, pad 1 = visual de base1 en la entrada 0 de switch2):
    #   10: [('MI VISUAL', 0, '/project2/null5'), None, None, ...]     # 16 lugares por canal
    9: [None] * 16,
    10: [None] * 16,
    11: [None] * 16,
}

# Acomodo de setup_ui en cada columna: preview -> thumbs -> barra y RESET -> parametros.
# Una pagina por canal, en 8x2 y 16:9. En paneles de TD, y crece hacia arriba.
TH_POR_PAG, TH_COLS = 16, 8
X_COL, W_COL = 10, 1262                     # columna VISUAL (solo visuales: dos columnas de ancho)
W_GRID, X_GRID = W_COL, X_COL               # thumbs a todo lo ancho abajo del preview
Y_TOP = 664                                 # cabe una segunda fila de pestanas (LOGOS)
TH_W, TH_H, LAB_H, PASO_X, PASO_Y = 154, 86, 16, 158, 106
TAB_H = 26
Y_PREV, H_PREV, W_PREV = 670, 262, 466      # a la altura del preview de SHOW
Y_BARRA = 358
ACTIVO = (0.18, 0.49, 0.88)                 # azul de ESCENA
# entrada de switch2 -> fila de table1, solo si NO coinciden (p. ej. visuales que se agregaron despues
# y tienen su cadena de pad propia en otra fila). Vacio = fila N de table1 = entrada N de switch2.
FILA = {}
N_VISUALES = 16                             # entradas de switch2 que usa el show
# visuales que entran a switch2 despues de la entrada 16 (entrada, nombre del TOP en /project2). Ej: [(22, 'null26')]
CONEXIONES_EXTRA = []

# Paginas con contenido: (canal, primer pad, titulo de la pestana). Una pagina vacia no sale.
PAGINAS = [
    (canal, inicio, 'CH%d  %s' % (canal, GRUPOS.get(canal, '')))
    for canal in sorted(BANCOS)
    for inicio in (0, TH_POR_PAG)
    if any(BANCOS[canal][inicio:inicio + TH_POR_PAG])
]

LIB = '''
# ==== BANCOS: paginas de thumbs por canal (lo escribe ui_bancos.py) ====
_BANCOS = %r
_PAGINAS = %r
_ACTIVO = %r


def _ruta_thumb(dato):
    return 'assets/thumbs/v%%02d.jpg' %% dato


def banco_set(pagina):
    u = op('/project2/ui_perform')
    pagina = int(pagina)
    u.store('pagina_visual', pagina)
    canal, inicio, _ = _PAGINAS[pagina]
    for i, slot in enumerate(_BANCOS[canal][inicio:inicio + 16]):
        th = u.op('th_visual_%%d' %% i)
        lb = u.op('lab_visual_%%d' %% i)
        on = slot is not None
        th.par.display = th.par.enable = on
        lb.par.display = lb.par.enable = on
        ip = th.op('img_p')
        ip.par.display = ip.par.enable = on
        if not on:
            th.store('tipo', 'NONE')
            th.store('dato', -1)
            continue
        lb.par.text = '%%s   %%d-%%d' %% (slot[0], canal, inicio + i + 1)
        th.store('tipo', 'VISUAL')
        th.store('dato', slot[1])
        for k, ch in enumerate('rgb'):
            getattr(th.par, 'bgcolor' + ch).expr = "%%g * (1.0 if op('/project2/switch2').par.index == %%d else 0.22)" %% (_ACTIVO[k], slot[1])
        img = ip.op('img')
        img.par.file = _ruta_thumb(slot[1])
        img.par.reloadpulse.pulse()
    for n in range(len(_PAGINAS)):
        b = u.op('btn_pag_%%d' %% (n + 1))
        k = 1.0 if n == pagina else 0.3
        b.par.bgcolorr, b.par.bgcolorg, b.par.bgcolorb = [c * k for c in _ACTIVO]


_elegir_base = elegir


def elegir(tipo, dato):
    if tipo == 'BANCO':
        return banco_set(dato)
    return _elegir_base(tipo, dato)


def _fuentes():
    for slots in _BANCOS.values():
        for slot in slots:
            if slot is not None and op(slot[2]) is not None:
                yield slot[1], op(slot[2])


def actualizar_thumbs():
    # Captura todos los bancos, no solo la pestana abierta. Unos frames antes, para que
    # los visuales apagados y los de feedback arranquen y no salgan en negro.
    _thumbs_paso(20)
    return sum(1 for _ in _fuentes())


def _thumbs_paso(faltan):
    for dato, top in _fuentes():
        top.cook(force=True)
        if faltan == 0:
            top.save(project.folder + '/' + _ruta_thumb(dato))
    if faltan > 0:
        run("op('/project2/ui_perform/ui_lib').module._thumbs_paso(%%d)" %% (faltan - 1), delayFrames=1)
    else:
        banco_set(op('/project2/ui_perform').fetch('pagina_visual', 0, search=False))
''' % (BANCOS, PAGINAS, ACTIVO)

# Luces del Beatstep: la nota del visual al aire sale de table1; el mapeo entrada -> fila se inyecta
# desde FILA para que no se desincronice (bug Casa Bacardi 2026-11-10). Si el show tiene escena_modular
# y el canal 9 no esta en BANCOS, el canal 9 sigue prendiendo la escena al aire.
LUCES = '''def deseados():
	out = set()
	e = op('/project2/base17/escena_modular')
	if e is not None and %s:
		i = e.par.Modoescena.menuIndex
		if i is not None and i < 16:
			out.add((9, 45 + i if i < 8 else 29 + i))
	t = op('/project2/table1')
	k = int(op('/project2/switch2').par.index.eval())
	k = %s.get(k, k)
	m = re.match(r'ch(\\d+)n(\\d+)', t[k, 0].val) if k < t.numRows else None
	if m:
		out.add((int(m.group(1)), int(m.group(2))))
	return out

''' % (not any(BANCOS.get(9, [])), repr(FILA))


def nota(pad):
    return 45 + pad if pad < 8 else 29 + pad


def _aplicar():
    R = op('/project2')
    u = R.op('ui_perform')
    sw = R.op('switch2')

    # ---- Pads: fila N de table1 = entrada N de switch2 (o la de FILA) ----
    t = R.op('table1')
    canales = '|'.join(str(c) for c in sorted(BANCOS))
    for r in range(t.numRows):
        if re.match(r'ch(%s)n' % canales, t[r, 0].val):
            t[r, 0] = ''
    for canal, slots in BANCOS.items():
        for pad, slot in enumerate(slots):
            if slot is not None:
                t[FILA.get(slot[1], slot[1]), 0] = 'ch%dn%d' % (canal, nota(pad))

    # filas 16+ de table1: sus chopexec apuntaban al switch de FX; en un show sin FX van a switch2
    propias = set(FILA.values())
    for k in range(16, N_VISUALES):
        x = R.op('chopexec%d' % (k + 1))
        if x is None or k in propias:          # las de FILA tienen su cadena propia
            continue
        x.text = re.sub(r"elegir\('switch23', \d+\)", "elegir('switch2', %d)" % k, x.text)

    # ---- Stream Deck: mismas paginas que los bancos ----
    ctrl = project.folder + '/control'
    visuales = [{'base': slot[1] + 1, 'nombre': slot[0].title(), 'grupo': GRUPOS.get(canal, 'CH%d' % canal)}
                for canal in sorted(BANCOS) for slot in BANCOS[canal] if slot is not None]
    with open(ctrl + '/bancos.json', 'w', encoding='utf-8') as f:
        json.dump(visuales, f, ensure_ascii=False, indent=1)
    if os.path.exists(ctrl + '/show.json'):
        with open(ctrl + '/show.json', encoding='utf-8') as f:
            show = json.load(f)
        show['visuales'] = visuales
        with open(ctrl + '/show.json', 'w', encoding='utf-8') as f:
            json.dump(show, f, ensure_ascii=False, indent=1)
    esc = op('/project2/base17/escena_modular')
    if esc is not None:
        nombres = dict(esc.fetch('menu_nombres', {}, search=False))
        nombres['vis'] = {str(v['base']): v['nombre'] for v in visuales}
        esc.store('menu_nombres', nombres)

    # ---- Conexiones extra a switch2 (visuales despues de la entrada 16) ----
    for k, n in CONEXIONES_EXTRA:
        if len(sw.inputs) <= k and R.op(n) is not None:
            sw.inputConnectors[k].connect(R.op(n))
    m_vis = R.op('vis_knobs_lib').module
    for slots in BANCOS.values():
        for slot in slots:
            if slot is not None and slot[1] < len(sw.inputs):
                b = m_vis.resolve(sw.inputs[slot[1]])
                if b is not None:
                    b.store('nombre', slot[0].title())

    # ---- Luces del Beatstep: el pad del visual al aire ----
    ex = R.op('bs_luces_exec')
    if ex:
        txt = re.sub(r'def deseados\(\):.*?(?=def onFrameEnd)', LUCES.replace('\\', '\\\\'), ex.text, flags=re.S)
        if 'import re' not in txt:
            txt = 'import re\n' + txt
        ex.text = txt

    if u is None or u.op('th_visual_0') is None or u.op('lab_visual_0') is None:
        print('[aviso] la UI no tiene th_visual_0 (correr setup_ui.py): pads y Stream Deck listos, thumbs no')
        return
    if u.op('prev_escena') is not None:
        # con columna ESCENA los btn_pag_N son las paginas de escenas: las pestanas por canal son de solo visuales
        print('[aviso] show con ESCENA: pads y Stream Deck listos; los thumbs por canal son solo para shows de solo visuales')
        return
    if u.op('btn_pag_1') is None:          # VISUAL no se pagina en setup_ui: la primera pestana se crea aqui
        _texto = globals().get('texto')
        if _texto is not None:
            _texto(u, 'btn_pag_1', X_GRID, Y_TOP - TAB_H, 100, TAB_H, '', ACTIVO, 13)
        else:
            u.create(textCOMP, 'btn_pag_1')

    # ---- Paneles: 16 thumbs que se reusan en cada canal ----
    for c in list(u.children):
        if not c.valid:              # su DAT acoplado ya se fue con el panel
            continue
        m = re.fullmatch(r'(th|lab)_visual_(\d+)(_callbacks)?', c.name)
        if m and int(m.group(2)) >= TH_POR_PAG:
            c.destroy()
    # Pestanas en filas por tipo (usabilidad: lo mismo junto): VISUALES arriba, LOGOS abajo (si hay canales de logos)
    filas_tabs = [[i for i, p in enumerate(PAGINAS) if 'LOGO' not in GRUPOS[p[0]]],
                  [i for i, p in enumerate(PAGINAS) if 'LOGO' in GRUPOS[p[0]]]]
    filas_tabs = [f for f in filas_tabs if f]
    etiquetas = ['VISUALES' if 'LOGO' not in GRUPOS[PAGINAS[f[0]][0]] else 'LOGOS' for f in filas_tabs]
    y_fila1 = Y_TOP - len(filas_tabs) * (TAB_H + 4) - TH_H
    for i in range(TH_POR_PAG):
        th = u.op('th_visual_%d' % i) or u.copy(u.op('th_visual_0'), name='th_visual_%d' % i)
        lb = u.op('lab_visual_%d' % i) or u.copy(u.op('lab_visual_0'), name='lab_visual_%d' % i)
        cb = next((p for p in lb.pars() if p.label == 'Callbacks DAT'), None)
        if cb is not None:
            cb.val = ''
        x = X_GRID + (i % TH_COLS) * PASO_X
        y = y_fila1 - (i // TH_COLS) * PASO_Y
        th.par.x, th.par.y, th.par.w, th.par.h = x, y, TH_W, TH_H
        lb.par.x, lb.par.y, lb.par.w, lb.par.h = x, y - LAB_H, TH_W, LAB_H
        ip = th.op('img_p')
        ip.par.x, ip.par.y, ip.par.w, ip.par.h = 3, 3, TH_W - 6, TH_H - 6
        ip.par.top = ip.op('img').path          # una copia sigue apuntando a la imagen de th_visual_0
        th.par.bgalpha.mode = ParMode.CONSTANT
        th.par.bgalpha.val = 1

    # Pestanas: el click pasa por th_click -> elegir('BANCO', pagina). Una fila por tipo con su etiqueta a la izquierda;
    # todas del mismo ancho (la fila corta queda alineada a la izquierda).
    n_pag = len(PAGINAS)
    w_eti = 110 if len(filas_tabs) > 1 else 0
    n_cols = max(len(f) for f in filas_tabs)
    w_tab = (W_GRID - w_eti - (4 if w_eti else 0) - 4 * (n_cols - 1)) // n_cols
    for c in list(u.children):
        if re.fullmatch(r'btn_pag_(\d+)', c.name) and int(c.name.rsplit('_', 1)[1]) > n_pag:
            c.destroy()
        if re.fullmatch(r'eti_tabs_(\d+)', c.name) and int(c.name.rsplit('_', 1)[1]) >= (len(filas_tabs) if w_eti else 0):
            c.destroy()
    for fi, fila in enumerate(filas_tabs):
        y_tab = Y_TOP - TAB_H - fi * (TAB_H + 4)
        x0 = X_GRID + (w_eti + 4 if w_eti else 0)
        if w_eti:
            et = u.op('eti_tabs_%d' % fi) or u.copy(u.op('btn_pag_1'), name='eti_tabs_%d' % fi)
            et.par.text = etiquetas[fi]
            et.par.x, et.par.y, et.par.w, et.par.h = X_GRID, y_tab, w_eti, TAB_H
            et.par.display, et.par.enable = True, False        # etiqueta: no se toca
            for k, ch in enumerate('rgb'):
                getattr(et.par, 'bgcolor' + ch).mode = ParMode.CONSTANT
                getattr(et.par, 'bgcolor' + ch).val = (0.09, 0.09, 0.10)[k]
            et.store('tipo', '')
        for j, i in enumerate(fila):
            b = u.op('btn_pag_%d' % (i + 1)) or u.copy(u.op('btn_pag_1'), name='btn_pag_%d' % (i + 1))
            b.par.text = PAGINAS[i][2]
            b.par.x, b.par.y, b.par.w, b.par.h = x0 + j * (w_tab + 4), y_tab, w_tab, TAB_H
            b.par.display = b.par.enable = True
            b.store('tipo', 'BANCO')
            b.store('dato', i)
            cb = next((p for p in b.pars() if p.label == 'Callbacks DAT'), None)     # sin Callbacks DAT propio
            if cb is not None:
                cb.val = ''

    # Preview arriba, thumbs abajo, y al final barra, RESET y parametros a todo lo ancho
    pv = u.op('prev_visual')
    if pv is not None:
        for n in ('x', 'y', 'w', 'h'):           # setup_ui ata el preview al aspecto por expresion
            getattr(pv.par, n).mode = ParMode.CONSTANT
        pv.par.x, pv.par.y, pv.par.w, pv.par.h = X_COL + (W_COL - W_PREV) // 2, Y_PREV, W_PREV, H_PREV
    tv = u.op('tipo_visual')
    if tv:
        tv.par.x, tv.par.y, tv.par.w, tv.par.h = X_COL, Y_BARRA, W_COL - 130, 34
        tv.par.display = tv.par.enable = True
    r = u.op('btn_reset_visual')
    if r:
        r.par.x, r.par.y, r.par.w, r.par.h = X_COL + W_COL - 124, Y_BARRA, 124, 34
    pc = u.op('par_visual')
    if pc:
        pc.par.x, pc.par.y, pc.par.w, pc.par.h = X_COL, 10, W_COL, Y_BARRA - 14

    lib = u.op('ui_lib')
    txt = lib.text
    for marca in ('# ==== PAGINACION', '# ==== BANCOS'):
        k = txt.find(marca)
        if k >= 0:
            txt = txt[:k]
    lib.text = txt.rstrip() + '\n\n' + LIB.lstrip('\n')

    lib.module.banco_set(0)
    print('[ok] pads y paginas de thumbs:', [p[2] for p in PAGINAS])


if PAGINAS:
    _aplicar()
else:
    print('[ui_bancos] BANCOS vacio: table1, pads, luces y thumbs se quedan de fabrica')
