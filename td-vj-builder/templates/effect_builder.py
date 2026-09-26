"""
TEMPLATE — Efecto / filtro de circuito cerrado (base18-24, base38-45)
=====================================================================
Construye la red de un efecto de camara DENTRO de un baseXX existente,
leyendo el feed de camara desde /project2/base17/switch1 y el audio desde
/project2/base17/audio_in. Idempotente: snapshot -> destroy managed -> rebuild.

NUNCA renombra el baseX. Solo administra sus children.

Como generar a partir de este template:
  - Reemplaza FILTER_NAME, SHADER_FILE, GLSL_NAME.
  - Llena FIVE_SLOTS con los 5 parametros en ORDEN DE ROL
    (intensidad, velocidad, distorsion, color, firma). Cada uno con su
    rango REAL. El tipo es 'f' (float) o 'c' (RGBA -> se bindea xyz).
  - SIGNATURE_EXTRAS: parametros adicionales del shader que NO entran en los
    5 macros pero el shader necesita (se exponen igual en la pagina Filter).
  - HAS_FEEDBACK: True si el shader usa sTD2DInputs[1] (feedback loop).
  - TARGET_BASE: el numero de base destino (ej. 'base18').

Ejecucion (Text DAT dentro del baseXX, o Textport):
  exec(open(<ruta>).read())
"""

import td

selectTOP    = td.selectTOP
selectCHOP   = td.selectCHOP
glslTOP      = td.glslTOP
feedbackTOP  = td.feedbackTOP
crossTOP     = td.crossTOP
constantTOP  = td.constantTOP
multiplyTOP  = td.multiplyTOP
switchTOP    = td.switchTOP
outTOP       = getattr(td, 'outTOP', None)
nullTOP      = td.nullTOP

# ----------------------------- CONFIG -----------------------------
TARGET_BASE = 'base18'
FILTER_NAME = 'TimeDisplacement'
SHADER_FILE = 'time_displacement.frag'   # vive en effects_glsl/shaders/
GLSL_NAME   = 'glsl_time_displacement'
HAS_FEEDBACK = True

SHADER_RELDIR = 'effects_glsl/shaders'   # relativo a project.folder

# Los 5 macros, en orden de ROL. (slot, role, uniform, par_name, kind, default, (min,max))
# kind: 'f' float, 'c' RGBA. par_name es el nombre del Custom Parameter en TD.
FIVE_SLOTS = [
    (1, 'intensity',  'uDisplaceAmount', 'Displaceamount', 'f', 0.035, (0.0, 0.2)),
    (2, 'speed',      'uTimeOffset',     'Timeoffset',     'f', 0.35,  (0.0, 1.0)),
    (3, 'distortion', 'uNoiseScale',     'Noisescale',     'f', 14.0,  (1.0, 40.0)),
    (4, 'color',      'uChromaSplit',    'Chromasplit',    'f', 0.008, (0.0, 0.05)),
    (5, 'signature',  'uFeedbackDecay',  'Feedbackdecay',  'f', 0.92,  (0.5, 0.995)),
]

# Parametros extra que el shader necesita pero no son macros (se exponen aparte).
# (uniform, par_name, kind, default, (min,max)|None)
SIGNATURE_EXTRAS = [
    ('uFeedbackOpacity', 'Feedbackopacity', 'f', 0.75, (0.0, 1.0)),
    ('uBlockSize',       'Blocksize',       'f', 24.0, (2.0, 96.0)),
    ('uLumaInfluence',   'Lumainfluence',   'f', 0.55, (0.0, 1.0)),
    ('uTint',            'Tint',            'c', (0.92, 0.98, 1.0, 1.0), None),
]
# ------------------------------------------------------------------


def _proj_folder():
    return td.project.folder.replace('\\', '/')


