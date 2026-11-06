"""
layout_core.py — builder corto para LAYOUTS CCTV (layout_* dentro de escena_modular).
Complementa a tdvj_core.py (visuales / efectos) con el mismo contrato y las mismas piezas:
  - Página Layout: 5 sliders en orden de rol + extras + colores + Bypass.
  - Página Audio: idéntica a la de las bases (Audioreact · Low/Mid/High · Audiotarget · Audiomult · Smooth · Audiochop · Energy).
  - Graf: cam_in_1..5 (Select TOP → CAM_1..5 de escena_modular) → GLSL → bypass → out1.

Un builder de layout es un CONFIG corto + una llamada (ver builders/layouts/setup_layout_*.py):

    import sys, importlib
    sys.path.insert(0, project.folder + '/_lib')
    import tdvj_core, layout_core
    importlib.reload(tdvj_core); importlib.reload(layout_core)
    layout_core.build_layout(**CONFIG)

Reglas que respeta (heredadas del skill td-vj-builder):
  - Cámaras = sTD2DInputs[0..4], nunca `uniform sampler2D`. Mínimo 2 cámaras.
  - Resolución SIEMPRE de escena_modular (ResW / ResH), nunca hardcodeada.
  - Todo uniform que el shader declare se asigna en la página Vectors (check_uniforms avisa si no).
  - Idempotente: el COMP layout_* y su out1 persisten (no se rompen cables hacia el switch de base17);
    los nodos internos llevan el tag 'tdvj' y se rehacen; los sliders conservan valor y export MIDI.
  - Al terminar se registra solo (escena_registro.py): queda en el menú Modoescena (al final si
    es nuevo) y conectado a su entrada de blend_switch, que crece con Numinputs.

Lo propio del show (ruta de escena_modular, audio) viene de _lib/rig.py vía tdvj_core.
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass  # fuera de TD: solo lectura / lint

import importlib
import tdvj_core as core
import escena_registro as registro
import camaras
import paleta
importlib.reload(registro)
importlib.reload(camaras)
importlib.reload(paleta)

CAMCOUNT_CANDS = ('Camerasenmulticam', 'Camarasenmulticam', 'Camerarasenmulticam', 'Camcount')
RESW_CANDS = ('Resw', 'ResW')
RESH_CANDS = ('Resh', 'ResH')


def _scene():
    s = op(core.ESCENA)
    if s is None:
        raise ValueError('No existe %s — ajusta ESCENA en _lib/rig.py' % core.ESCENA)
    return s


def _find_par(comp, cands, label_hints=()):
    """Parámetro por nombre; si no, por etiqueta (los nombres cambian entre versiones del patch)."""
    for n in cands:
        p = getattr(comp.par, n, None)
        if p is not None:
            return p
    for p in comp.customPars:
        lab = (p.label or '').lower().replace(' ', '')
        if any(h in lab for h in label_hints):
            return p
    return None


def _reloj(comp, slot_vel):
    """Reloj acumulado del layout (uPhase): un Speed CHOP suma la velocidad del slot 2 (con su audio)
    cuadro por cuadro. Los shaders usan uPhase en vez de uTime * velocidad: asi un cambio de velocidad
    (knob, slider o audio) acelera o frena el movimiento, nunca lo hace brincar."""
    name, _uni, mn, mx, _d = slot_vel
    vel = core._new(comp, constantCHOP, 'tdvj_vel', -500, 450)
    vel.par.name0 = 'vel'
    vel.par.value0.expr = core._slot_expr(comp, name, mn, mx) or '1'
    fase = core._new(comp, speedCHOP, 'tdvj_fase', -350, 450)
    fase.inputConnectors[0].connect(vel)
    return fase


def _glsl_multi(comp, name, pixel_dat, x, y, res):
    """Como tdvj_core._glsl pero GLSL Multi TOP: el GLSL TOP solo acepta 3 entradas y los
    layouts leen 5 camaras (sTD2DInputs[0..4]). Mismos parametros y pagina Vectors."""
    g = core._new(comp, glslmultiTOP, name, x, y)
    g.par.pixeldat = pixel_dat.name
    core._set(g, 'format', 'rgba16float')
    core._set(g, 'outputresolution', 'custom')
    core._set_expr(g, 'resolutionw', res[0])
    core._set_expr(g, 'resolutionh', res[1])
    info = core._new(comp, infoDAT, name + '_info', x, y - 150)
    core._set(info, 'op', g.name)
    return g


def _contract(comp, page_name, five_slots, extras, colors, audio_target):
    """Misma forma que tdvj_core.build_contract pero sin la página Salida: la resolución
    de un layout la manda escena_modular."""
    if len(five_slots) != 5:
        raise ValueError('five_slots debe tener exactamente 5 entradas (tiene %d)' % len(five_slots))
    names = [s[0] for s in five_slots]
    if audio_target is not None and audio_target not in names:
        raise ValueError('audio_target %r no es uno de los 5 slots %s' % (audio_target, names))

    pg = core._page(comp, page_name)
    keep = []
    for i, (name, _uni, mn, mx, dflt) in enumerate(five_slots):
        core._float(pg, name, '%d %s' % (i + 1, name), mn, mx, dflt)
        keep.append(name)
    for (name, _uni, mn, mx, dflt) in extras:
        core._float(pg, name, name, mn, mx, dflt)
        keep.append(name)
    for (name, _uni, rgb) in colors:
        core._rgb(pg, name, name, rgb)
        keep.append(name)
    core._toggle(pg, 'Bypass', 'Bypass', False)
    keep.append('Bypass')
    core._prune_and_sort(pg, keep)

    ap = core._page(comp, 'Audio')
    core._toggle(ap, 'Audioreact', 'Audio React', True)
    core._toggle(ap, 'Low', 'Low', True)
    core._toggle(ap, 'Mid', 'Mid', False)
    core._toggle(ap, 'High', 'High', False)
    core._menu(ap, 'Audiotarget', 'Audio Target', names,
               ['%d %s' % (i + 1, n) for i, n in enumerate(names)], audio_target or names[0])
    core._float(ap, 'Audiomult', 'Audio Mult', 0.0, 3.0, 1.0)
    core._float(ap, 'Smooth', 'Smooth (s)', 0.0, 1.0, 0.12)
    core._opref(ap, 'Audiochop', 'Audio CHOP', core.AUDIO_SOURCE, style='CHOP')
    energy = core._float(ap, 'Energy', 'Energy (lectura)', 0.0, 3.0, 0.0)
    energy.clampMax = False
    energy.expr = ('({l} * me.par.Low + {m} * me.par.Mid + {h} * me.par.High)'
                   ' * me.par.Audiomult * me.par.Audioreact').format(
        l=core._band_expr('low'), m=core._band_expr('mid'), h=core._band_expr('high'))
    energy.readOnly = True
    core._prune_and_sort(ap, ['Audioreact', 'Low', 'Mid', 'High', 'Audiotarget', 'Audiomult',
                              'Smooth', 'Audiochop', 'Energy'])


def build_layout(name, shader, five_slots, extras=(), colors=(), hero=False, num_cams=5,
                 audio_target=None, page='Layout', sources=None):
    """Layout CCTV: cam_in_1..N → GLSL (sTD2DInputs[0..N-1]) → bypass(cam 1) → out1.

    name:         layout_<algo> (Base COMP dentro de escena_modular; se crea si falta).
    shader:       ruta relativa a project.folder (p. ej. 'shaders/layouts/layout_rs_luna.frag').
    five_slots:   [(Par, uniform, min, max, default) ×5] en orden de rol:
                  1 intensidad · 2 velocidad · 3 distorsión · 4 color · 5 firma.
    extras:       [(Par, uniform, min, max, default)] — sliders extra (no empujados por el audio).
    colors:       [(Par, uniform, (r, g, b))] — selectores de color (vec3).
    hero:         True = el shader declara uHeroIndex. Siempre 0: el hero es la cámara del Lugar 1
                  (página Slots de escena_modular); para cambiar de hero se cambia ese lugar.
    audio_target: slot que empuja el audio por default (por nombre); None = el slot 1.
    sources:      None = SLOT_1..N (los 5 lugares) · o lista de TOPs de escena_modular
                  (p. ej. ['SLOT_UNICA'] para el layout de una sola cámara; num_cams = len(sources)).
                  Si todas las fuentes son la misma, el layout es de la familia SINGLE CAM; si no, MULTIVIEW
                  (tag tdvj_fam_*; ordena el menú y las páginas del Stream Deck).
    Nombres: layout_mv_<nombre> (multiview) · layout_sc_<nombre> (single cam).
    Uniforms base: uTime · uResolution (escena_modular ResW/ResH) · uCamCount (cámaras en multicam)
                   · uCamfit (escena_modular Camfit) · uCamAspect (16/9) · [uHeroIndex].
    """
    scene = _scene()
    comp = scene.op(name)
    if comp is None:
        comp = scene.create(baseCOMP, name)
        n_rs = len([c for c in scene.children if c.name.startswith('layout_rs_')])
        comp.nodeX, comp.nodeY = 0, -700 - 160 * max(n_rs - 1, 0)
    elif comp.OPType != 'baseCOMP':
        raise ValueError('%s existe pero no es un Base COMP (%s)' % (comp.path, comp.OPType))

    # paleta del álbum (estándar del show): Color1..5 en todos los layouts, repuestos en cada build
    colors = paleta.con_album(colors)
    _contract(comp, page, five_slots, extras, colors, audio_target)
    for (pname, _uni, rgb) in colors:
        p = getattr(comp.par, pname + 'r', None)
        if p is not None and paleta.es_del_album(rgb):
            for sub, v in zip(p.tuplet, rgb):
                if sub.mode == type(sub.mode).CONSTANT:
                    sub.val = v
    core.clear_managed(comp)

    # cámaras: Select TOP por CAM_n de escena_modular
    # El shader lee sTD2DInputs[0..num_cams-1] y TD dimensiona el arreglo con las entradas que
    # funcionan: si falta una cámara se repite otra que sí existe, si no el shader no compila.
    # cam_in_N lee SLOT_N (camaras.py: Slot1..5 eligen entre CAM_1..CAM_6); sin slot, CAM_N directo
    slots = camaras.ensure(scene)
    if sources:
        num_cams = len(sources)
        cams = [scene.op(n) for n in sources]
    else:
        cams = [(slots[i] if i < len(slots) else None) or scene.op('CAM_%d' % (i + 1)) for i in range(num_cams)]
    ok_cams = [c for c in cams if c is not None and not c.errors()]
    if not ok_cams:
        core.warn('ninguna CAM_1..%d sin error en %s — el layout queda sin cámaras' % (num_cams, scene.path))
    sels = []
    for i in range(num_cams):
        cam = cams[i]
        s = core._new(comp, selectTOP, 'cam_in_%d' % (i + 1), -500, -130 * i)
        if cam is None or cam.errors():
            sub = ok_cams[i % len(ok_cams)] if ok_cams else None
            core.warn('CAM_%d %s en %s — cam_in_%d usa %s' % (
                i + 1, 'no existe' if cam is None else 'con error', scene.path, i + 1,
                sub.name if sub is not None else 'nada'))
            cam = sub
        if cam is not None:
            s.par.top = cam.path
        sels.append(s)

    core._audio_in(comp, -500, 300)
    pix, abspath = core._shader_dat(comp, 'shader_frag', shader, -200, 200)

    # resolución de escena_modular (nunca hardcodeada); si faltan los parámetros, DEFAULT_RES
    rw = _find_par(scene, RESW_CANDS, ('resw',))
    rh = _find_par(scene, RESH_CANDS, ('resh',))
    if rw is None or rh is None:
        # en este rig la pestaña Resolucion trae ancho y alto con otro nombre (W / H): los dos primeros
        pg = next((g for g in scene.customPages if g.name.lower().startswith('resol')), None)
        nums = [p for p in pg.pars if p.isNumber] if pg is not None else []
        if len(nums) >= 2:
            rw, rh = nums[0], nums[1]
    rw_expr = "op('%s').par.%s" % (scene.path, rw.name) if rw is not None else str(core.DEFAULT_RES[0])
    rh_expr = "op('%s').par.%s" % (scene.path, rh.name) if rh is not None else str(core.DEFAULT_RES[1])
    if rw is None or rh is None:
        core.warn('escena_modular sin ResW/ResH — uso %s×%s; crea los parámetros o ajusta DEFAULT_RES' % core.DEFAULT_RES)

    g = _glsl_multi(comp, 'glsl_layout', pix, 0, -300, (rw_expr, rh_expr))
    for i, s in enumerate(sels):
        try:
            if i < len(g.inputConnectors):
                g.inputConnectors[i].connect(s)
            else:                               # el conector libre aparece al conectar el anterior
                s.outputConnectors[0].connect(g)
        except Exception as e:
            core.warn('input %d del GLSL: %s' % (i, e))
    if len(g.inputs) < num_cams:
        core.warn('glsl_layout tiene %d entradas y el shader espera %d' % (len(g.inputs), num_cams))

    # Bypass: enseña la cámara 1 limpia
    sw = core._new(comp, switchTOP, 'bypass', 200, -300)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(sels[0])
    sw.par.index.expr = 'int(parent().par.Bypass)'
    core._ensure_out(comp, 400, -300).inputConnectors[0].connect(sw)

    # uniforms
    cc = _find_par(scene, CAMCOUNT_CANDS, ('multicam',))
    camfit = _find_par(scene, ('Camfit',), ('camfit',))
    specs = [('uTime', ['absTime.seconds']),
             ('uResolution', [rw_expr, rh_expr]),
             ('uCamCount', ["op('%s').par.%s" % (scene.path, cc.name) if cc is not None else str(num_cams)]),
             ('uCamfit', ["op('%s').par.%s" % (scene.path, camfit.name) if camfit is not None else '0']),
             ('uCamAspect', ['16.0/9.0'])]
    if cc is None:
        core.warn('no encuentro el parámetro de cámaras en multicam en %s — uCamCount fijo en %d' % (scene.path, num_cams))
    if hero:
        specs.append(('uHeroIndex', ['0']))     # hero = Lugar 1 (Slots)
    if 'uPhase' in core._declared(abspath):
        specs.append(('uPhase', ["op('tdvj_fase')[0]"]))
        _reloj(comp, five_slots[1])
    specs += core._slot_specs(comp, five_slots, extras, colors)
    core.check_uniforms(abspath, core._bind_vectors(g, specs))

    # familia: single cam si todas sus entradas son la misma fuente (SLOT_UNICA); si no, multiview
    familia = 'singlecam' if sources and len(set(sources)) == 1 else 'multiview'
    for t in list(comp.tags):
        if t.startswith('tdvj_fam_'):
            comp.tags.remove(t)
    comp.tags.add('tdvj_fam_' + familia)
    core.log('%s listo (%d cámaras · %s) ← %s' % (comp.path, num_cams, familia, shader))
    registro.registrar(name)
    return comp
