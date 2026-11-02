"""
tdvj_core.py — núcleo compartido de los builders VJ (ON TOUR x MERCADO LIBRE).

Los setup_*.py lo importan desde un Text DAT dentro de TouchDesigner:

    import sys, importlib
    sys.path.insert(0, project.folder + '/_lib')
    import tdvj_core; importlib.reload(tdvj_core)

Reglas del rig (no negociables — el sampler MIDI depende de ellas):
  - Nunca renombrar / mover / destruir un baseX. Solo se gestionan sus hijos.
  - 5 sliders en orden de rol + Bypass aparte + página Audio en cada base.
  - Visuales base1–16 · Efectos base18–24 y base38–45 · Layouts layout_* en escena_modular.

Idempotencia:
  - Los parámetros custom se hacen "upsert": si ya existen se actualizan rango/label
    y se CONSERVA su valor y su modo (expresión / export MIDI). Solo se borran los
    parámetros de la página que ya no están en la config.
  - Los operadores internos llevan el tag 'tdvj' y se destruyen/rehacen en cada run.
    Lo que no tenga el tag (tus nodos, el Text DAT del builder) no se toca.
  - out1 es persistente para no romper los cables que salen del base.
"""
import os
import re

try:
    from td import *  # noqa: F401,F403  (op, project, glslTOP, selectTOP, ...)
except ImportError:
    pass  # fuera de TD: solo lectura / lint


# ─────────────────────────────────────────────────────────────── rutas del rig
ROOT          = '/project2'
ESCENA        = ROOT + '/base17/escena_modular'
CAMERA_SWITCH = ESCENA + '/switch1'
AUDIO_SOURCE  = '/project1/null4'          # canales: low mid high (+ otros)
WEBCAM        = ROOT + '/webcam_test'      # Video Device In compartido, solo para pruebas

VISUAL_BASES = list(range(1, 17))
EFFECT_BASES = list(range(18, 25)) + list(range(38, 46))

TAG = 'tdvj'
SLOT_ROLES = ('intensidad', 'velocidad', 'distorsión', 'color', 'firma')

_UNIFORM_RE = re.compile(r'^\s*uniform\s+(?:float|int|vec2|vec3|vec4)\s+(\w+)\s*;', re.M)


# ─────────────────────────────────────────────────────────────── utilidades
def log(msg):
    print('[tdvj] ' + msg)


def warn(msg):
    print('[WARN] ' + msg)


def find_base(name):
    for path in (ROOT + '/' + name, '/' + name):
        o = op(path)
        if o is not None:
            return o
    raise ValueError('No encuentro %s (probé %s/%s y /%s)' % (name, ROOT, name, name))


def check_range(name, allowed, kind):
    try:
        n = int(name.replace('base', ''))
    except ValueError:
        raise ValueError('%s no es un nombre baseXX válido' % name)
    if n not in allowed:
        raise ValueError('%s está fuera del rango de %s — el sampler MIDI depende de los rangos' % (name, kind))


def _set(o, parname, value):
    p = getattr(o.par, parname, None)
    if p is None:
        warn('%s no tiene el parámetro %s (versión de TD distinta?)' % (o.path, parname))
        return None
    try:
        p.val = value
    except Exception as e:
        warn('%s.par.%s = %r falló: %s' % (o.path, parname, value, e))
    return p


def _set_expr(o, parname, expr):
    p = getattr(o.par, parname, None)
    if p is None:
        warn('%s no tiene el parámetro %s' % (o.path, parname))
        return None
    p.expr = expr
    return p


def hub_expr(par, fallback):
    """Expresión que lee un parámetro del hub tracking_input (hermano del base) con fallback.
    Se evalúa en nodos DENTRO del base: parent(2) = el padre del base (/project2 o el pack)."""
    return ("(parent(2).op('tracking_input').par.{p} if parent(2).op('tracking_input') "
            "is not None else {f})").format(p=par, f=fallback)


