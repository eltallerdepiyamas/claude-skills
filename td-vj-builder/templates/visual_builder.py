"""
TEMPLATE — Visual generativo (base1-16)
=======================================
Construye la red de un VISUAL generativo dentro de un baseXX existente.
Convencion de uniforms snake_case: u_time, u_res, u_bass, u_color1/2/3,
+ los u_* propios del shader. #define u_input sTD2DInputs[0].

DOS variantes segun GENERATIVE_ONLY:
  - True  : visual puro, sin fuente de video (sTD2DInputs[0] vacio).
  - False : mezcla un input de video; el builder cablea una fuente al GLSL.
            Define INPUT_REF con el TOP que alimenta el visual.

Mismo contrato que los efectos: 5 macros en orden de rol + Bypass + pagina Audio.
Idempotente. NUNCA renombra el baseX.

Ejecucion (Text DAT dentro del baseXX, o Textport):
  exec(open(<ruta>).read())
"""

import td

selectTOP    = td.selectTOP
selectCHOP   = td.selectCHOP
glslTOP      = td.glslTOP
crossTOP     = td.crossTOP
switchTOP    = td.switchTOP
nullTOP      = td.nullTOP
outTOP       = getattr(td, 'outTOP', None)

# ----------------------------- CONFIG -----------------------------
TARGET_BASE = 'base1'
VISUAL_NAME = 'NeonGrid'
SHADER_FILE = '02_neon_grid.glsl'        # vive en visuals_glsl/shaders/
GLSL_NAME   = 'glsl_gen'

GENERATIVE_ONLY = True
INPUT_REF = '../base17/out1'             # solo se usa si GENERATIVE_ONLY=False

SHADER_RELDIR = 'visuals_glsl/shaders'

# 5 macros en orden de ROL. (slot, role, uniform, par_name, kind, default, (min,max))
FIVE_SLOTS = [
    (1, 'intensity',  'u_fog_density', 'Fogdensity', 'f', 1.5, (0.0, 4.0)),
    (2, 'speed',      'u_speed',       'Speed',      'f', 1.5, (0.0, 4.0)),
    (3, 'distortion', 'u_grid_scale',  'Gridscale',  'f', 8.0, (1.0, 24.0)),
    (4, 'color',      'u_glow_radius', 'Glowradius', 'f', 0.01, (0.0, 0.05)),
    (5, 'signature',  'u_horizon',     'Horizon',    'f', 0.5, (0.0, 1.0)),
]

# Extras del shader (no macros). (uniform, par_name, kind, default, (min,max)|None)
SIGNATURE_EXTRAS = [
    ('u_sun_size', 'Sunsize', 'f', 0.08, (0.0, 0.3)),
]

# Colores generativos -> RGBA pickers. (uniform, par_name, default_rgba)
COLOR_UNIFORMS = [
    ('u_color1', 'Color1', (1.0, 0.106, 0.553, 1.0)),
    ('u_color2', 'Color2', (0.0, 0.898, 1.0, 1.0)),
    ('u_color3', 'Color3', (0.039, 0.039, 0.039, 1.0)),
]
# ------------------------------------------------------------------


def _proj_folder():
    return td.project.folder.replace('\\', '/')


def _set_par_any(node, attempts):
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


import re as _re


def _expr_refs_missing_par(owner, expr_str):
    """Parametros parent().par.X referenciados que NO existen en owner."""
    missing = []
    for name in _re.findall(r"parent\(\)\.par\.([A-Za-z_]\w*)", str(expr_str)):
        if not hasattr(owner.par, name):
            missing.append(name)
    return missing


