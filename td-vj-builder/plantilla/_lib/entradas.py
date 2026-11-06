"""
entradas.py — las fuentes de cada camara de escena_modular, ordenadas y con UN control.

Cada camara N (1..6) queda igual:

    camN_solido (Constant, color del album) ─┐
    camN_stock  (Movie File In)            ──┼─> CAM_N (Switch: 0 solido · 1 stock · 2 en vivo) ─> SLOT_x
    camN_vivo   (Video Device In)          ──┘

Pestana Camaras de escena_modular:
  - Fuente          (Solidos / Stock / En vivo)  -> todas las camaras a la vez.
  - Fuente 1..6     (Global / Solido / Stock / En vivo) -> una camara distinta a las demas.
  - Vivo prendido   -> deja abiertas las capturadoras aunque no se usen (prenderlo ANTES del show
                       para que el cambio a En vivo sea inmediato). Apagado: cada capturadora se abre
                       solo cuando su camara esta en En vivo.

Los layouts no cambian: siguen leyendo SLOT_N (camaras.py), y SLOT_N lee CAM_N.

    entradas.ensure(scene, legado=True)   (idempotente)
      legado=True: renombra las fuentes viejas (constantN, videodevinN, <archivo>_fps) a camN_*,
      y manda a /project2/_respaldo/escena_modular_entradas lo que ya no se usa.
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass

import paleta

N_CAMS = 6
TAG = 'tdvj_entrada'
MODOS = ['solido', 'stock', 'vivo']
MODOS_LBL = ['Solidos', 'Stock', 'En vivo']
RESPALDO = '/project2/_respaldo'
SOBRAN = ('select', 'select4', 'select6', 'select7', 'select8', 'switch4', 'base1')

# geometria de la zona (filas = camaras)
X_SOLIDO, X_STOCK, X_VIVO, X_CAM, X_SLOT = -2050, -1800, -1550, -1250, -1000
Y0, DY = 1000, -230
VERDE = (0.13, 0.70, 0.35)


def _color(i):
    """cam 1..5 = amarillo, verde, azul, negro, rojo del album · cam 6 = crema."""
    return paleta.ALBUM[i - 1] if i <= 5 else paleta.CREMA


def _modo_expr(i):
    return ("(parent().par.Fuente{i}.eval() if parent().par.Fuente{i}.eval() != 'global' "
            "else parent().par.Fuente.eval())").format(i=i)


def _pars(scene):
    pg = next((p for p in scene.customPages if p.name == 'Camaras'), None) or scene.appendCustomPage('Camaras')
    if not hasattr(scene.par, 'Fuente'):
        p = pg.appendMenu('Fuente', label='Fuente (todas)')[0]
        p.menuNames, p.menuLabels = MODOS, MODOS_LBL
        p.val = 'stock'
    for i in range(1, N_CAMS + 1):
        if not hasattr(scene.par, 'Fuente%d' % i):
            p = pg.appendMenu('Fuente%d' % i, label='Fuente Cam %d' % i)[0]
            p.menuNames, p.menuLabels = ['global'] + MODOS, ['Global'] + MODOS_LBL
            p.val = 'global'
    if not hasattr(scene.par, 'Vivoprendido'):
        pg.appendToggle('Vivoprendido', label='Vivo prendido')
        scene.par.Vivoprendido = False


def _a_respaldo(scene, ops):
    ops = [o for o in ops if o is not None]
    if not ops:
        return []
    r = op(RESPALDO) or op('/project2').create(baseCOMP, '_respaldo')
    dest = r.op('escena_modular_entradas') or r.create(baseCOMP, 'escena_modular_entradas')
    dest.copyOPs(ops)
    nombres = [o.name for o in ops]
    for o in ops:
        o.destroy()
    return nombres


def _legado(scene):
    """Renombra las fuentes viejas segun a que CAM_N entran, y respalda lo que sobra."""
    log = []
    # CAM_2 viejo no tenia Movie File In propio: switch4 -> select -> /project2/base17/moviefilein1
    src = op('/project2/base17/moviefilein1')
    stock_cam2 = src.par.file.eval() if src is not None else None
    for i in range(1, N_CAMS + 1):
        cam = scene.op('CAM_%d' % i)
        if cam is None:
            continue
        for o in list(cam.inputs):
            if o.parent() != scene or o.name.startswith('cam%d_' % i):
                continue
            t = o.OPType
            new = {'constantTOP': 'cam%d_solido', 'moviefileinTOP': 'cam%d_stock',
                   'videodeviceinTOP': 'cam%d_vivo'}.get(t)
            if new and scene.op(new % i) is None:
                log.append('%s -> %s' % (o.name, new % i))
                o.name = new % i
    fuera = _a_respaldo(scene, [scene.op(n) for n in SOBRAN])
    if fuera:
        log.append('a %s/escena_modular_entradas: %s' % (RESPALDO, ', '.join(fuera)))
    return log, stock_cam2


def _fuente(scene, i, kind, tipo, stock_file=None):
    name = 'cam%d_%s' % (i, kind)
    o = scene.op(name)
    if o is None:
        o = scene.create(tipo, name)
    if kind == 'stock' and stock_file and 'samplesFolder' in (o.par.file.expr or ''):   # nuevo (default Banana)
        o.par.file.expr = ''
        o.par.file.mode = type(o.par.file.mode).CONSTANT
        o.par.file = stock_file
    o.tags.add(TAG)
    if kind == 'solido':
        c = _color(i)
        o.par.colorr, o.par.colorg, o.par.colorb = c
        o.par.alpha = 1.0
        o.par.outputresolution = 'custom'
        o.par.resolutionw.expr = 'parent().par.W'
        o.par.resolutionh.expr = 'parent().par.H'
    if kind == 'vivo':
        o.par.active.expr = 'parent().par.Vivoprendido or %s == %r' % (_modo_expr(i), 'vivo')
    return o


def _cc(scene, i, src):
    """CAM_N = correccion de color de lo que muestra la camara (solido, video o en vivo). Controles en show."""
    d = scene.op('cam_cc_frag') or scene.create(textDAT, 'cam_cc_frag')
    d.text = open(project.folder + '/shaders/master/correccion_camara.frag', encoding='utf-8').read()
    g = scene.op('CAM_%d' % i) or scene.create(glslTOP)
    g.name = 'CAM_%d' % i
    g.par.pixeldat = d
    g.par.outputresolution = 'useinput'
    g.tags.add(TAG)
    for k, (u, n) in enumerate((('uBrillo', 'Brillo'), ('uContraste', 'Contraste'), ('uNegros', 'Negros'),
                                ('uSaturacion', 'Saturacion'), ('uBypass', 'Colorbypass'))):
        getattr(g.par, 'uniname%d' % k).val = u
        getattr(g.par, 'value%dx' % k).expr = "float(op('/project2/show').par.%s)" % n
    g.inputConnectors[0].connect(src)
    return g


def ensure(scene, legado=True):
    log, stock2 = _legado(scene) if legado else ([], None)
    _pars(scene)
    for i in range(1, N_CAMS + 1):
        y = Y0 + (i - 1) * DY
        fuentes = [_fuente(scene, i, 'solido', constantTOP),
                   _fuente(scene, i, 'stock', moviefileinTOP, stock2 if i == 2 else None),
                   _fuente(scene, i, 'vivo', videodeviceinTOP)]
        viejo = scene.op('cam%d_cc' % i)
        if viejo is not None:
            viejo.destroy()
        cam = scene.op('cam%d_fuente' % i)
        if cam is None:
            cam = scene.op('CAM_%d' % i) if scene.op('CAM_%d' % i) is not None and scene.op('CAM_%d' % i).OPType == 'switchTOP' else scene.create(switchTOP)
            cam.name = 'cam%d_fuente' % i
        for c in reversed(list(cam.inputConnectors)):
            c.disconnect()
        for k, f in enumerate(fuentes):
            cam.inputConnectors[k].connect(f)
        cam.par.blend = False
        cam.par.index.expr = '%r.index(%s)' % (MODOS, _modo_expr(i))
        cam.tags.add(TAG)
        _cc(scene, i, cam)
        for o, x in zip(fuentes + [cam], (X_SOLIDO, X_STOCK, X_VIVO, X_CAM)):
            o.nodeX, o.nodeY = x, y
            o.color = VERDE
        cam.comment = 'Cam %d: 0 solido · 1 stock · 2 en vivo (pestana Camaras -> Fuente)' % i
    for i in range(1, 6):
        s = scene.op('SLOT_%d' % i)
        if s is not None:
            s.nodeX, s.nodeY = X_SLOT, Y0 + (i - 1) * DY
    su = scene.op('SLOT_UNICA')
    if su is not None:
        su.nodeX, su.nodeY = X_SLOT, Y0 + 5 * DY
    _recuadro(scene)
    return log


def _recuadro(scene):
    a = scene.op('zona_entradas') or scene.create(annotateCOMP, 'zona_entradas')
    x0, x1 = X_SOLIDO - 80, X_SLOT + 220
    y1, y0 = Y0 + 200, Y0 + (N_CAMS - 1) * DY - 120
    a.nodeX, a.nodeY = x0, y0
    a.nodeWidth, a.nodeHeight = x1 - x0, y1 - y0
    for pn, v in (('Titletext', 'ENTRADAS  ·  solido · stock · en vivo  ->  CAM_N  ->  SLOT_N   (pestana Camaras -> Fuente)'),
                  ('Bodytext', '')):
        if hasattr(a.par, pn):
            setattr(a.par, pn, v)
    for k, c in enumerate('rgb'):
        p = getattr(a.par, 'Backcolor' + c, None)
        if p is not None:
            p.val = VERDE[k] * 0.35
    if hasattr(a.par, 'Backcoloralpha'):
        a.par.Backcoloralpha = 0.25