def res_exprs(resolution=None):
    """Resolución: 'hub' = tracking_input (Resw/Resh, una sola para todas las bases) ·
    (w, h) fija · None = escena_modular Resw/Resh; fallback 1920x1080."""
    if resolution == 'hub':
        return [hub_expr('Resw', 1920), hub_expr('Resh', 1080)]
    if resolution is not None:
        return [str(int(resolution[0])), str(int(resolution[1]))]
    esc = op(ESCENA)
    out = []
    for axis, fallback in (('w', '1920'), ('h', '1080')):
        name = None
        if esc is not None:
            for cand in ('Res' + axis, 'Res' + axis.upper()):
                if getattr(esc.par, cand, None) is not None:
                    name = cand
                    break
        if name is None:
            warn('escena_modular no tiene Res%s — uso %s fijo' % (axis, fallback))
            out.append(fallback)
        else:
            out.append("op('%s').par.%s" % (ESCENA, name))
    return out


# ─────────────────────────────────────────────────────────────── custom pars
def _page(comp, name):
    for pg in comp.customPages:
        if pg.name == name:
            return pg
    return comp.appendCustomPage(name)


def _upsert(page, style, name, label):
    """Devuelve (primer Par del tuplet, creado?). Conserva el par si ya existe con el mismo estilo/página."""
    comp = page.owner
    probe = name + ('r' if style == 'RGB' else '')
    p = getattr(comp.par, probe, None)
    if p is not None and (p.style != style or p.page.name != page.name):
        p.destroy()
        p = None
    created = p is None
    if created:
        getattr(page, 'append' + style)(name, label=label)
        p = getattr(comp.par, probe)
    else:
        p.label = label
    return p, created


def _float(page, name, label, mn, mx, default):
    p, created = _upsert(page, 'Float', name, label)
    p.min, p.max = mn, mx
    p.normMin, p.normMax = mn, mx
    p.clampMin = p.clampMax = True
    p.default = default
    if created:
        p.val = default
    return p


def _toggle(page, name, label, default):
    p, created = _upsert(page, 'Toggle', name, label)
    p.default = default
    if created:
        p.val = default
    return p


def _menu(page, name, label, names, labels, default):
    p, created = _upsert(page, 'Menu', name, label)
    p.menuNames = names
    p.menuLabels = labels
    p.default = default
    if created or p.eval() not in names:
        p.val = default
    return p


def _int(page, name, label, mn, mx, default):
    p, created = _upsert(page, 'Int', name, label)
    p.min, p.max = mn, mx
    p.normMin, p.normMax = mn, mx
    p.clampMin = p.clampMax = True
    p.default = default
    if created:
        p.val = default
    return p


def _str(page, name, label, default):
    p, created = _upsert(page, 'Str', name, label)
    p.default = default
    if created:
        p.val = default
    return p


def _opref(page, name, label, default, style='CHOP'):
    """Parámetro de referencia a operador (CHOP/TOP/COMP): se puede arrastrar un nodo encima."""
    p, created = _upsert(page, style, name, label)
    p.default = default
    if created:
        p.val = default
    return p


def _pulse(page, name, label):
    p, _ = _upsert(page, 'Pulse', name, label)
    return p


def _rgb(page, name, label, rgb):
    p, created = _upsert(page, 'RGB', name, label)
    for sub, v in zip(p.tuplet, rgb):
        sub.default = v
        sub.normMin, sub.normMax = 0.0, 1.0
        if created:
            sub.val = v
    return p


def _prune_and_sort(page, keep):
    for p in list(page.pars):
        try:
            if p.valid and p.tupletName not in keep:
                p.destroy()
        except Exception:
            pass
    try:
        page.sort(*keep)
    except Exception:
        pass


