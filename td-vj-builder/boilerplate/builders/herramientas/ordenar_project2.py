# ─────────────────────────────────────────────────────────────
# ordenar_project2.py — acomoda /project2 por CADENAS (una fila por señal, de izquierda a derecha
# como fluye) y por GRUPOS (recuadros de color). SOLO mueve, pinta y pone recuadros: no conecta,
# no borra, no cambia parametros. Guarda antes las posiciones en control/ordenar_project2_respaldo.json.
#
#   VISUALES      baseN · nullN · vidN · switchN  -> switch2 -> level1 -> out1 -> null19 (a /project1)
#   FX            baseN · nullN                   -> switch23 -> level2 -> out2 -> null28
#   PADS VISUALES constantN -> logicN -> chopexecN   (los que mueven switch2)
#   PADS FX       constantN -> logicN -> chopexecN   (los que mueven switch23)
#   MIDIMIX       vis_knobs_* · fx_knobs_*  (una fila cada uno)
#   MIDI Y TABLAS MIDI · table1 · play · constant34 · folder1 ...
#   UI            ui_* (perform) y lo que quede de la UI vieja
#   SISTEMA       td_mcp · _respaldo · lo demas
# Colores = los del Stream Deck (morado visuales · naranja FX · turquesa control · gris lo demas).
#
# RESTAURAR = True -> regresa todo a como estaba en el respaldo.
# ─────────────────────────────────────────────────────────────
import json, os, re

RESTAURAR = False
R = op('/project2')
RESPALDO = project.folder + '/control/ordenar_project2_respaldo.json'
DX, DY = 200, 140
GAP = 420

MORADO = (0.64, 0.23, 0.77)
NARANJA = (0.91, 0.45, 0.11)
TURQUESA = (0.08, 0.72, 0.72)
VERDE = (0.13, 0.70, 0.35)
GRIS = (0.45, 0.45, 0.45)
AZUL = (0.18, 0.49, 0.88)


def _n(name):
    m = re.search(r'(\d+)$', name)
    return int(m.group(1)) if m else 0


def _null_de(base):
    """El nullTOP de /project2 que recibe el out1 del base."""
    for oc in base.outputConnectors:
        for c in oc.connections:
            if c.owner.parent() == R:
                return c.owner
    o = base.op('out1')
    if o is not None:
        for oc in o.outputConnectors:
            for c in oc.connections:
                if c.owner.parent() == R:
                    return c.owner
    return None


def cadenas_visuales():
    rows = []
    s2 = R.op('switch2')
    for sw in (s2.inputs if s2 else []):
        ins = sw.inputs
        vid = next((i for i in ins if i.OPType == 'moviefileinTOP'), None)
        nul = next((i for i in ins if i.OPType == 'nullTOP'), None)
        base = nul.inputs[0].parent() if nul is not None and nul.inputs else None
        rows.append([base, nul, vid, sw])
    tail = [s2]
    o = s2
    for _ in range(4):
        nxt = [c.owner for oc in o.outputConnectors for c in oc.connections if c.owner.parent() == R]
        if not nxt:
            break
        o = nxt[0]
        tail.append(o)
    return rows, tail


def cadenas_fx():
    rows = []
    s = R.op('switch23')
    for nul in (s.inputs if s else []):
        base = nul.inputs[0].parent() if nul.inputs else None
        rows.append([base if base is not None and base.parent() == R else None, nul])
    tail = [s]
    o = s
    for _ in range(4):
        nxt = [c.owner for oc in o.outputConnectors for c in oc.connections if c.owner.parent() == R]
        if not nxt:
            break
        o = nxt[0]
        tail.append(o)
    return rows, tail


def pads():
    vis, fx, otros = [], [], []
    for d in sorted(R.findChildren(type=chopexecuteDAT, depth=1), key=lambda d: _n(d.name)):
        if d.name.startswith(('vis_knobs', 'fx_knobs')):
            continue
        lg = op(d.par.chops.eval()) if d.par.chops.eval() else None
        lg = lg if lg is not None and lg.parent() == R else None
        src = lg.inputs[0] if lg is not None and lg.inputs else None
        row = [src, lg, d]
        if "op('switch2')" in d.text:
            vis.append(row)
        elif "op('switch23')" in d.text:
            fx.append(row)
        else:
            otros.append(row)
    return vis, fx, otros


def knobs():
    rows = []
    for pre in ('vis_knobs', 'fx_knobs'):
        row = [R.op('%s_%s' % (pre, s)) for s in ('in', 'lag', 'exec', 'lib', 'map', 'parexec', 'cook')]
        if any(row):
            rows.append(row)
    return rows


def recuadro(titulo, x0, y0, x1, y1, color):
    name = 'zona_' + re.sub(r'\W+', '_', titulo.lower()).strip('_')
    a = R.op(name)
    if a is None:
        a = R.create(annotateCOMP)
        a.name = name             # create() ignora el nombre en los annotate: se renombra despues
    a.nodeX, a.nodeY = x0 - 80, y1 - 90
    a.nodeWidth, a.nodeHeight = (x1 - x0) + 160 + 160, (y0 - y1) + 90 + 200
    for pn, v in (('Titletext', titulo), ('Bodytext', '')):
        if hasattr(a.par, pn):
            setattr(a.par, pn, v)
    for k, c in enumerate('rgb'):
        p = getattr(a.par, 'Backcolor' + c, None)
        if p is not None:
            p.val = color[k] * 0.35
    if hasattr(a.par, 'Backcoloralpha'):
        a.par.Backcoloralpha = 0.22
    return a


placed = set()


