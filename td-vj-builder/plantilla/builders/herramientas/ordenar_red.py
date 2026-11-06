# ─────────────────────────────────────────────────────────────
# ordenar_red.py — acomoda la red para que se navegue igual en todos los shows.
# SOLO mueve, pinta, comenta y pone recuadros con titulo: no conecta, no borra, no cambia parametros.
#
# /project2 (izquierda -> derecha, como fluye la senal):
#   ENTRADAS (MIDI, audio, OSC, pads) · VISUALES base1-16 · ESCENA base17 · FX base18-32 · SALIDAS · OTROS
# escena_modular (arriba -> abajo):
#   CAMARAS · LUGARES Y ROTACION · ESCENAS MULTIVIEW · ESCENAS SINGLE CAM · MEZCLA · CONTROL · OTROS
# Colores = los del Stream Deck: morado visuales · naranja FX · azul multiview · amarillo single cam ·
#   verde camaras · turquesa control / navegacion · gris lo demas.
#
# APPLY = False -> solo imprime que haria.  APPLY = True -> acomoda (guarda antes las posiciones en
#   control/ordenar_red_respaldo.json).  RESTAURAR = True -> regresa todo a como estaba en ese respaldo.
# Textport:  exec(open(project.folder + '/builders/herramientas/ordenar_red.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────
import json, os, re

APPLY = False
RESTAURAR = False

ROOT = '/project2'
SCENE = '/project2/base17/escena_modular'
RESPALDO = project.folder + '/control/ordenar_red_respaldo.json'
DX, DY = 220, 160        # separacion entre nodos
ZONA_GAP = 360           # separacion entre zonas

MORADO   = (0.64, 0.23, 0.77)
NARANJA  = (0.91, 0.45, 0.11)
AZUL     = (0.18, 0.49, 0.88)
AMARILLO = (0.85, 0.64, 0.00)
VERDE    = (0.13, 0.70, 0.35)
TURQUESA = (0.08, 0.72, 0.72)
GRIS     = (0.45, 0.45, 0.45)
ROJO     = (0.88, 0.14, 0.14)


def _num(name):
    m = re.match(r'base(\d+)$', name)
    return int(m.group(1)) if m else None


def zonas_project2(p):
    z = {k: [] for k in ('ENTRADAS', 'VISUALES', 'ESCENA', 'FX', 'SALIDAS', 'OTROS')}
    for o in p.children:
        n, k = o.name, _num(o.name)
        if o.OPType == 'annotateCOMP' and n.startswith('zona_'):
            continue
        if k is not None and 1 <= k <= 16:
            z['VISUALES'].append(o)
        elif k == 17:
            z['ESCENA'].append(o)
        elif k is not None and 18 <= k <= 45:
            z['FX'].append(o)
        elif re.match(r'(midi|audio|osc|logic|chopexec|bs_|fx_knobs|vis_knobs|scene_fader)', n):
            z['ENTRADAS'].append(o)
        elif re.match(r'(fit|out|switch|select|null|black|level|comp|over)', n):
            z['SALIDAS'].append(o)
        else:
            z['OTROS'].append(o)
    z['VISUALES'].sort(key=lambda o: _num(o.name))
    z['FX'].sort(key=lambda o: _num(o.name))
    for k in ('ENTRADAS', 'SALIDAS', 'OTROS'):
        z[k].sort(key=lambda o: (re.sub(r'\d+$', '', o.name), int(re.search(r'(\d*)$', o.name).group(1) or 0)))
    return [('ENTRADAS', z['ENTRADAS'], GRIS, 4), ('VISUALES', z['VISUALES'], MORADO, 4),
            ('ESCENA', z['ESCENA'], AZUL, 1), ('FX', z['FX'], NARANJA, 4),
            ('SALIDAS', z['SALIDAS'], TURQUESA, 3), ('OTROS', z['OTROS'], GRIS, 3)]


def zonas_escena(s):
    z = {k: [] for k in ('CAMARAS', 'LUGARES Y ROTACION', 'ESCENAS MULTIVIEW', 'ESCENAS SINGLE CAM',
                         'MEZCLA', 'CONTROL', 'OTROS')}
    for o in s.children:
        n = o.name
        if o.OPType == 'annotateCOMP' and n.startswith('zona_'):
            continue
        if n.startswith('layout_'):
            z['ESCENAS SINGLE CAM' if 'tdvj_fam_singlecam' in o.tags else 'ESCENAS MULTIVIEW'].append(o)
        elif re.match(r'(CAM_|videodevin|cam_|cam\d+_)', n):
            z['CAMARAS'].append(o)
        elif re.match(r'(SLOT_|rotar_)', n):
            z['LUGARES Y ROTACION'].append(o)
        elif re.match(r'(blend_switch|master_switch|switch|out|select|null)', n):
            z['MEZCLA'].append(o)
        elif re.match(r'(osc|companion|mix_feedback|demo_|bs_escenas|scene_fader|midi)', n):
            z['CONTROL'].append(o)
        else:
            z['OTROS'].append(o)
    menu = list(s.par.Modoescena.menuNames) if hasattr(s.par, 'Modoescena') else []
    for k in ('ESCENAS MULTIVIEW', 'ESCENAS SINGLE CAM'):       # en el orden del menu
        z[k].sort(key=lambda o: menu.index(o.name) if o.name in menu else 999)
    for k in ('CAMARAS', 'LUGARES Y ROTACION', 'MEZCLA', 'CONTROL', 'OTROS'):
        z[k].sort(key=lambda o: o.name)
    return [('CAMARAS', z['CAMARAS'], VERDE, 7), ('LUGARES Y ROTACION', z['LUGARES Y ROTACION'], VERDE, 7),
            ('ESCENAS MULTIVIEW', z['ESCENAS MULTIVIEW'], AZUL, 6),
            ('ESCENAS SINGLE CAM', z['ESCENAS SINGLE CAM'], AMARILLO, 6),
            ('MEZCLA', z['MEZCLA'], TURQUESA, 6), ('CONTROL', z['CONTROL'], TURQUESA, 6),
            ('OTROS', z['OTROS'], GRIS, 6)]