def build_contract(comp, page_name, five_slots, extras=(), colors=(), audio=True):
    """Página principal (5 slots + extras + colores + Bypass) y página Audio (si audio=True).
    audio=False: el proyecto no tiene análisis de audio → se elimina la página Audio."""
    if len(five_slots) != 5:
        raise ValueError('FIVE_SLOTS debe tener exactamente 5 entradas (tiene %d)' % len(five_slots))

    pg = _page(comp, page_name)
    keep = []
    for i, (name, _uni, mn, mx, dflt) in enumerate(five_slots):
        _float(pg, name, '%d %s' % (i + 1, name), mn, mx, dflt)
        keep.append(name)
    for (name, _uni, mn, mx, dflt) in extras:
        _float(pg, name, name, mn, mx, dflt)
        keep.append(name)
    for (name, _uni, rgb) in colors:
        _rgb(pg, name, name, rgb)
        keep.append(name)
    _toggle(pg, 'Bypass', 'Bypass', False)
    keep.append('Bypass')
    _prune_and_sort(pg, keep)

    if not audio:
        for p in comp.customPages:
            if p.name == 'Audio':
                p.destroy()
        return

    ap = _page(comp, 'Audio')
    _toggle(ap, 'Audioreact', 'Audio React', False)
    _toggle(ap, 'Low', 'Low', True)
    _toggle(ap, 'Mid', 'Mid', False)
    _toggle(ap, 'High', 'High', False)
    slot_names = [s[0] for s in five_slots]
    _menu(ap, 'Audiotarget', 'Audio Target', slot_names,
          ['%d %s' % (i + 1, n) for i, n in enumerate(slot_names)], slot_names[0])
    _float(ap, 'Audiomult', 'Audio Mult', 0.0, 3.0, 1.0)
    energy = _float(ap, 'Energy', 'Energy (lectura)', 0.0, 3.0, 0.0)
    energy.clampMax = False
    energy.expr = (
        "(float(me.op('audio_in')['low'] or 0) * me.par.Low"
        " + float(me.op('audio_in')['mid'] or 0) * me.par.Mid"
        " + float(me.op('audio_in')['high'] or 0) * me.par.High)"
        " * me.par.Audiomult * me.par.Audioreact"
    )
    energy.readOnly = True
    _prune_and_sort(ap, ['Audioreact', 'Low', 'Mid', 'High', 'Audiotarget', 'Audiomult', 'Energy'])


# API pública para los ganchos `extra` de los builders (páginas y nodos propios del visual)
page, float_par, int_par, toggle_par, str_par, menu_par, rgb_par, prune_and_sort = (
    _page, _float, _int, _toggle, _str, _menu, _rgb, _prune_and_sort)
opref_par, pulse_par = _opref, _pulse


# ─────────────────────────────────────────────────────────────── operadores
def clear_managed(comp):
    # al destruir un nodo, TD destruye también sus DATs acoplados (docked):
    # por eso se revalida cada referencia antes de usarla
    for c in list(comp.children):
        if c.valid and TAG in c.tags:
            for d in list(c.docked):
                if d.valid:
                    d.destroy()
            if c.valid:
                c.destroy()


def _new(comp, optype, name, x, y):
    o = comp.create(optype, name)
    # GLSL TOP, Script CHOP, etc. crean DATs acoplados por defecto (pixel, info, callbacks);
    # los quitamos: el builder crea y enlaza los suyos
    for d in list(o.docked):
        if d.valid:
            d.destroy()
    if o.name != name:
        warn('%s ya existía (no gestionado); el nuevo se llama %s' % (name, o.name))
    o.tags.add(TAG)
    o.nodeX, o.nodeY = x, y
    return o


new_op = None  # se asigna abajo (alias público de _new)


def ensure_webcam():
    """Webcam de pruebas en /project2/webcam_test. Persistente y fuera de los baseX."""
    w = op(WEBCAM)
    if w is None:
        w = op(ROOT).create(videodeviceinTOP, WEBCAM.rsplit('/', 1)[1])
        w.nodeX, w.nodeY = -800, 600
        log('creada %s (Video Device In) — elige tu webcam en sus parámetros' % w.path)
    return w.path


def _ensure_out(comp, x, y):
    o = comp.op('out1')
    if o is None or o.OPType != 'outTOP':
        o = comp.create(outTOP, 'out1')
    o.nodeX, o.nodeY = x, y
    return o


new_op = _new


def _audio_in(comp, x, y):
    a = _new(comp, selectCHOP, 'audio_in', x, y)
    chop_par = getattr(a.par, 'chop', None) or getattr(a.par, 'chops', None)
    if chop_par is None:
        warn('Select CHOP sin parámetro chop/chops')
    else:
        chop_par.val = AUDIO_SOURCE
    _set(a, 'channames', 'low mid high')
    return a


