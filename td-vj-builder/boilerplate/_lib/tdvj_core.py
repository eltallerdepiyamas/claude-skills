"""
tdvj_core.py — núcleo compartido de los builders VJ (skill td-vj-builder).
Linaje: ON TOUR x MERCADO LIBRE → CORONA x FUTURE x ULTRA → boilerplate.
Lo propio de cada show (rangos de bases, audio, cámaras) va en _lib/rig.py, no aquí.

Los setup_*.py lo importan desde un Text DAT dentro de TouchDesigner:

    import sys, importlib
    sys.path.insert(0, project.folder + '/_lib')
    import tdvj_core; importlib.reload(tdvj_core)

Reglas del rig (no negociables — el sampler MIDI depende de ellas):
  - Nunca renombrar / mover / destruir un baseX. Solo se gestionan sus hijos.
  - 5 sliders en orden de rol + Bypass aparte + página Audio en cada base.
  - Visuales base1–18 · Efectos (assets de marca) base19–24 y base38–45.

Cada base trae además:
  - Página Audio: Audioreact · Low/Mid/High (suman) · Audiotarget · Audiomult · Smooth · Audiochop · Energy.
    u_bass (visuales) / uEnergy (efectos) = Energy: las bandas activas, suavizadas, ya multiplicadas.
  - Página Salida: Resw / Resh propios de la base (resolución del GLSL). Para cambiar todas
    a la vez: builders/herramientas/aplicar_resolucion.py.

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
# sin cámaras en este show: base17 ya no es el host de escena_modular (2026-10-23, ahora es visual).
# CAMERA_SWITCH queda solo como fallback de build_effect; los efectos de marca pasan su propio source.
ESCENA        = ROOT + '/base17/escena_modular'
CAMERA_SWITCH = ESCENA + '/switch1'
AUDIO_SOURCE  = '/project1/null4'          # canónico del rig · canales: low mid high (+ otros)

# 2026-10-23: base17–18 alojan visuales (refs. pinterest del cliente; sin cámaras) → marca empieza en base19
VISUAL_BASES = list(range(1, 19))
EFFECT_BASES = [n for n in list(range(18, 25)) + list(range(38, 46)) if n not in VISUAL_BASES]

DEFAULT_RES = (1920, 1080)                 # provisional hasta tener el pixel map
TAG = 'tdvj'
SLOT_ROLES = ('intensidad', 'velocidad', 'distorsión', 'color', 'firma')

# lo propio del show sobreescribe los defaults de arriba (_lib/rig.py, opcional)
try:
    import rig as _rig
    for _k in ('ROOT', 'ESCENA', 'CAMERA_SWITCH', 'AUDIO_SOURCE', 'VISUAL_BASES', 'EFFECT_BASES', 'DEFAULT_RES'):
        if hasattr(_rig, _k):
            globals()[_k] = getattr(_rig, _k)
except ImportError:
    pass

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


def _int(page, name, label, mn, mx, default):
    p, created = _upsert(page, 'Int', name, label)
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


def _band_expr(band):
    """Canal suavizado de una banda, con fallback a 0 si el CHOP o el canal no existen.
    Se evalúa en un parámetro del COMP: me = la base, me.op() busca entre sus hijos."""
    return ("(me.op('audio_smooth')['{b}'].eval() if me.op('audio_smooth') is not None "
            "and me.op('audio_smooth')['{b}'] is not None else 0.0)").format(b=band)


def build_contract(comp, page_name, five_slots, extras=(), colors=(), resolution=DEFAULT_RES,
                   colmap='repartido', techo=None):
    """Página principal (5 slots + extras + colores + Bypass), página Audio y página Salida."""
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

    # Audio: todas las bases pueden ser audio-reactivas
    ap = _page(comp, 'Audio')
    _toggle(ap, 'Audioreact', 'Audio React', True)
    _toggle(ap, 'Low', 'Low', True)
    _toggle(ap, 'Mid', 'Mid', False)
    _toggle(ap, 'High', 'High', False)
    slot_names = [s[0] for s in five_slots]
    _menu(ap, 'Audiotarget', 'Audio Target', slot_names,
          ['%d %s' % (i + 1, n) for i, n in enumerate(slot_names)], slot_names[0])
    _float(ap, 'Audiomult', 'Audio Mult', 0.0, 3.0, 1.0)
    _float(ap, 'Smooth', 'Smooth (s)', 0.0, 1.0, 0.12)
    _opref(ap, 'Audiochop', 'Audio CHOP', AUDIO_SOURCE, style='CHOP')
    energy = _float(ap, 'Energy', 'Energy (lectura)', 0.0, 3.0, 0.0)
    energy.clampMax = False
    energy.expr = ('({l} * me.par.Low + {m} * me.par.Mid + {h} * me.par.High)'
                   ' * me.par.Audiomult * me.par.Audioreact').format(
        l=_band_expr('low'), m=_band_expr('mid'), h=_band_expr('high'))
    energy.readOnly = True
    _prune_and_sort(ap, ['Audioreact', 'Low', 'Mid', 'High', 'Audiotarget', 'Audiomult',
                         'Smooth', 'Audiochop', 'Energy'])

    # Salida: resolución propia de cada base
    sp = _page(comp, 'Salida')
    _int(sp, 'Resw', 'Resolución W', 64, 8192, int(resolution[0]))   # default solo al crear: luego manda tu valor
    _int(sp, 'Resh', 'Resolución H', 64, 8192, int(resolution[1]))
    # cómo se acomoda en las 8 columnas (lo aplica /project2/salidas). Lo dicta SIEMPRE el CONFIG
    # del builder: es parte del diseño de la base, no se opera en vivo.
    cm = _menu(sp, 'Colmap', 'Columnas: acomodo', ['repartido', 'repetido'],
               ['Repartido (un canvas alrededor)', 'Repetido (igual en cada columna)'], colmap)
    cm.val = colmap
    keep = ['Resw', 'Resh', 'Colmap']
    if techo:   # versión propia para el techo (out_techo, cuadrada); si no, el techo recorta out1 a 1:1
        _int(sp, 'Techores', 'Techo: resolución (1:1)', 64, 8192, int(techo))
        keep.append('Techores')
    _prune_and_sort(sp, keep)


# API pública para los ganchos `extra` de los builders (páginas y nodos propios)
page, float_par, int_par, toggle_par, menu_par, rgb_par, prune_and_sort = (
    _page, _float, _int, _toggle, _menu, _rgb, _prune_and_sort)
opref_par, pulse_par = _opref, _pulse

RES_EXPRS = ['parent().par.Resw', 'parent().par.Resh']


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
    # GLSL TOP, Script CHOP, etc. crean DATs acoplados por defecto; los quitamos
    for d in list(o.docked):
        if d.valid:
            d.destroy()
    if o.name != name:
        warn('%s ya existía (no gestionado); el nuevo se llama %s' % (name, o.name))
    o.tags.add(TAG)
    o.nodeX, o.nodeY = x, y
    return o


new_op = _new


def _ensure_out(comp, x, y):
    o = comp.op('out1')
    if o is None or o.OPType != 'outTOP':
        o = comp.create(outTOP, 'out1')
    o.nodeX, o.nodeY = x, y
    return o


def ensure_comp(parent_path, name, x=0, y=0):
    """COMP de herramienta (no baseX, p.ej. previz): se crea si falta y nunca se destruye."""
    parent = op(parent_path)
    c = parent.op(name)
    if c is None:
        c = parent.create(baseCOMP, name)
        c.nodeX, c.nodeY = x, y
        log('creado %s' % c.path)
    return c


def _ensure_named_out(comp, name, x, y):
    """Out TOP persistente (sin tag) para no romper cables que salgan del base."""
    o = comp.op(name)
    if o is None or o.OPType != 'outTOP':
        o = comp.create(outTOP, name)
    o.nodeX, o.nodeY = x, y
    return o


def _audio_in(comp, x, y):
    """audio_in (Select CHOP, low mid high) → audio_smooth (Lag CHOP, página Audio → Smooth)."""
    a = _new(comp, selectCHOP, 'audio_in', x, y)
    chop_par = getattr(a.par, 'chop', None) or getattr(a.par, 'chops', None)
    if chop_par is None:
        warn('Select CHOP sin parámetro chop/chops')
    else:
        chop_par.expr = 'parent().par.Audiochop'
    _set(a, 'channames', 'low mid high kick')   # kick: disparos exactos (Audio Analysis); si no existe → 0
    if op(AUDIO_SOURCE) is None:
        warn('no existe %s — arrastra tu CHOP de análisis a Audio → Audio CHOP' % AUDIO_SOURCE)

    s = _new(comp, lagCHOP, 'audio_smooth', x + 200, y)
    s.inputConnectors[0].connect(a)
    _set_expr(s, 'lag1', 'parent().par.Smooth * 0.25')   # ataque rápido
    _set_expr(s, 'lag2', 'parent().par.Smooth')          # caída suave
    return s


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


def _black(comp, x, y):
    b = _new(comp, constantTOP, 'black', x, y)
    for pn, v in (('colorr', 0), ('colorg', 0), ('colorb', 0), ('alpha', 0)):
        _set(b, pn, v)
    _set(b, 'outputresolution', 'custom')
    _set_expr(b, 'resolutionw', RES_EXPRS[0])
    _set_expr(b, 'resolutionh', RES_EXPRS[1])
    return b


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


def _slot_specs(comp, five_slots, extras, colors):
    specs = []
    for (name, uni, mn, mx, _d) in five_slots:
        e = _slot_expr(comp, name, mn, mx)
        specs.append((uni, [e]) if e else None)
    for (name, uni, mn, mx, _d) in extras:
        e = _slot_expr(comp, name, mn, mx, audio=False)
        specs.append((uni, [e]) if e else None)
    for (name, uni, _rgb) in colors:
        specs.append((uni, ['parent().par.%sr' % name, 'parent().par.%sg' % name,
                            'parent().par.%sb' % name]))
    return specs


def _feedback(comp, g, reset_src, input_index, page_name):
    fb = _new(comp, feedbackTOP, 'feedback1', -200, -150)
    fb.inputConnectors[0].connect(reset_src)
    fb.par.top = g.name
    _set(fb, 'format', 'rgba16float')
    g.inputConnectors[input_index].connect(fb)
    pulse_par(_page(comp, page_name), 'Resetfb', 'Reset estela')
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
    return fb


# ─────────────────────────────────────────────────────────────── audio opcional por shader
# Si el shader DECLARA estos uniforms, se enlazan solos (si no, no se crean → sin warnings).
#   u_low / u_mid / u_high : cada banda suavizada × Audiomult × Audioreact (ignoran los toggles Low/Mid/High)
#   u_kick                 : canal kick crudo (sin Lag, para golpes exactos) × Audioreact
def _chan_expr(chop, ch):
    return ("(op('{c}')['{n}'].eval() if op('{c}') is not None and op('{c}')['{n}'] is not None "
            "else 0.0)").format(c=chop, n=ch)


OPTIONAL_AUDIO = {
    'u_low':  _chan_expr('audio_smooth', 'low') + ' * parent().par.Audiomult * parent().par.Audioreact',
    'u_mid':  _chan_expr('audio_smooth', 'mid') + ' * parent().par.Audiomult * parent().par.Audioreact',
    'u_high': _chan_expr('audio_smooth', 'high') + ' * parent().par.Audiomult * parent().par.Audioreact',
    'u_kick': _chan_expr('audio_in', 'kick') + ' * parent().par.Audioreact',
}


def _declared(abspath):
    try:
        with open(abspath, encoding='utf-8') as f:
            return set(_UNIFORM_RE.findall(f.read()))
    except OSError:
        return set()


def _optional_audio_specs(abspath):
    d = _declared(abspath)
    return [(u, [e]) for u, e in OPTIONAL_AUDIO.items() if u in d]


# ─────────────────────────────────────────────────────────────── secuenciador por kick
KICK_CB = """# generado por tdvj_core.kick_step — avanza Step en cada kick (cruce del umbral hacia arriba)
def onValueChange(channel, sampleIndex, val, prev):
    comp = me.parent()
    thr = comp.par.Threshold.eval()
    if prev < thr <= val:
        comp.par.Step = (comp.par.Step.eval() + 1) % 64
    return
