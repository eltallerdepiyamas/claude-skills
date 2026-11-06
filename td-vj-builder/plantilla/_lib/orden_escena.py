"""
orden_escena.py — acomodo de escena_modular (mismo principio que /project2: bloques de ARRIBA a ABAJO,
una fila por cadena, recuadros del color del Stream Deck). SOLO mueve / pinta / recuadros.

  1 CONTROL   osc · companion · mix_feedback · demo_* · bs_escenas_* · scene_faders_* · prender_camaras
  2 ENTRADAS  una fila por camara: camN_solido · camN_stock · camN_vivo -> CAM_N -> SLOT_N (+ SLOT_UNICA, rotar_*)
  3 ESCENAS   cada layout en la fila de SU entrada de blend_switch (= orden del menu) -> blend_switch -> master_video
  4 OTROS     lo demas

  escenas(scene)  -> solo el bloque 3 (lo llama escena_registro.sincronizar: cada escena nueva se acomoda sola)
  acomodar(scene) -> todo (builders/herramientas/ordenar_escena.py)
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass
import re

DX, DY, GAP = 220, 150, 420
VERDE, AZUL, AMARILLO, TURQUESA, GRIS = (0.13, 0.70, 0.35), (0.18, 0.49, 0.88), (0.85, 0.64, 0.0), (0.08, 0.72, 0.72), (0.45, 0.45, 0.45)
CONTROL = ('osc', 'companion', 'mix_feedback', 'demo_', 'bs_escenas', 'scene_fader', 'prender_camaras', 'midi')


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
    """Bloque 3: layouts en columna, en el orden de las entradas de blend_switch, -> blend_switch -> master_video."""
    hecho = set() if hecho is None else hecho
    b, mo = scene.op('blend_switch'), scene.op('master_video')
    lays = _layouts_en_orden(scene)
    if not lays:
        return y
    if x is None or y is None:                     # solo escenas: se queda donde ya estaba el bloque
        ref = lays[0]
        x, y = ref.nodeX, max(l.nodeY for l in lays)
    for j, l in enumerate(lays):
        l.nodeX, l.nodeY = x, y - j * DY
        l.color = AMARILLO if 'tdvj_fam_singlecam' in l.tags else AZUL
        hecho.add(l.path)
    yc = y - (len(lays) - 1) * DY / 2.0
    for k, o in enumerate((b, mo)):
        if o is not None:
            o.nodeX, o.nodeY = x + (2 + 2 * k) * DX, int(yc)
            o.color = TURQUESA
            hecho.add(o.path)
    y1 = y - (len(lays) - 1) * DY
    if caja:
        _caja(scene, '3 ESCENAS  ·  cada layout en la fila de su entrada de blend_switch (orden del menu) -> blend_switch -> master_video',
              x, y, x + 4 * DX, y1, AZUL)
    return y1


def acomodar(scene):
    for a in [o for o in scene.children if o.OPType == 'annotateCOMP' and o.name.startswith('zona_')]:
        a.destroy()
    hecho, y = set(), 0
    # 1 CONTROL (por prefijo, una fila cada uno)
    grupos = {}
    for o in scene.children:
        for p in CONTROL:
            if o.name.startswith(p) and o.OPType != 'annotateCOMP':
                grupos.setdefault(p, []).append(o)
                break
    rows = [sorted(v, key=lambda o: o.name) for k, v in sorted(grupos.items())]
    x1, y1 = _filas(rows, 0, y, TURQUESA, hecho)
    _caja(scene, '1 CONTROL  ·  OSC / Companion · AJUSTES (mix_feedback) · DEMO / REC · Beatstep · faders', 0, y, x1, y1, TURQUESA)
    y = y1 - DY - GAP
    # 2 ENTRADAS
    # tres opciones separadas, cada una en su columna con recuadro; la camara N siempre en la fila N
    SEP = 520
    y1 = y
    for c, (k, titulo, rgb) in enumerate((('solido', '2A SOLIDOS', AMARILLO), ('stock', '2B VIDEOS  ·  Movie File In', AZUL),
                                          ('vivo', '2C EN VIVO  ·  Video Device In', VERDE))):
        x = c * SEP
        x1, y1 = _filas([[scene.op('cam%d_%s' % (i, k))] for i in range(1, 7)], x, y, rgb, hecho)
        _caja(scene, titulo, x, y, x1, y1, rgb)
    rows = [[scene.op('cam%d_fuente' % i), scene.op('CAM_%d' % i), scene.op('SLOT_%d' % i)] for i in range(1, 7)]
    rows[-1][-1] = scene.op('SLOT_UNICA')
    x0 = 3 * SEP
    x1, y1 = _filas(rows, x0, y, TURQUESA, hecho)
    _caja(scene, '2D camN_fuente (switch) -> CAM_N (correccion de color) -> SLOT_N', x0, y, x1, y1, TURQUESA)
    y = y1 - DY - GAP
    rot = [sorted([o for o in scene.children if o.name.startswith('rotar_')], key=lambda o: o.name)]
    x1, y1 = _filas(rot, 0, y, VERDE, hecho)
    _caja(scene, '2E ROTACION DE CAMARAS', 0, y, x1, y1, VERDE)
    y = y1 - DY - GAP
    # 3 ESCENAS
    y1 = escenas(scene, 0, y, hecho)
    y = y1 - DY - GAP
    # 4 OTROS
    resto = sorted([o for o in scene.children if o.path not in hecho and o.OPType != 'annotateCOMP' or o.name == 'annotate1'],
                   key=lambda o: (o.OPType, o.name))
    if resto:
        x1, y1 = _filas([resto[k:k + 6] for k in range(0, len(resto), 6)], 0, y, GRIS, hecho)
        _caja(scene, '4 OTROS', 0, y, x1, y1, GRIS)
    return len(hecho)