def _shader_dat(comp, name, rel, x, y):
    rel = rel.replace('\\', '/')
    abspath = os.path.join(project.folder, rel)
    if not os.path.isfile(abspath):
        warn('no existe el shader %s' % abspath)
    d = _new(comp, textDAT, name, x, y)
    d.par.file.expr = "project.folder + '/%s'" % rel
    sync = getattr(d.par, 'syncfile', None)
    if sync is not None:
        sync.val = True
    elif os.path.isfile(abspath):
        with open(abspath, encoding='utf-8') as f:
            d.text = f.read()
    return d, abspath


def _glsl(comp, name, pixel_dat, x, y, custom_res=None):
    g = _new(comp, glslTOP, name, x, y)
    g.par.pixeldat = pixel_dat.name
    _set(g, 'format', 'rgba16float')
    if custom_res is None:
        _set(g, 'outputresolution', 'useinput')
    else:
        _set(g, 'outputresolution', 'custom')
        _set_expr(g, 'resolutionw', custom_res[0])
        _set_expr(g, 'resolutionh', custom_res[1])
    info = _new(comp, infoDAT, name + '_info', x, y - 150)
    _set(info, 'op', g.name)
    return g


def _slot_expr(comp, name, mn, mx, audio=True):
    """Expresión del uniform: slider + energía de audio (si este slot es el Audiotarget)."""
    if getattr(comp.par, name, None) is None:
        warn('parámetro %s no existe en %s — uniform sin enlazar' % (name, comp.path))
        return None
    if not audio:
        return 'parent().par.%s' % name
    return ("tdu.clamp(parent().par.{n} + (parent().par.Energy * {rng} "
            "if parent().par.Audiotarget.eval() == '{n}' else 0), {mn}, {mx})"
            ).format(n=name, rng=float(mx - mn), mn=float(mn), mx=float(mx))


def _bind_vectors(glsl, specs):
    """specs: [(uniform, [x, y, z, w])] — cada valor es expresión (str), número o None."""
    specs = [s for s in specs if s is not None]
    try:
        glsl.seq.vec.numBlocks = max(len(specs), 1)
    except Exception:
        pass  # TD antiguo: bloques fijos vec0..vecN
    for i, (uni, values) in enumerate(specs):
        pname = getattr(glsl.par, 'vec%dname' % i, None)
        if pname is None:
            warn('%s no tiene bloque vec%d para %s' % (glsl.path, i, uni))
            continue
        pname.val = uni
        for axis, v in zip('xyzw', values):
            if v is None:
                continue
            p = getattr(glsl.par, 'vec%dvalue%s' % (i, axis))
            if isinstance(v, str):
                p.expr = v
            else:
                p.val = v
    return [s[0] for s in specs]


def ensure_comp(parent_path, name, x=0, y=0):
    """COMP de herramienta (no baseX): se crea si falta y nunca se destruye."""
    parent = op(parent_path)
    c = parent.op(name)
    if c is None:
        c = parent.create(baseCOMP, name)
        c.nodeX, c.nodeY = x, y
        log('creado %s' % c.path)
    return c


def freeze_for_handoff(comp):
    """Deja un COMP autocontenido para exportar como .tox:
    - shaders/scripts incrustados (Text DAT sin Sync to File ni ruta),
    - toda expresión que apunte a escena_modular se congela a su valor actual."""
    for c in comp.findChildren(tags=[TAG]):
        if c.OPType == 'textDAT':
            text = c.text
            sync = getattr(c.par, 'syncfile', None)
            if sync is not None:
                sync.val = False
            c.par.file.expr = ''
            c.par.file.val = ''
            c.text = text
        for p in c.pars():
            if str(p.mode).upper().endswith('EXPRESSION') and 'escena_modular' in (p.expr or ''):
                v = p.eval()
                p.expr = ''
                p.val = v
    log('%s congelado para handoff' % comp.path)