"""


def kick_step(comp):
    """Página Secuencia: Stepmode (kick / bpm) · Bpm · Threshold · Step. Devuelve el spec de u_step.
    Úsalo como `extra=tdvj_core.kick_step` en el CONFIG del builder."""
    pg = _page(comp, 'Secuencia')
    _menu(pg, 'Stepmode', 'Avanza con', ['kick', 'bpm'], ['Kick (Audio Analysis)', 'BPM fijo'], 'kick')
    _float(pg, 'Bpm', 'BPM', 60.0, 200.0, 128.0)
    _float(pg, 'Threshold', 'Umbral kick', 0.05, 1.0, 0.5)
    _int(pg, 'Step', 'Paso (lectura)', 0, 63, 0)
    _prune_and_sort(pg, ['Stepmode', 'Bpm', 'Threshold', 'Step'])
    ex = _new(comp, chopexecuteDAT, 'on_kick', -400, -500)
    _set(ex, 'chop', 'audio_in')
    for pn in ('channels', 'channel'):
        if getattr(ex.par, pn, None) is not None:
            _set(ex, pn, 'kick')
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False),
                  ('whileon', False), ('whileoff', False)):
        if getattr(ex.par, pn, None) is not None:
            _set(ex, pn, v)
    ex.text = KICK_CB
    return [('u_step', ["float(parent().par.Step) if parent().par.Stepmode.eval() == 'kick' "
                        "else float(math.floor(absTime.seconds * parent().par.Bpm / 60.0))"])]


def refresh_salidas():
    """/project2/salidas elige out_techo / out1 con una expresión que TD solo re-evalúa cuando cambia Visual:
    crear o quitar un out_techo no la despierta y el techo se queda con out1 (el canvas de columnas recortado).
    Se llama al terminar cada builder y la limpieza para que las salidas siempre lean el out correcto."""
    s = op(ROOT + '/salidas')
    if s is None:
        return
    for name in ('src_columnas', 'src_techo', 'src_marca'):
        o = s.op(name)
        p = getattr(o.par, 'top', None) if o is not None else None
        if p is not None and p.expr:
            e = p.expr
            p.expr = e                          # re-asignar fuerza a evaluar de nuevo


# ─────────────────────────────────────────────────────────────── builders
def build_visual(base, shader, five_slots, signature_extras=(), color_uniforms=(),
                 source=None, feedback=False, extra=None, page='Visual', resolution=DEFAULT_RES,
                 colmap='repartido', techo=False):
    """Visual generativo: [source] → GLSL → bypass(negro) → out1.

    source:   None = generativo puro · o ruta de un TOP (entra en sTD2DInputs[0], #define u_input).
    feedback: True = la salida anterior del GLSL entra en sTD2DInputs[0] (o [1] si hay source).
              Pulso Resetfb en la página principal.
    extra:    función extra(comp) → [(uniform, [x, y, z, w])] para uniforms propios del visual.
    colmap:   cómo se acomoda en columnas: 'repartido' (un canvas alrededor de las 8) /
              'repetido' (el centro del canvas en cada columna). El techo recibe la misma imagen 1:1.
    techo:    True = la base renderiza también una versión propia para el techo (GLSL 'glsl_techo',
              cuadrada, Salida → Techores) con el MISMO shader y u_surface = 1 → out_techo.
              Las salidas la usan en TD_techo; sin techo, TD_techo recorta out1 a 1:1.
    Uniforms base: u_time · u_res (= Salida Resw/Resh) · u_bass (= Audio → Energy) ·
                   u_surface (0 columnas / 1 techo, si el shader lo declara).
    """
    check_range(base, VISUAL_BASES, 'visuales (1–18)')
    comp = find_base(base)
    build_contract(comp, page, five_slots, signature_extras, color_uniforms, resolution=resolution,
                   colmap=colmap, techo=1080 if techo else None)
    clear_managed(comp)

    _audio_in(comp, -600, -300)
    pix, abspath = _shader_dat(comp, 'shader_frag', shader, -200, 200)
    g = _glsl(comp, 'glsl1', pix, 0, 0, custom_res=RES_EXPRS)
    if source:
        src = _new(comp, selectTOP, 'src_in', -400, 0)
        src.par.top = source
        g.inputConnectors[0].connect(src)

    # 1) grafo completo y conectado ANTES de cualquier paso que pueda fallar
    black = _black(comp, 0, -150)
    if feedback:
        _feedback(comp, g, black, 1 if source else 0, page)
    sw = _new(comp, switchTOP, 'bypass', 200, 0)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(black)
    sw.par.index.expr = 'int(parent().par.Bypass)'
    _ensure_out(comp, 400, 0).inputConnectors[0].connect(sw)

    # 2) uniforms
    specs = [('u_time', ['absTime.seconds']),
             ('u_res', RES_EXPRS),
             ('u_bass', ['parent().par.Energy'])]
    specs += _optional_audio_specs(abspath)
    specs += _slot_specs(comp, five_slots, signature_extras, color_uniforms)
    if extra is not None:
        try:
            specs += extra(comp) or []
        except Exception:
            import traceback
            traceback.print_exc()
            warn('%s: falló extra — la base queda conectada pero sin esos uniforms' % comp.path)
    declared = _declared(abspath)
    surf = [('u_surface', [0.0])] if 'u_surface' in declared else []
    check_uniforms(abspath, _bind_vectors(g, specs + surf))

    if techo:
        tres = ['parent().par.Techores', 'parent().par.Techores']
        gt = _glsl(comp, 'glsl_techo', pix, 0, -400, custom_res=tres)
        if source:
            gt.inputConnectors[0].connect(comp.op('src_in'))
        bt = _new(comp, constantTOP, 'black_techo', 0, -550)
        for pn, v in (('colorr', 0), ('colorg', 0), ('colorb', 0), ('alpha', 0)):
            _set(bt, pn, v)
        _set(bt, 'outputresolution', 'custom')
        _set_expr(bt, 'resolutionw', tres[0])
        _set_expr(bt, 'resolutionh', tres[1])
        swt = _new(comp, switchTOP, 'bypass_techo', 200, -400)
        swt.inputConnectors[0].connect(gt)
        swt.inputConnectors[1].connect(bt)
        swt.par.index.expr = 'int(parent().par.Bypass)'
        _ensure_named_out(comp, 'out_techo', 400, -400).inputConnectors[0].connect(swt)
        tspecs = [(u, tres if u == 'u_res' else v) for (u, v) in specs]
        check_uniforms(abspath, _bind_vectors(gt, tspecs + [('u_surface', [1.0])]))
        if 'u_surface' not in declared:
            log('%s: techo = mismo shader a 1:1 en todo el canvas (sin u_surface)' % comp.path)
    else:
        ot = comp.op('out_techo')
        if ot is not None:
            ot.destroy()            # ya no hay versión de techo: salidas vuelve a recortar out1
    refresh_salidas()
    log('%s listo (visual%s%s) ← %s' % (comp.path, ' + input' if source else ' puro',
                                         ' + techo' if techo else '', shader))
    return comp


def build_effect(base, shader, five_slots, signature_extras=(), color_uniforms=(),
                 source=None, feedback=False, extra=None, page='Filter'):
    """Efecto / filtro (en este show: procesa assets de marca para las laterales).
    source → [feedback] → GLSL → bypass(source) → out1.
    source: ruta del TOP a procesar (player de marca). None = base17/switch1 (cámaras del rig).
    Uniforms base: uTime · uResolution (= Salida Resw/Resh) · uEnergy (= Audio → Energy).
    """
    check_range(base, EFFECT_BASES, 'efectos (19–24, 38–45)')
    comp = find_base(base)
    build_contract(comp, page, five_slots, signature_extras, color_uniforms)
    clear_managed(comp)

    _audio_in(comp, -600, -300)
    src = _new(comp, selectTOP, 'src_in', -400, 0)
    src.par.top = source or CAMERA_SWITCH
    pix, abspath = _shader_dat(comp, 'shader_frag', shader, -200, 200)
    g = _glsl(comp, 'glsl1', pix, 0, 0, custom_res=RES_EXPRS)
    g.inputConnectors[0].connect(src)
    if feedback:
        _feedback(comp, g, src, 1, page)

    sw = _new(comp, switchTOP, 'bypass', 200, 0)
    sw.inputConnectors[0].connect(g)
    sw.inputConnectors[1].connect(src)
    sw.par.index.expr = 'int(parent().par.Bypass)'
    _ensure_out(comp, 400, 0).inputConnectors[0].connect(sw)

    specs = [('uTime', ['absTime.seconds']),
             ('uResolution', RES_EXPRS),
             ('uEnergy', ['parent().par.Energy'])]
    specs += _slot_specs(comp, five_slots, signature_extras, color_uniforms)
    if extra is not None:
        try:
            specs += extra(comp) or []
        except Exception:
            import traceback
            traceback.print_exc()
            warn('%s: falló extra — la base queda conectada pero sin esos uniforms' % comp.path)
    check_uniforms(abspath, _bind_vectors(g, specs))
    log('%s listo (efecto%s) ← %s' % (comp.path, ' + feedback' if feedback else '', shader))
    return comp