def _bind_uniform(glsl, uniform, expr_or_tuple, slot, owner=None):
    """Asigna un uniform en la pagina Vectors. Si owner se pasa, valida que
    todo parent().par.X exista; si falta, avisa y NO escribe (evita cook error)."""
    exprs = expr_or_tuple if isinstance(expr_or_tuple, (tuple, list)) else (expr_or_tuple,)
    if owner is not None:
        for e in exprs:
            miss = _expr_refs_missing_par(owner, e)
            if miss:
                print(f"  [WARN] uniform '{uniform}' (slot {slot}) referencia "
                      f"parametro(s) inexistente(s): {', '.join(miss)}. "
                      f"Crea ese Custom Parameter o corrige el nombre. Salto este uniform.")
                return
    for cand in (f'Uniformname{slot}', f'uniformname{slot}',
                 f'Vec{slot}name', f'vec{slot}name'):
        np_ = getattr(glsl.par, cand, None)
        if np_ is not None:
            try: np_.val = uniform
            except Exception: pass
            break
    for i, e in enumerate(exprs):
        axis = 'xyzw'[i]
        for cand in (f'Value{slot}{axis}', f'value{slot}{axis}',
                     f'Vec{slot}value{i}', f'vec{slot}value{i}'):
            vp = getattr(glsl.par, cand, None)
            if vp is not None:
                try:
                    vp.expr = e
                    try: vp.mode = ParMode.EXPRESSION
                    except Exception: pass
                except Exception:
                    pass
                break


def _audio_energy_expr():
    return (
        "(op('audio_in')['low']*parent().par.Low "
        "+ op('audio_in')['mid']*parent().par.Mid "
        "+ op('audio_in')['high']*parent().par.High) "
        "* parent().par.Audiomult * parent().par.Audioreact "
        "if parent().op('audio_in') and parent().op('audio_in').numChans>0 else 0.0"
    )


def _slot_driven_expr(slot_index, par_name, rng):
    lo, hi = (rng if rng else (0.0, 1.0))
    return (
        f"min({hi}, max({lo}, parent().par.{par_name} "
        f"+ (({_audio_energy_expr()}) if parent().par.Audiotarget.menuIndex=={slot_index-1} else 0.0)))"
    )