shader_dat, glsl_top, bind_vectors = _shader_dat, _glsl, _bind_vectors


def check_uniforms(abspath, bound):
    """Shader y parámetros son un par sincronizado: avisa de cualquier desajuste."""
    try:
        with open(abspath, encoding='utf-8') as f:
            declared = set(_UNIFORM_RE.findall(f.read()))
    except OSError:
        return
    for u in sorted(declared - set(bound)):
        warn('uniform %s declarado en el shader pero SIN asignar (render negro/plano)' % u)
    for u in sorted(set(bound) - declared):
        log('nota: %s asignado pero no declarado en el shader' % u)


def _slot_specs(comp, five_slots, extras, colors, audio=True):
    specs = []
    for (name, uni, mn, mx, _d) in five_slots:
        e = _slot_expr(comp, name, mn, mx, audio=audio)
        specs.append((uni, [e]) if e else None)
    for (name, uni, mn, mx, _d) in extras:
        e = _slot_expr(comp, name, mn, mx, audio=False)
        specs.append((uni, [e]) if e else None)
    for (name, uni, _rgb) in colors:
        specs.append((uni, ['parent().par.%sr' % name, 'parent().par.%sg' % name,
                            'parent().par.%sb' % name]))
    return specs


# ─────────────────────────────────────────────────────────────── tracking (piso interactivo)
# Contrato de canales (webcam_tracker y Hokuyo): p{i}x p{i}y 0..1 · p{i}a 0/1 · p{i}id, i = 0..7
# En el shader: uniform vec4 u_p0..u_p7 (xy = posición, z = activa, w = id) + uniform vec2 u_floor_m.
MAX_PEOPLE = 8
# Todas las bases leen el HUB (setup_tracking_input.py) por ruta relativa al padre de la base:
# funciona igual en /project2 que dentro del paquete .tox de handoff.
HUB_NAME = 'tracking_input'
HUB_EXPR = "me.parent().op('%s/out1')" % HUB_NAME
_OLD_TRACKING_DEFAULT = ROOT + '/webcam_tracker/tracking'


def _chan(name, fallback):
    return ("(op('tracking_in')['{n}'].eval() if op('tracking_in') is not None "
            "and op('tracking_in')['{n}'] is not None else {f})").format(n=name, f=fallback)


def _person(i):
    """Caminantes sintéticos (Lissajous lentos, distintos por slot) si Simulate; si no, el CHOP."""
    sim = 'parent().par.Simulate'
    sx = '(0.5 + 0.38*math.sin(absTime.seconds*%.3f + %.2f))' % (0.13 + 0.037 * i, i * 1.9)
    sy = '(0.5 + 0.36*math.sin(absTime.seconds*%.3f + %.2f))' % (0.11 + 0.029 * i, i * 0.7 + 1.3)
    sa = '(1.0 if %d < parent().par.Simcount else 0.0)' % i
    ry = _chan('p%dy' % i, 0.0)                  # flip/swap/metros ya los resuelve el hub
    return ['%s if %s else %s' % (sx, sim, _chan('p%dx' % i, 0.0)),
            '%s if %s else %s' % (sy, sim, ry),
            '%s if %s else %s' % (sa, sim, _chan('p%da' % i, 0.0)),
            '%s if %s else %s' % (float(i), sim, _chan('p%did' % i, float(i)))]