def comentario(o):
    n = o.name
    if n.startswith('layout_'):
        return 'Escena %s · builders/layouts/setup_%s.py' % (n.split('_', 2)[-1].replace('_', ' ').upper(), n)
    k = _num(n)
    if k is not None and 1 <= k <= 16:
        return 'Visual %s · builders/visuales/setup_%s_*.py' % (n, n)
    if k is not None and 18 <= k <= 45:
        return 'FX %s · builders/efectos/setup_%s_*.py' % (n, n)
    if n == 'base17':
        return 'Escena modular (camaras + escenas) · _lib/layout_core.py, _lib/camaras.py'
    return None


def recuadro(parent, titulo, x0, y0, x1, y1, color):
    name = 'zona_' + re.sub(r'\W+', '_', titulo.lower())
    a = parent.op(name)
    if a is None:
        a = parent.create(annotateCOMP, name)
    a.nodeX, a.nodeY = x0 - 60, y0 - 60
    a.nodeWidth, a.nodeHeight = (x1 - x0) + 120 + 160, (y1 - y0) + 120 + 140
    for pn, v in (('Titletext', titulo), ('Bodytext', '')):
        if hasattr(a.par, pn):
            setattr(a.par, pn, v)
    for i, c in enumerate('rgb'):
        p = getattr(a.par, 'Backcolor' + c, None)
        if p is not None:
            p.val = color[i] * 0.35
    if hasattr(a.par, 'Backcoloralpha'):
        a.par.Backcoloralpha = 0.25
    return a


def acomodar(parent, zonas, horizontal):
    """horizontal: zonas de izquierda a derecha (project2); si no, de arriba a abajo (escena)."""
    x, y = 0, 0
    for titulo, ops, color, cols in zonas:
        if not ops:
            continue
        rows = (len(ops) + cols - 1) // cols
        for i, o in enumerate(ops):
            if APPLY:
                o.nodeX = x + (i % cols) * DX
                o.nodeY = y - (i // cols) * DY
                if titulo != 'OTROS':          # lo no clasificado conserva su color
                    o.color = color
                c = comentario(o)
                if c and not o.comment:
                    o.comment = c
        w, h = (min(len(ops), cols) - 1) * DX, (rows - 1) * DY
        print('  %-20s %3d nodos  %s' % (titulo, len(ops), ', '.join(o.name for o in ops[:6]) + (' ...' if len(ops) > 6 else '')))
        if APPLY:
            recuadro(parent, titulo, x, y - h, x + w, y, color)
        if horizontal:
            x += w + ZONA_GAP + 160
        else:
            y -= h + ZONA_GAP


def respaldo(parents):
    data = {}
    for p in parents:
        for o in p.children:
            data[o.path] = [o.nodeX, o.nodeY, list(o.color), o.comment]
    os.makedirs(os.path.dirname(RESPALDO), exist_ok=True)
    with open(RESPALDO, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=0)
    print('[ok] posiciones guardadas en', RESPALDO)


def restaurar():
    with open(RESPALDO, encoding='utf-8') as f:
        data = json.load(f)
    n = 0
    for path, (x, y, col, com) in data.items():
        o = op(path)
        if o is not None:
            o.nodeX, o.nodeY, o.color, o.comment = x, y, tuple(col), com
            n += 1
    for p in (op(ROOT), op(SCENE)):
        for a in (p.findChildren(type=annotateCOMP, depth=1, name='zona_*') if p is not None else []):
            a.destroy()
    print('[ok] restaurados %d nodos (y quitados los recuadros)' % n)


def run():
    if RESTAURAR:
        restaurar()
        return
    p2, sc = op(ROOT), op(SCENE)
    print('==== ordenar_red (%s) ====' % ('APLICANDO' if APPLY else 'solo revision: APPLY = True para acomodar'))
    if APPLY:
        respaldo([x for x in (p2, sc) if x is not None])
    print('/project2  (izquierda -> derecha)')
    acomodar(p2, zonas_project2(p2), True)
    if sc is not None:
        print('escena_modular  (arriba -> abajo)')
        acomodar(sc, zonas_escena(sc), False)
    if APPLY:
        print('[ok] listo. Si algo no te gusta: RESTAURAR = True y vuelve a correrlo.')


run()