def build(base):
    managed = ['select_input', 'audio_in', GLSL_NAME, 'shader_pixel',
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

    # input opcional (solo si mezcla video)
    inp = None
    if not GENERATIVE_ONLY:
        inp = _create(base, selectTOP, 'select_input', -860, 0)
        _set_par_any(inp, (('top', INPUT_REF, 'val'), ('topop', INPUT_REF, 'val')))

    # audio_in (mismo contrato que efectos)
    audio = _create(base, selectCHOP, 'audio_in', -860, 220)
    for path in ('/project2/base17/audio_in', '/base17/audio_in'):
        if td.op(path):
            _set_par_any(audio, (('chop', path, 'val'), ('chopop', path, 'val')))
            break
    _set_par_any(audio, (('channames', 'low mid high', 'val'),
                         ('channelnames', 'low mid high', 'val')))

    # pagina Visual: 5 macros + extras + colores + Bypass
    page = base.appendCustomPage('Visual')
    for (slot, role, uniform, par_name, kind, default, rng) in FIVE_SLOTS:
        if kind == 'c':
            _add_rgba(page, par_name, default)
        else:
            _add_float(page, par_name, default, rng)
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        _add_float(page, par_name, default, rng)
    for (uniform, par_name, default) in COLOR_UNIFORMS:
        _add_rgba(page, par_name, default)
    _add_toggle(page, 'Bypass', default=False)

    # pagina Audio
    apage = base.appendCustomPage('Audio')
    _add_toggle(apage, 'Audioreact', default=True)
    _add_toggle(apage, 'Low',  default=True)
    _add_toggle(apage, 'Mid',  default=False)
    _add_toggle(apage, 'High', default=False)
    slot_names = [s[3] for s in FIVE_SLOTS]
    _add_menu(apage, 'Audiotarget', slot_names, slot_names, default_index=0)
    _add_float(apage, 'Audiomult', 1.0, (0.0, 3.0))

    # shader + GLSL
    shader_abs = f'{_proj_folder()}/{SHADER_RELDIR}/{SHADER_FILE}'
    dat = _create(base, td.textDAT, 'shader_pixel', -860, -320)
    _set_par_any(dat, (('file', shader_abs, 'val'),))
    if hasattr(dat.par, 'syncfile'):
        dat.par.syncfile = True
    try: dat.par.loadonstartpulse.pulse()
    except Exception: pass

    glsl = _create(base, glslTOP, GLSL_NAME, -240, 0)
    _set_par_any(glsl, (('pixeldat', dat.name, 'val'), ('pixelshader', dat.name, 'val')))
    _set_par_any(glsl, (('outputresolution', 'custom', 'val'),))
    sm = td.op('/project2/base17/escena_modular') or td.op('/project2/escena_modular')
    if sm is not None:
        for axis, cands in (('w', ('Resw', 'ResW')), ('h', ('Resh', 'ResH'))):
            rp = next((c for c in cands if hasattr(sm.par, c)), None)
            gp = getattr(glsl.par, f'resolution{axis}', None)
            if rp and gp is not None:
                gp.expr = f"op('{sm.path}').par.{rp}"
                try: gp.mode = ParMode.EXPRESSION
                except Exception: pass
    if inp is not None:
        _connect(inp, glsl, 0)

    # uniforms base + macros + extras + colores
    total = 3 + len(FIVE_SLOTS) + len(SIGNATURE_EXTRAS) + len(COLOR_UNIFORMS)
    _ensure_vec_rows(glsl, total + 1)
    vslot = 0
    _bind_uniform(glsl, 'u_time', 'absTime.seconds', vslot); vslot += 1
    if sm is not None:
        rw = next((c for c in ('Resw', 'ResW') if hasattr(sm.par, c)), None)
        rh = next((c for c in ('Resh', 'ResH') if hasattr(sm.par, c)), None)
        _bind_uniform(glsl, 'u_res',
                      (f"op('{sm.path}').par.{rw}", f"op('{sm.path}').par.{rh}"), vslot)
    vslot += 1
    _bind_uniform(glsl, 'u_bass', f"({_audio_energy_expr()})", vslot); vslot += 1

    for (slot_index, role, uniform, par_name, kind, default, rng) in FIVE_SLOTS:
        _bind_uniform(glsl, uniform, _slot_driven_expr(slot_index, par_name, rng), vslot, owner=base)
        vslot += 1
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        _bind_uniform(glsl, uniform, f'parent().par.{par_name}', vslot); vslot += 1
    for (uniform, par_name, default) in COLOR_UNIFORMS:
        _bind_uniform(glsl, uniform,
                      (f'parent().par.{par_name}r', f'parent().par.{par_name}g',
                       f'parent().par.{par_name}b'), vslot)
        vslot += 1

    # bypass: si mezcla input, dry = input; si es puro, dry = negro via la propia salida
    sw = _create(base, switchTOP, 'switch1', 300, 0)
    _connect(glsl, sw, 0)
    if inp is not None:
        _connect(inp, sw, 1)
    else:
        _connect(glsl, sw, 1)  # sin dry real; Bypass queda como passthrough del visual
    sw.par.index.expr = 'parent().par.Bypass'
    try: sw.par.index.mode = ParMode.EXPRESSION
    except Exception: pass

    null = _create(base, nullTOP, 'null1', 500, 0)
    _connect(sw, null)
    try: null.viewer = True
    except Exception: pass
    if outTOP is not None:
        o = _create(base, outTOP, 'out1', 680, 0)
        _connect(null, o)

    mode = 'generativo puro' if GENERATIVE_ONLY else f'mezcla input ({INPUT_REF})'
    print(f'[ok] {base.path} listo — {VISUAL_NAME} ({mode})')
    print(f'     5 macros: ' + ', '.join(s[3] for s in FIVE_SLOTS))
    print(f'     colores: ' + ', '.join(c[1] for c in COLOR_UNIFORMS) + ' + Bypass + Audio')


def run():
    for path in (f'/{TARGET_BASE}', f'/project2/{TARGET_BASE}'):
        base = td.op(path)
        if base is not None:
            build(base)
            return
    print(f'[error] no encontre {TARGET_BASE} en /project2')


run()