def build_tracking(comp):
    """Página Tracking + select CHOP tracking_in. Devuelve los specs de u_floor_m y u_p0..u_p7."""
    pg = _page(comp, 'Tracking')
    _toggle(pg, 'Simulate', 'Simulate (local, ignora el hub)', False)
    _int(pg, 'Simcount', 'Sim Count', 0, MAX_PEOPLE, 3)
    tc, created = _upsert(pg, 'CHOP', 'Trackingchop', 'Tracking CHOP (hub)')
    cur = tc.eval()
    cur_path = getattr(cur, 'path', cur or '')
    old = str(tc.mode).upper().endswith('CONSTANT') and cur_path in ('', _OLD_TRACKING_DEFAULT)
    if created or old:
        tc.expr = HUB_EXPR                      # migra bases viejas: webcam directa → hub
        comp.par.Simulate = False
    # Floor W/H, flips y resolución viven en el hub (una sola vez para todas las bases)
    _prune_and_sort(pg, ['Simulate', 'Simcount', 'Trackingchop'])

    trk = _new(comp, selectCHOP, 'tracking_in', -400, -450)
    chop_par = getattr(trk.par, 'chop', None) or getattr(trk.par, 'chops', None)
    if chop_par is not None:
        chop_par.expr = 'parent().par.Trackingchop'

    specs = [('u_floor_m', [hub_expr('Floorw', 7.0), hub_expr('Floorh', 5.0)])]
    specs += [('u_p%d' % i, _person(i)) for i in range(MAX_PEOPLE)]
    return specs


# ─────────────────────────────────────────────────────────────── builders
def build_effect(base, shader, five_slots, signature_extras=(), color_uniforms=(),
                 feedback=False, page='Filter'):
    """Efecto de cámara: base17/switch1 → [feedback] → GLSL → bypass → out1."""
    check_range(base, EFFECT_BASES, 'efectos (18–24, 38–45)')
    comp = find_base(base)
    build_contract(comp, page, five_slots, signature_extras, color_uniforms)
    clear_managed(comp)

    _audio_in(comp, -400, -300)
    cam = _new(comp, selectTOP, 'cam_in', -400, 0)
    cam.par.top = CAMERA_SWITCH
    pix, abspath = _shader_dat(comp, 'shader_frag', shader, -200, 200)
    g = _glsl(comp, 'glsl1', pix, 0, 0)
    g.inputConnectors[0].connect(cam)

    if feedback:
        fb = _new(comp, feedbackTOP, 'feedback1', -200, -150)
        fb.inputConnectors[0].connect(cam)
        fb.par.top = g.name
        g.inputConnectors[1].connect(fb)

    specs = [('uTime', ['absTime.seconds']),
             ('uResolution', ['me.inputs[0].width if me.inputs else 1920',
                              'me.inputs[0].height if me.inputs else 1080'])]
    specs += _slot_specs(comp, five_slots, signature_extras, color_uniforms)
    check_uniforms(abspath, _bind_vectors(g, specs))

    sw = _new(comp, switchTOP, 'bypass', 200, 0)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(cam)
    sw.par.index.expr = 'int(parent().par.Bypass)'
    _ensure_out(comp, 400, 0).inputConnectors[0].connect(sw)
    log('%s listo (efecto%s) ← %s' % (comp.path, ' + feedback' if feedback else '', shader))
    return comp


FIGURES = [('original', 'Original (sin figura)'), ('opsphere', 'Esfera op-art'),
           ('ovalos', 'Arco de óvalos'), ('destello', 'Destello'), ('eclipse', 'Eclipse'),
           ('esferalila', 'Esfera lila')]
FIG_SHADER = 'shaders/herramientas/figuras.frag'


def _figure_page(comp):
    """Página Figura: figura del moodboard sobre cada persona (Original = la base tal cual)."""
    pg = _page(comp, 'Figura')
    _menu(pg, 'Figura', 'Figura por persona', [n for n, _ in FIGURES], [l for _, l in FIGURES], 'original')
    _float(pg, 'Figsize', 'Tamaño (m)', 0.15, 2.0, 0.6)
    _float(pg, 'Figmix', 'Opacidad', 0.0, 1.0, 1.0)
    _float(pg, 'Figspeed', 'Velocidad', 0.0, 3.0, 1.0)
    _toggle(pg, 'Hidemarker', 'Ocultar marcador original', True)
    _prune_and_sort(pg, ['Figura', 'Figsize', 'Figmix', 'Figspeed', 'Hidemarker'])