def poner(rows, x, y, color, tail=None, titulo=''):
    """rows = listas de ops (None = hueco). tail = cadena final, centrada a la derecha."""
    ancho = max([len(r) for r in rows] + [1])
    for j, row in enumerate(rows):
        for i, o in enumerate(row):
            if o is None or o.path in placed:
                continue
            o.nodeX, o.nodeY = x + i * DX, y - j * DY
            o.color = color
            placed.add(o.path)
    xt = x + ancho * DX + 60
    yc = y - (len(rows) - 1) * DY / 2.0
    for i, o in enumerate(tail or []):
        if o is None or o.path in placed:
            continue
        o.nodeX, o.nodeY = xt + i * DX, int(yc)
        o.color = color
        placed.add(o.path)
    x1 = xt + (len(tail or []) - 1) * DX if tail else x + (ancho - 1) * DX
    y1 = y - (max(len(rows), 1) - 1) * DY
    if titulo:
        recuadro(titulo, x, y, x1, y1, color)
    return x1


def respaldo():
    if os.path.exists(RESPALDO) and not os.path.exists(RESPALDO.replace('.json', '_original.json')):
        import shutil
        shutil.copy(RESPALDO, RESPALDO.replace('.json', '_original.json'))   # el de antes del primer acomodo
    data = {o.path: [o.nodeX, o.nodeY, list(o.color)] for o in R.children}
    os.makedirs(os.path.dirname(RESPALDO), exist_ok=True)
    with open(RESPALDO, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=0)


def restaurar():
    data = json.load(open(RESPALDO, encoding='utf-8'))
    for path, (x, y, col) in data.items():
        o = op(path)
        if o is not None:
            o.nodeX, o.nodeY, o.color = x, y, tuple(col)
    for a in R.findChildren(type=annotateCOMP, depth=1, name='zona_*'):
        a.destroy()
    print('[ok] restaurado')


def alto(rows):
    return (max(len(rows), 1) - 1) * DY


def run():
    """De ARRIBA a ABAJO, por bloques; en cada bloque una fila por cadena (izquierda -> derecha):
       1 CONTROL   pads visuales · pads FX · MIDImix · MIDI y tablas (lado a lado)
       2 VISUALES  baseN · null · vid · switch -> switch2 -> level1 -> out1 -> null19
       3 ESCENA / CAMARAS Y FX   base17 (escena) + FX -> switch23 -> level2 -> out2 -> null28
       4 SISTEMA   hub show · ui_perform · td_mcp · _respaldo · lo demas"""
    if RESTAURAR:
        restaurar()
        return
    respaldo()
    for a in [o for o in R.children if o.OPType == 'annotateCOMP' and (o.name.startswith('zona_') or o.name.startswith('annotate'))]:
        a.destroy()               # recuadros de corridas anteriores (los annotateN salieron de un bug)
    y = 0
    # 1 CONTROL (lado a lado)
    pv, pf, po = pads()
    kr = knobs()
    mid = [o for o in (R.op(n) for n in ('MIDI', 'table1', 'play', 'constant34', 'folder1', 'folder1_callbacks')) if o is not None]
    midrows = [mid[k:k + 2] for k in range(0, len(mid), 2)]
    x = 0
    x = poner(pv, x, y, MORADO, None, '1 CONTROL · PADS VISUALES  ·  constant -> logic -> chopexec (mueve switch2)') + GAP
    x = poner(pf, x, y, NARANJA, None, '1 CONTROL · PADS FX  ·  constant -> logic -> chopexec (mueve switch23)') + GAP
    x = poner(kr + [r for r in po], x, y, TURQUESA, None, '1 CONTROL · MIDIMIX  ·  fila 1 = visual activo · fila 2 = FX activo') + GAP
    poner(midrows, x, y, GRIS, None, '1 CONTROL · MIDI Y TABLAS  ·  table1 = notas de los pads · folder1 / constant34 = videos de visuales')
    y -= max(alto(pv), alto(pf), alto(kr), alto(midrows)) + DY + GAP
    # 2 VISUALES
    vr, vt = cadenas_visuales()
    poner(vr, 0, y, MORADO, vt, '2 VISUALES  ·  baseN · null · vid · switch  ->  switch2 (entrada N-1 = baseN)  ->  level1 -> out1 -> null19 (a /project1)')
    y -= alto(vr) + DY + GAP
    # 3 ESCENA / CAMARAS Y FX
    fr, ft = cadenas_fx()
    poner(fr, 0, y, NARANJA, ft, '3 ESCENA / CAMARAS Y FX  ·  base17 = escena_modular (entrada 0, sin FX) · baseN FX  ->  switch23  ->  level2 -> out2 -> null28 (a /project1)')
    y -= alto(fr) + DY + GAP
    # 4 SISTEMA
    sis = [o for o in (R.op(n) for n in ('show', 'ui_perform', 'td_mcp', '_respaldo')) if o is not None and o.path not in placed]
    resto = sorted([o for o in R.children if o.path not in placed and o not in sis and o.OPType != 'annotateCOMP'],
                   key=lambda o: (o.OPType, o.name))
    rows = [sis] + [resto[k:k + 6] for k in range(0, len(resto), 6)]
    poner(rows, 0, y, AZUL, None, '4 SISTEMA  ·  show = HUB (resolucion · audio · color) · ui_perform = UI de perform · td_mcp = MCP · _respaldo (no corre)')
    print('[ok] /project2 acomodado de arriba a abajo: %d nodos · respaldo en %s' % (len(placed), RESPALDO))
    print('     control: pads vis %d · pads fx %d · midimix %d · midi %d | visuales %d | fx %d | sistema %d + %d' % (
        len(pv), len(pf), len(kr), len(mid), len(vr), len(fr), len(sis), len(resto)))

run()
