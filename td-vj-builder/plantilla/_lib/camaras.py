"""
camaras.py — 6 camaras, 5 lugares: que camara entra en cada lugar de los layouts.

En escena_modular:
  - CAM_1..CAM_6: las camaras (Switch TOPs). Si falta CAM_6 se crea con la misma forma que las
    demas: negro (entrada 0) o capturadora `videodevin6` (entrada 1). El dispositivo se elige en TD.
  - Pagina "Slots": Slot1..Slot5, menu CAM_1..CAM_6 (por default Slot N = CAM_N).
  - SLOT_1..SLOT_5: Select TOPs que siguen a cada Slot. Los layouts leen de aqui (cam_in_N -> SLOT_N),
    asi que cambiar un Slot cambia esa camara en TODOS los layouts al mismo tiempo, sin reconstruir.

  - Rotar camaras + Cambiar cada (s) (pestana Slots): con Rotar prendido, cada X segundos todos los
    lugares avanzan a la siguiente camara (entra tambien la Cam 6); al apagarlo regresan a la suya.
  - Camara unica: Menu2 (CAM_1..CAM_6) y SLOT_UNICA, para el layout de una sola camara a pantalla completa.

    camaras.ensure(scene)  -> [SLOT_1..SLOT_5]   (idempotente)
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass

import tdvj_core as core

N_CAMS = 6
N_SLOTS = 5
TAG = 'tdvj_cam'


def _cam6(scene):
    if scene.op('CAM_6') is not None:
        return
    ref = scene.op('CAM_5')
    x, y = (ref.nodeX, ref.nodeY - 250) if ref is not None else (0, 0)
    black = scene.create(constantTOP, 'cam6_negro')
    black.par.colorr = black.par.colorg = black.par.colorb = 0.0
    black.par.alpha = 1.0
    black.par.outputresolution = 'custom'
    black.par.resolutionw, black.par.resolutionh = core.DEFAULT_RES
    dev = scene.create(videodeviceinTOP, 'videodevin6')
    sw = scene.create(switchTOP, 'CAM_6')
    sw.inputConnectors[0].connect(black)
    sw.inputConnectors[1].connect(dev)
    sw.par.index = 1
    for o, dx, dy in ((black, -300, 60), (dev, -300, -60), (sw, 0, 0)):
        o.tags.add(TAG)
        o.nodeX, o.nodeY = x + dx, y + dy
    core.warn('CAM_6 creada: elige el dispositivo en %s/videodevin6' % scene.path)


def _slots_page(scene):
    return next((pg for pg in scene.customPages if pg.name == 'Slots'), None) or scene.appendCustomPage('Slots')


def ensure(scene):
    _cam6(scene)
    names = ['CAM_%d' % i for i in range(1, N_CAMS + 1) if scene.op('CAM_%d' % i) is not None]
    labels = [n.replace('CAM_', 'Cam ') for n in names]
    pg = _slots_page(scene)
    cuenta = _rotacion(scene, pg)
    slots = []
    for i in range(1, N_SLOTS + 1):
        p = getattr(scene.par, 'Slot%d' % i, None)
        new = p is None
        if new:
            p = pg.appendMenu('Slot%d' % i, label='Lugar %d' % i)[0]
        p.label = 'Lugar %d' % i
        p.menuNames = names
        p.menuLabels = labels
        if names and (new or p.eval() not in names):
            p.val = names[(i - 1) % len(names)]
        s = scene.op('SLOT_%d' % i)
        if s is None:
            s = scene.create(selectTOP, 'SLOT_%d' % i)
            s.tags.add(TAG)
            cam = scene.op('CAM_%d' % i)
            if cam is not None:
                s.nodeX, s.nodeY = cam.nodeX + 200, cam.nodeY
        # el lugar avanza tantas camaras como cambios lleve la rotacion (0 con Rotar apagado)
        s.par.top.expr = ("parent().par.Slot{i}.menuNames[(parent().par.Slot{i}.menuIndex + int(op('{c}')[0]))"
                          " % len(parent().par.Slot{i}.menuNames)]").format(i=i, c=cuenta.name)
        slots.append(s)
    try:
        pg.sort('Rotar', 'Rotarmodo', 'Rotarcada', 'Rotarsens', *['Slot%d' % i for i in range(1, N_SLOTS + 1)])
    except Exception:
        pass
    _unica(scene, names, labels)
    return slots


def _node(scene, optype, name, x, y):
    o = scene.op(name)
    if o is None:
        o = scene.create(optype, name)
        o.tags.add(TAG)
        o.nodeX, o.nodeY = x, y
    return o


def _float(pg, name, label, mn, mx, default):
    p = getattr(pg.owner.par, name, None)
    if p is None:
        p = pg.appendFloat(name, label=label)[0]
        p.val = default
    p.label = label
    p.min, p.max, p.normMin, p.normMax = mn, mx, mn, mx
    p.clampMin = p.clampMax = True
    p.default = default
    return p


def _rotacion(scene, pg):
    """Rotar camaras (on/off) y su modo:
         Por tiempo  -> un LFO cuadrado cambia cada 'Cambiar cada (s)'
         Con el audio -> cambia en cada golpe (kick o graves del CHOP de audio, por la sensibilidad)
    Un Count CHOP cuenta los cambios; con Rotar apagado la cuenta vuelve a 0 y cada lugar regresa a su camara."""
    if getattr(scene.par, 'Rotar', None) is None:
        pg.appendToggle('Rotar', label='Rotar camaras')[0].val = False
    scene.par.Rotar.label = 'Rotar camaras'
    m = getattr(scene.par, 'Rotarmodo', None)
    if m is None:
        m = pg.appendMenu('Rotarmodo', label='Rotar')[0]
    m.label = 'Rotar'
    m.menuNames = ['tiempo', 'audio']
    m.menuLabels = ['Por tiempo', 'Con el audio']
    _float(pg, 'Rotarcada', 'Cambiar cada (s)', 0.5, 30.0, 4.0)
    _float(pg, 'Rotarsens', 'Sensibilidad al audio', 0.5, 6.0, 1.5)

    ref = scene.op('SLOT_1')
    x, y = (ref.nodeX, ref.nodeY + 250) if ref is not None else (0, 0)
    lfo = scene.op('rotar_ritmo')
    if lfo is None:
        lfo = scene.create(lfoCHOP, 'rotar_ritmo')
        lfo.tags.add(TAG)
        lfo.nodeX, lfo.nodeY = x - 150, y
    shape = next((getattr(lfo.par, n) for n in ('wavetype', 'type') if hasattr(lfo.par, n)), None)
    if shape is not None:
        shape.val = 'square'                 # el nombre del parametro cambia entre versiones de TD
    else:
        core.warn('rotar_ritmo: no encontré la forma de onda del LFO; ponla en Square a mano')
    lfo.par.frequency.expr = '1.0 / max(parent().par.Rotarcada.eval(), 0.1)'

    # golpe de audio: kick (o graves) del CHOP de audio del show x sensibilidad
    src = op(core.AUDIO_SOURCE)
    fuente = _node(scene, switchCHOP, 'rotar_fuente', x, y)
    fuente.inputConnectors[0].connect(lfo)
    if src is not None:
        chans = [c.name for c in src.chans()]
        ch = next((c for c in ('kick', 'low') if c in chans), chans[0] if chans else '')
        sel = _node(scene, selectCHOP, 'rotar_audio', x - 300, y - 120)
        sel.par.chop = src.path
        sel.par.channames = ch
        gol = _node(scene, mathCHOP, 'rotar_golpe', x - 150, y - 120)
        gol.inputConnectors[0].connect(sel)
        if hasattr(gol.par, 'gain'):
            gol.par.gain.expr = 'parent().par.Rotarsens.eval()'
        fuente.inputConnectors[1].connect(gol)
        fuente.par.index.expr = "1 if parent().par.Rotarmodo.eval() == 'audio' else 0"
    else:
        core.warn('rotar: no existe el CHOP de audio %s (rig.py AUDIO_SOURCE) — solo funciona "Por tiempo"'
                  % core.AUDIO_SOURCE)
        fuente.par.index = 0

    cnt = _node(scene, countCHOP, 'rotar_cuenta', x + 150, y)
    cnt.inputConnectors[0].connect(fuente)
    if hasattr(cnt.par, 'threshold'):
        cnt.par.threshold = 0.5              # cuenta cada vez que la señal sube de 0.5
    else:
        core.warn('rotar_cuenta: sin parámetro Threshold en el Count CHOP; con audio ajusta la sensibilidad')
    if hasattr(cnt.par, 'reset'):
        cnt.par.reset.expr = 'not parent().par.Rotar.eval()'
    else:
        core.warn('rotar_cuenta: no encontré el parámetro Reset del Count CHOP; apágalo a mano')
    return cnt


def _unica(scene, names, labels):
    """Camara unica: Menu2 (pestana Camaras) elige 1 de las 6; SLOT_UNICA la sigue (layout_rs_camara_unica)."""
    p = getattr(scene.par, 'Menu2', None)
    if p is None or not names:
        return
    p.menuNames = names
    p.menuLabels = labels
    if p.eval() not in names:
        p.val = names[0]
    s = scene.op('SLOT_UNICA')
    if s is None:
        s = scene.create(selectTOP, 'SLOT_UNICA')
        s.tags.add(TAG)
        ref = scene.op('SLOT_%d' % N_SLOTS)
        if ref is not None:
            s.nodeX, s.nodeY = ref.nodeX, ref.nodeY - 200
    s.par.top.expr = 'parent().par.Menu2.eval()'