def _figure_layer(comp, res, track_specs):
    """GLSL 'figuras' justo antes de bypass (después de extra: respeta glsl_opaque de base9, etc.)."""
    sw = comp.op('bypass')
    src = sw.inputs[0] if sw.inputs else None
    pix, abspath = _shader_dat(comp, 'figuras_frag', FIG_SHADER, 100, -500)
    f = _glsl(comp, 'figuras', pix, 100, -300, custom_res=res)
    if src is not None:
        f.inputConnectors[0].connect(src)
    sw.inputConnectors[0].connect(f)
    specs = [('u_time', ['absTime.seconds']), ('u_res', res),
             ('u_fig', ['parent().par.Figura.menuIndex']),
             ('u_figsize', ['parent().par.Figsize']),
             ('u_figmix', ['parent().par.Figmix']),
             ('u_figspeed', ['parent().par.Figspeed'])] + list(track_specs)
    check_uniforms(abspath, _bind_vectors(f, specs))


def build_visual(base, shader, five_slots, signature_extras=(), color_uniforms=(),
                 source=None, resolution=None, tracking=False, audio=True, feedback=False,
                 extra=None, page='Visual', figures=None):
    """Visual generativo: [source] → GLSL → bypass(negro) → out1.

    source:     None = generativo puro · 'webcam' = /project2/webcam_test · o ruta de un TOP.
                Entra en sTD2DInputs[0] (el shader lo usa vía #define u_input).
    resolution: None = escena_modular Resw/Resh · (w, h) = fija (p.ej. la del piso LED).
    feedback:   True = la salida anterior del GLSL entra en sTD2DInputs[0] (o [1] si hay source):
                estelas / acumulación. Resetea con el pulso Resetfb de la página principal.
    audio:      False = sin audio_in ni página Audio (u_bass = 0; sliders sin empuje de audio).
    tracking:   True = página Tracking (Simulate / CHOP de webcam o Hokuyo) + u_floor_m, u_p0..u_p7.
    extra:      función extra(comp) → [(uniform, [x, y, z, w])] para páginas/nodos/uniforms
                propios del visual (tracking, etc.). Usa tdvj_core.page/float_par/new_op...
    figures:    True (default si tracking) = página Figura + capa 'figuras' antes de bypass: una
                figura del moodboard sobre cada persona. Si el shader declara u_hide_marker, el
                marcador original se oculta mientras haya figura (toggle Hidemarker).
    """
    if figures is None:
        figures = tracking
    check_range(base, VISUAL_BASES, 'visuales (1–16)')
    comp = find_base(base)
    build_contract(comp, page, five_slots, signature_extras, color_uniforms, audio=audio)
    if feedback:
        pulse_par(_page(comp, page), 'Resetfb', 'Reset estela')
    if figures:
        _figure_page(comp)
    clear_managed(comp)

    res = res_exprs(resolution)
    if audio:
        _audio_in(comp, -400, -300)
    pix, abspath = _shader_dat(comp, 'shader_frag', shader, -200, 200)
    g = _glsl(comp, 'glsl1', pix, 0, 0, custom_res=res)
    if source == 'webcam':
        source = ensure_webcam()
    if source:
        src = _new(comp, selectTOP, 'src_in', -400, 0)
        src.par.top = source
        g.inputConnectors[0].connect(src)

    # 1) grafo completo y conectado ANTES de cualquier paso que pueda fallar
    black = _new(comp, constantTOP, 'black', 0, -150)
    for pn, v in (('colorr', 0), ('colorg', 0), ('colorb', 0), ('alpha', 0)):
        _set(black, pn, v)
    _set(black, 'outputresolution', 'custom')
    _set_expr(black, 'resolutionw', res[0])
    _set_expr(black, 'resolutionh', res[1])

    if feedback:
        fb = _new(comp, feedbackTOP, 'feedback1', -200, -150)
        fb.inputConnectors[0].connect(black)           # fuente de reset: negro
        fb.par.top = g.name
        _set(fb, 'format', 'rgba16float')
        g.inputConnectors[1 if source else 0].connect(fb)
        if getattr(comp.par, 'Resetfb', None) is not None:
            rp = getattr(fb.par, 'resetpulse', None) or getattr(fb.par, 'reset', None)
            if rp is not None and rp.isPulse:
                pex = _new(comp, parameterexecuteDAT, 'on_resetfb', -200, -300)
                _set(pex, 'op', comp.path)
                _set(pex, 'pars', 'Resetfb')
                _set(pex, 'onpulse', True)
                _set(pex, 'valuechange', False)
                pex.text = ("def onPulse(par):\n"
                            "    op('feedback1').par.%s.pulse()\n"
                            "    return\n" % rp.name)

    sw = _new(comp, switchTOP, 'bypass', 200, 0)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(black)
    sw.par.index.expr = 'int(parent().par.Bypass)'
    _ensure_out(comp, 400, 0).inputConnectors[0].connect(sw)

    # 2) uniforms: si tracking/extra fallan se avisa y se sigue (la base queda conectada)
    specs = [('u_time', ['absTime.seconds']),
             ('u_res', res),
             ('u_bass', ["float(op('audio_in')['low'] or 0) * parent().par.Audiomult" if audio else 0.0])]
    specs += _slot_specs(comp, five_slots, signature_extras, color_uniforms, audio=audio)
    track_specs = []
    for label, fn in (('tracking', build_tracking if tracking else None), ('extra', extra)):
        if fn is None:
            continue
        try:
            got = fn(comp) or []
            specs += got
            if label == 'tracking':
                track_specs = got
        except Exception:
            import traceback
            traceback.print_exc()
            warn('%s: falló %s — la base queda conectada pero sin esos uniforms' % (comp.path, label))
    if figures and os.path.isfile(abspath):
        with open(abspath, encoding='utf-8') as fh:
            if 'u_hide_marker' in fh.read():
                specs.append(('u_hide_marker', ['float(parent().par.Figura.menuIndex > 0 '
                                                'and parent().par.Hidemarker)']))
    check_uniforms(abspath, _bind_vectors(g, specs))
    if figures:
        try:
            _figure_layer(comp, res, track_specs)
        except Exception:
            import traceback
            traceback.print_exc()
            warn('%s: falló la capa Figura — la base sigue funcionando sin ella' % comp.path)
    log('%s listo (visual%s) ← %s' % (comp.path, ' + input' if source else ' puro', shader))
    return comp