def _set_par_any(node, attempts):
    """attempts: tuple de (par_name, value, mode) con mode 'val' o 'expr'."""
    for name, value, mode in attempts:
        p = getattr(node.par, name, None)
        if p is None:
            continue
        try:
            if mode == 'expr':
                p.expr = value
            else:
                p.val = value
            return name
        except Exception:
            continue
    return None


def _create(parent, optype, name, x, y):
    n = parent.op(name)
    if n is None:
        n = parent.create(optype, name)
    n.nodeX, n.nodeY = x, y
    return n


def _connect(src, dst, idx=0):
    dst.inputConnectors[idx].connect(src)


def _add_float(page, name, default, rng):
    p = page.appendFloat(name, label=name)[0]
    p.default, p.val = float(default), float(default)
    if rng:
        p.normMin, p.normMax = rng
    return p


def _add_rgba(page, name, default):
    parts = page.appendRGBA(name, label=name)
    for p, v in zip(parts, default):
        p.default, p.val = v, v
    return parts


def _add_toggle(page, name, default=False):
    p = page.appendToggle(name, label=name)[0]
    p.default, p.val = int(default), int(default)
    return p


def _add_menu(page, name, names, labels, default_index=0):
    p = page.appendMenu(name, label=name)[0]
    p.menuNames, p.menuLabels = names, labels
    p.default = names[default_index]
    p.val = names[default_index]
    return p


import re as _re


def _expr_refs_missing_par(base, expr_str):
    """Devuelve la lista de parametros parent().par.X referenciados en la
    expresion que NO existen en el base. Vacia si todos existen."""
    missing = []
    for name in _re.findall(r"parent\(\)\.par\.([A-Za-z_]\w*)", str(expr_str)):
        # los componentes RGBA terminan en r/g/b/a; TD los expone como Xr/Xg...
        if not hasattr(base.par, name):
            missing.append(name)
    return missing


def _bind_uniform(glsl, uniform, expr_or_tuple, slot, base=None):
    """Asigna un vector uniform en la pagina Vectors del GLSL TOP.
    expr_or_tuple: str (1 componente) o tuple de str (vec).
    Si base se pasa, valida que todo parent().par.X referenciado exista; si
    falta alguno, avisa claro y NO escribe la expresion (evita el cook error
    'ParCollection has no attribute X')."""
    exprs = expr_or_tuple if isinstance(expr_or_tuple, (tuple, list)) else (expr_or_tuple,)
    if base is not None:
        for e in exprs:
            miss = _expr_refs_missing_par(base, e)
            if miss:
                print(f"  [WARN] uniform '{uniform}' (slot {slot}) referencia "
                      f"parametro(s) inexistente(s): {', '.join(miss)}. "
                      f"Crea ese Custom Parameter en el base o corrige el nombre. "
                      f"Salto este uniform.")
                return
    # name
    for cand in (f'Uniformname{slot}', f'uniformname{slot}',
                 f'Vec{slot}name', f'vec{slot}name'):
        np_ = getattr(glsl.par, cand, None)
        if np_ is not None:
            try: np_.val = uniform
            except Exception: pass
            break
    for i, e in enumerate(exprs):
        axis = 'xyzw'[i]
        idx = i
        for cand in (f'Value{slot}{axis}', f'value{slot}{axis}',
                     f'Vec{slot}value{idx}', f'vec{slot}value{idx}'):
            vp = getattr(glsl.par, cand, None)
            if vp is not None:
                try:
                    vp.expr = e
                    vp.mode = ParMode.EXPRESSION
                except Exception:
                    pass
                break


def _ensure_vec_rows(glsl, n):
    for cand in ('vectors', 'Vectors'):
        p = getattr(glsl.par, cand, None)
        seq = getattr(p, 'sequence', None) if p is not None else None
        if seq is not None:
            try:
                if seq.numBlocks < n:
                    seq.numBlocks = n
                return
            except Exception:
                pass


