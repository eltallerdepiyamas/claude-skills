"""
orden_escena.py — acomodo de escena_modular (mismo principio que /project2: bloques de ARRIBA a ABAJO,
una fila por cadena, recuadros del color del Stream Deck). SOLO mueve / pinta / recuadros.

  1 CONTROL   osc · companion · mix_feedback · demo_* · bs_escenas_* · scene_faders_* · prender_camaras ...
  2 ENTRADAS  una fila por camara: camN_solido · camN_stock · camN_vivo
              -> camN_fuente -> camN_lut -> camN_lut_sw -> CAM_N -> SLOT_N
     2E CAMARA UNICA (SLOT_UNICA + fundido) · 2F ROTACION · 2G PALETA AUDIO
  3 ESCENAS   una columna por familia (MULTIVIEW · SPLITSCREEN · SINGLE SHOT), cada una en el orden
              del menu (= entradas de blend_switch) -> blend_switch -> master_video
  4 OTROS     lo demas

  Los DAT acoplados (shaders e info de los GLSL) se esconden: host.showDocked = False.

  escenas(scene)  -> solo el bloque 3 (lo llama escena_registro.sincronizar: cada escena nueva se acomoda sola)
  acomodar(scene) -> todo (builders/herramientas/ordenar_escena.py)
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass
import re

DX, DY, GAP = 220, 150, 420
CX = 340                                   # separacion entre columnas de familias
VERDE, AZUL, AMARILLO, TURQUESA, GRIS = (0.13, 0.70, 0.35), (0.18, 0.49, 0.88), (0.85, 0.64, 0.0), (0.08, 0.72, 0.72), (0.45, 0.45, 0.45)
NARANJA = (0.90, 0.45, 0.10)
CONTROL = ('osc', 'companion', 'mix_feedback', 'demo_', 'bs_escenas', 'scene_fader', 'prender_camaras', 'midi',
           'vivoprendido', 'constant')
VIEJOS = ('LAYOUTS', 'ENTRADAS')            # recuadros de acomodos anteriores (annotateN)


def _caja(scene, titulo, x0, y0, x1, y1, rgb):
    name = 'zona_' + re.sub(r'\W+', '_', titulo.lower()).strip('_')[:40]
    a = scene.op(name)
    if a is None:
        a = scene.create(annotateCOMP)
        a.name = name                       # create() ignora el nombre en los annotate
    a.nodeX, a.nodeY = x0 - 80, y1 - 90
    a.nodeWidth, a.nodeHeight = (x1 - x0) + 320, (y0 - y1) + 290
    a.par.Titletext = titulo
    a.par.Backcolorr, a.par.Backcolorg, a.par.Backcolorb = [c * 0.35 for c in rgb]
    a.par.Backcoloralpha = 0.22


def _filas(rows, x, y, rgb, hecho):
    for j, row in enumerate(rows):
        for i, o in enumerate(row):
            if o is not None:
                o.nodeX, o.nodeY = x + i * DX, y - j * DY
                o.color = rgb
                hecho.add(o.path)
    w = max([len(r) for r in rows] + [1])
    return x + (w - 1) * DX, y - (max(len(rows), 1) - 1) * DY


def _cadena(ops):
    """Ordena un grupo de izquierda a derecha siguiendo sus cables (fuentes primero)."""
    paths = {o.path for o in ops}
    prof = {}

    def p(o, pila=()):
        if o.path in prof:
            return prof[o.path]
        if o.path in pila:
            return 0
        ins = [i for i in o.inputs if i is not None and i.path in paths]
        prof[o.path] = (1 + max(p(i, pila + (o.path,)) for i in ins)) if ins else 0
        return prof[o.path]

    return sorted(ops, key=lambda o: (_tipo(o), p(o), o.name))


TIPOS = ('TOP', 'CHOP', 'SOP', 'MAT', 'COMP', 'DAT')


def _tipo(o):
    """Nunca se mezclan tipos: en cada fila van primero los TOP, luego CHOP ... y al final los DAT."""
    return TIPOS.index(o.family) if o.family in TIPOS else len(TIPOS)


def _familia(l):
    if 'tdvj_fam_singlecam' in l.tags:
        return 2
    if 'tdvj_fam_splitscreen' in l.tags:
        return 1
    return 0


def _layouts_en_orden(scene):
    b = scene.op('blend_switch')
    out = []
    for src in (b.inputs if b is not None else []):
        o = src if src.parent() == scene else src.parent()
        if o.parent() == scene and o.name.startswith('layout_') and o not in out:
            out.append(o)
    out += sorted([c for c in scene.children if c.name.startswith('layout_') and c not in out], key=lambda c: c.name)
    return out


def escenas(scene, x=None, y=None, hecho=None, caja=True):
    """Bloque 3: una columna por familia, en el orden del menu, -> blend_switch -> master_video."""
    hecho = set() if hecho is None else hecho
    b, mo = scene.op('blend_switch'), scene.op('master_video')
    lays = _layouts_en_orden(scene)
    if not lays:
        return y
    if x is None or y is None:                     # solo escenas: se queda donde ya estaba el bloque
        x, y = min(l.nodeX for l in lays), max(l.nodeY for l in lays)
    cols = [[], [], []]
    for l in lays:
        cols[_familia(l)].append(l)
    j = 0                                          # una sola columna hacia abajo: azul, naranja, amarillo
    for col, rgb in zip(cols, (AZUL, NARANJA, AMARILLO)):
        for l in col:
            l.nodeX, l.nodeY = x, y - j * DY
            l.color = rgb
            hecho.add(l.path)
            j += 1
    y1 = y - (j - 1) * DY
    yc = (y + y1) / 2.0
    xb = x + 3 * DX
    xf = xb
    for o in (b, mo):                              # centrados a la altura de la columna, sin encimarse
        if o is not None:
            o.nodeX, o.nodeY = xf, int(yc - o.nodeHeight / 2.0 + 45)
            o.color = TURQUESA
            hecho.add(o.path)
            xf += o.nodeWidth + DX
    xb = xf - 2 * DX
    if caja:
        for a in [o for o in scene.children if o.OPType == 'annotateCOMP' and o.name.startswith('zona_3_')]:
            a.destroy()
        _caja(scene, '3 ESCENAS  ·  hacia abajo: MULTIVIEW (azul) · SPLITSCREEN (naranja) · SINGLE SHOT (amarillo) -> blend_switch -> master_video',
              x, y, xb + 2 * DX, y1, AZUL)
    return y1


def acomodar(scene):
    for a in [o for o in scene.children if o.OPType == 'annotateCOMP']:
        if a.name.startswith('zona_') or (re.match(r'annotate\d+$', a.name) and a.par.Titletext.eval().startswith(VIEJOS)):
            a.destroy()
    hecho, y = set(), 0
    kids = [o for o in scene.children if o.OPType != 'annotateCOMP']
    # DAT acoplados (shader / info de un GLSL): se esconden bajo su nodo
    acoplados = [o for o in kids if o.dock is not None and o.dock.parent() == scene and o.dock.family != 'DAT']
    for o in acoplados:
        hecho.add(o.path)

    def libres(pref):
        return [o for o in kids if o.name.startswith(pref) and o.path not in hecho]

    # 1 CONTROL (por prefijo, una fila cada uno, siguiendo los cables)
    grupos = {}
    for o in kids:
        if o.path in hecho:
            continue
        for p in CONTROL:
            if o.name.startswith(p):
                grupos.setdefault(p, []).append(o)
                break
    rows = [_cadena(v) for k, v in sorted(grupos.items())]
    x1, y1 = _filas(rows, 0, y, TURQUESA, hecho)
    _caja(scene, '1 CONTROL  ·  OSC / Companion · AJUSTES (mix_feedback) · DEMO / REC · Beatstep · faders', 0, y, x1, y1, TURQUESA)
    y = y1 - DY - GAP

    # 2 ENTRADAS: la camara N siempre en la fila N
    SEP = 520
    fuentes = [('solido', '2A SOLIDOS', AMARILLO), ('stock', '2B VIDEOS  ·  Movie File In', AZUL),
               ('vivo', '2C EN VIVO  ·  Video Device In', VERDE)]
    if any(scene.op('cam%d_negro' % i) is not None for i in range(1, 7)):
        fuentes.append(('negro', '2C NEGRO', GRIS))
    y1 = y
    for c, (k, titulo, rgb) in enumerate(fuentes):
        x = c * SEP
        x1, y1 = _filas([[scene.op('cam%d_%s' % (i, k))] for i in range(1, 7)], x, y, rgb, hecho)
        _caja(scene, titulo, x, y, x1, y1, rgb)
    rows = [[scene.op('cam%d_fuente' % i), scene.op('cam%d_lut' % i), scene.op('cam%d_lut_sw' % i),
             scene.op('CAM_%d' % i), scene.op('SLOT_%d' % i)] for i in range(1, 7)]
    rows.append([None, scene.op('cam_lut_file')])   # Hald compartido, bajo la columna del LUT
    chicos = [r[0] for r in rows[:6] if r[0] is not None]
    if chicos:                                      # los switch de fuente, todos del mismo tamano
        w, h = min(o.nodeWidth for o in chicos), min(o.nodeHeight for o in chicos)
        for o in chicos:
            o.nodeWidth, o.nodeHeight = w, h
    x0 = len(fuentes) * SEP
    x1, y1 = _filas(rows, x0, y, TURQUESA, hecho)
    _caja(scene, '2D camN_fuente (switch) -> camN_lut -> camN_lut_sw (LUT si / no) -> CAM_N (correccion de color) -> SLOT_N',
          x0, y, x1, y1, TURQUESA)
    # 2D DAT: shaders e info de esos GLSL, aparte de los TOP y en la fila de su camara
    xd = x1 + DX + GAP
    usados = set()
    drows = []
    for i in range(1, 7):
        hosts = [h.path for h in (scene.op('cam%d_lut' % i), scene.op('CAM_%d' % i)) if h is not None]
        fila = sorted([o for o in acoplados if o.dock.path in hosts], key=lambda o: (hosts.index(o.dock.path), o.name))
        usados.update(o.path for o in fila)
        drows.append(fila)
    drows.append([o for o in (scene.op('cam_lut_pixel'), scene.op('cam_cc_frag')) if o is not None] +
                 sorted([o for o in acoplados if o.path not in usados], key=lambda o: o.name))
    xd1, yd1 = _filas(drows, xd, y, GRIS, hecho)
    _caja(scene, '2D DAT  ·  shaders e info de camN_lut y CAM_N (fila N = camara N) · abajo: los compartidos', xd, y, xd1, yd1, GRIS)
    y = min(y1, yd1) - DY - GAP

    # 2E CAMARA UNICA (lo que alimenta SLOT_UNICA y su fundido)
    rows = [[scene.op('SLOT_UNICA_PREV'), scene.op('SLOT_UNICA_NOW'), scene.op('SLOT_UNICA')],
            _cadena([o for o in kids if o.name.startswith(('fade_', 'transicion_')) and o.path not in hecho])]
    x1, y1 = _filas(rows, 0, y, AMARILLO, hecho)
    _caja(scene, '2E CAMARA UNICA  ·  anterior + actual -> SLOT_UNICA · fundido entre camaras', 0, y, x1, y1, AMARILLO)
    y = y1 - DY - GAP

    # 2F ROTACION · 2G PALETA AUDIO
    for pref, titulo in (('rotar_', '2F ROTACION DE CAMARAS'), ('palaudio_', '2G PALETA AUDIO  ·  golpes contados por banda -> palaudio_out')):
        g = _cadena(libres(pref))
        if g:
            x1, y1 = _filas([g], 0, y, VERDE, hecho)
            _caja(scene, titulo, 0, y, x1, y1, VERDE)
            y = y1 - DY - GAP

    # 3 ESCENAS
    y1 = escenas(scene, 0, y, hecho)
    y = y1 - DY - GAP

    # 4 OTROS
    resto = [o for o in kids if o.path not in hecho]
    if resto:
        rows = []                                   # una tanda de filas por tipo de nodo
        for t in range(len(TIPOS) + 1):
            g = sorted([o for o in resto if _tipo(o) == t], key=lambda o: (o.OPType, o.name))
            rows += [g[k:k + 6] for k in range(0, len(g), 6)]
        x1, y1 = _filas(rows, 0, y, GRIS, hecho)
        _caja(scene, '4 OTROS', 0, y, x1, y1, GRIS)
    return len(hecho)