def build_layout(name, shader, cams, five_slots, signature_extras=(), color_uniforms=(),
                 page='Layout'):
    """Layout CCTV: CAM_n → GLSL multi-input (sTD2DInputs[0..]) → bypass(CAM 1) → out1.
    Crea layout_<name> en escena_modular si no existe. No toca switch1: el cableado es tuyo."""
    if not 2 <= len(cams) <= 5:
        raise ValueError('un layout usa entre 2 y 5 cámaras')
    esc = op(ESCENA)
    if esc is None:
        raise ValueError('No encuentro %s' % ESCENA)
    cname = name if name.startswith('layout_') else 'layout_' + name
    comp = esc.op(cname)
    if comp is None:
        comp = esc.create(baseCOMP, cname)
        log('creado %s' % comp.path)
    build_contract(comp, page, five_slots, signature_extras, color_uniforms)
    clear_managed(comp)

    res = res_exprs()
    _audio_in(comp, -400, -450)
    pix, abspath = _shader_dat(comp, 'shader_frag', shader, -200, 200)
    g = _glsl(comp, 'glsl1', pix, 0, 0, custom_res=res)
    cam_ops = []
    for i, n in enumerate(cams):
        c = _new(comp, selectTOP, 'cam%d' % n, -400, 150 - i * 120)
        c.par.top = '%s/CAM_%d' % (ESCENA, n)
        g.inputConnectors[i].connect(c)
        cam_ops.append(c)

    specs = [('uTime', ['absTime.seconds']), ('uResolution', res)]
    specs += _slot_specs(comp, five_slots, signature_extras, color_uniforms)
    check_uniforms(abspath, _bind_vectors(g, specs))

    sw = _new(comp, switchTOP, 'bypass', 200, 0)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(cam_ops[0])
    sw.par.index.expr = 'int(parent().par.Bypass)'
    _ensure_out(comp, 400, 0).inputConnectors[0].connect(sw)
    log('%s listo (layout %d cams) ← %s — conéctalo a switch1 a mano' % (comp.path, len(cams), shader))
    return comp