# --------- audio energy expression (shared contract) ----------
def _audio_energy_expr():
    return (
        "(op('audio_in')['low']*parent().par.Low "
        "+ op('audio_in')['mid']*parent().par.Mid "
        "+ op('audio_in')['high']*parent().par.High) "
        "* parent().par.Audiomult * parent().par.Audioreact "
        "if parent().op('audio_in') and parent().op('audio_in').numChans>0 else 0.0"
    )


def _slot_driven_expr(slot_index, par_name, rng):
    """clamp(slider + (energy if Audiotarget==slot else 0), min, max)."""
    lo, hi = (rng if rng else (0.0, 1.0))
    return (
        f"min({hi}, max({lo}, parent().par.{par_name} "
        f"+ (({_audio_energy_expr()}) if parent().par.Audiotarget.menuIndex=={slot_index-1} else 0.0)))"
    )


def build(base):
    # --- managed children: limpiar para idempotencia ---
    managed = ['select_video', 'audio_in', GLSL_NAME, 'shader_pixel',
               'feedback1', 'cross_intensity', 'constant_tint', 'mult_tint',
               'switch1', 'null1', 'out1']
    for nm in managed:
        ch = base.op(nm)
        if ch is not None:
            try: ch.destroy()
            except Exception: pass
    try:
        base.destroyCustomPars()
    except Exception:
        pass

    # --- input: select del switch de base17 ---
    inp = _create(base, selectTOP, 'select_video', -860, 0)
    for path in ('/project2/base17/switch1', '/base17/switch1'):
        if td.op(path):
            _set_par_any(inp, (('top', path, 'val'), ('topop', path, 'val')))
            break

    # --- audio_in: un solo Select CHOP, ruta CANONICA fija, canales low mid high ---
    # La fuente de audio del rig es project1/null4 (analisis con bandas).
    # Ruta relativa desde el baseXX: ../../project1/null4
    audio = _create(base, selectCHOP, 'audio_in', -860, 220)
    _set_par_any(audio, (('chop', '../../project1/null4', 'val'),
                         ('chopop', '../../project1/null4', 'val')))
    _set_par_any(audio, (('channames', 'low mid high', 'val'),
                         ('channelnames', 'low mid high', 'val')))

    # --- paginas custom: Filter (5 macros + extras + Bypass) ---
    page = base.appendCustomPage('Filter')
    for (slot, role, uniform, par_name, kind, default, rng) in FIVE_SLOTS:
        if kind == 'c':
            _add_rgba(page, par_name, default)
        else:
            _add_float(page, par_name, default, rng)
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        if kind == 'c':
            _add_rgba(page, par_name, default)
        else:
            _add_float(page, par_name, default, rng)
    _add_toggle(page, 'Bypass', default=False)

    # --- pagina Audio (contrato estandar) ---
    apage = base.appendCustomPage('Audio')
    _add_toggle(apage, 'Audioreact', default=True)
    _add_toggle(apage, 'Low',  default=True)
    _add_toggle(apage, 'Mid',  default=False)
    _add_toggle(apage, 'High', default=False)
    slot_names  = [s[3] for s in FIVE_SLOTS]
    _add_menu(apage, 'Audiotarget', slot_names, slot_names, default_index=0)
    _add_float(apage, 'Audiomult', 1.0, (0.0, 3.0))

    # --- shader DAT + GLSL TOP ---
    shader_abs = f'{_proj_folder()}/{SHADER_RELDIR}/{SHADER_FILE}'
    dat = _create(base, td.textDAT, 'shader_pixel', -860, -320)
    _set_par_any(dat, (('file', shader_abs, 'val'),))
    if hasattr(dat.par, 'syncfile'):
        dat.par.syncfile = True
    try: dat.par.loadonstartpulse.pulse()
    except Exception: pass

    glsl = _create(base, glslTOP, GLSL_NAME, -240, 0)
    _set_par_any(glsl, (('pixeldat', dat.name, 'val'),
                        ('pixelshader', dat.name, 'val')))
    # Output resolution = Use Input por default: el efecto hereda el tamano del
    # video que entra. Cambias el tamano en la fuente y el efecto lo sigue.
    _set_par_any(glsl, (('outputresolution', 'useinput', 'val'),
                        ('outputres', 'useinput', 'val')))
    sm = td.op('/project2/base17/escena_modular') or td.op('/project2/escena_modular')
    _connect(inp, glsl, 0)

    if HAS_FEEDBACK:
        fb = _create(base, feedbackTOP, 'feedback1', -240, -180)
        _set_par_any(fb, (('top', glsl.name, 'val'), ('targetop', glsl.name, 'val'),
                          ('target', glsl.name, 'val')))
        # El feedback captura la salida del GLSL (Target) y se reinyecta al input 1.
        # Ademas conectamos el source (select_video) al input del feedback para que
        # quede cableado automaticamente y no haya que hacerlo a mano.
        _connect(inp, fb, 0)
        _connect(fb, glsl, 1)

    # --- uniforms BASE primero (uTime, uResolution), luego 5 macros, luego extras ---
    # Casi todos los shaders de camara declaran uTime y uResolution; si no se
    # asignan en la pagina Vectors, TD tira warnings y el efecto sale plano.
    all_specs = [(s[0], s[2], s[3], s[6]) for s in FIVE_SLOTS]  # (slot,uniform,par,rng)
    _ensure_vec_rows(glsl, 2 + len(all_specs) + len(SIGNATURE_EXTRAS) + 1)
    vslot = 0

    # uTime = absTime.seconds
    _bind_uniform(glsl, 'uTime', 'absTime.seconds', vslot)
    vslot += 1
    # uResolution = resolucion real del propio GLSL TOP. Como el output esta en
    # "Use Input", esto sigue al tamano del video de entrada automaticamente.
    _bind_uniform(glsl, 'uResolution', ('me.width', 'me.height'), vslot)
    vslot += 1

    for (slot_index, uniform, par_name, rng) in all_specs:
        _bind_uniform(glsl, uniform, _slot_driven_expr(slot_index, par_name, rng), vslot, base=base)
        vslot += 1
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        if kind == 'c':
            _bind_uniform(glsl, uniform,
                          (f'parent().par.{par_name}r', f'parent().par.{par_name}g',
                           f'parent().par.{par_name}b'), vslot, base=base)
        else:
            _bind_uniform(glsl, uniform, f'parent().par.{par_name}', vslot, base=base)
        vslot += 1

    # --- post: cross (intensidad maestra opcional) + bypass switch ---
    cross = _create(base, crossTOP, 'cross_intensity', 80, 0)
    _connect(inp, cross, 0)
    _connect(glsl, cross, 1)
    if hasattr(cross.par, 'cross'):
        cross.par.cross.val = 1.0  # wet por defecto; el usuario puede mapear

    sw = _create(base, switchTOP, 'switch1', 500, 0)
    _connect(cross, sw, 0)
    _connect(inp, sw, 1)
    sw.par.index.expr = 'parent().par.Bypass'
    try: sw.par.index.mode = ParMode.EXPRESSION
    except Exception: pass

    out_src = sw
    null = _create(base, nullTOP, 'null1', 700, 0)
    _connect(out_src, null)
    try: null.viewer = True
    except Exception: pass
    if outTOP is not None:
        o = _create(base, outTOP, 'out1', 880, 0)
        _connect(null, o)

    print(f'[ok] {base.path} listo — {FILTER_NAME}')
    print(f'     5 macros: ' + ', '.join(s[3] for s in FIVE_SLOTS))
    print(f'     + Bypass + pagina Audio (Low/Mid/High, Audiotarget, Audiomult)')


def run():
    for path in (f'/{TARGET_BASE}', f'/project2/{TARGET_BASE}'):
        base = td.op(path)
        if base is not None:
            build(base)
            return
    print(f'[error] no encontre {TARGET_BASE} en /project2')


run()
