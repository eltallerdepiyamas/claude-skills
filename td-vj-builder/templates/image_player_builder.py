"""
TEMPLATE — Reproductor de imagenes desde carpeta (base1-16)
===========================================================
Carga una CARPETA de imagenes (logos, PNGs, etc.) y permite cambiar entre
ellas en vivo con un solo parametro (indice). Encima aplica tratamiento por
shader (tinte Klein, strobo, stripes, etc.). Mismo contrato que los visuales:
5 macros en orden de rol + Bypass + pagina Audio. Idempotente. NUNCA renombra el baseX.

Como funciona:
  - Un Movie File In TOP en modo carpeta recorre todas las imagenes de IMAGE_DIR.
  - El parametro Imageindex (slot 1) elige cual imagen se ve -> switch en vivo.
  - El GLSL toma esa imagen como sTD2DInputs[0] y le aplica el look (Klein/strobo/stripes).
  - Para agregar una imagen nueva: suelta un PNG en la carpeta. Cero codigo.

IMPORTANTE sobre SVG: TouchDesigner no carga .svg en un TOP. Exporta tus SVG a
PNG con fondo transparente (2048 px lado largo) y ponlos en IMAGE_DIR.

Ejecucion (Text DAT dentro del baseXX, o Textport):
  exec(open(<ruta>).read())
"""

import td

moviefileinTOP = (getattr(td, 'moviefileinTOP', None)
                  or getattr(td, 'movieFileInTOP', None))
selectCHOP   = td.selectCHOP
glslTOP      = td.glslTOP
crossTOP     = td.crossTOP
switchTOP    = td.switchTOP
nullTOP      = td.nullTOP
outTOP       = getattr(td, 'outTOP', None)

# ----------------------------- CONFIG -----------------------------
TARGET_BASE = 'base3'
VISUAL_NAME = 'LogoPlayer'
SHADER_FILE = 'logo_player.glsl'         # vive en visuals_glsl/shaders/
GLSL_NAME   = 'glsl_gen'

# Carpeta de imagenes, relativa a project.folder (donde esta el .toe).
# Mete ahi los PNGs (logos exportados desde SVG, etc.).
IMAGE_DIR   = 'assets/logos'
SHADER_RELDIR = 'visuals_glsl/shaders'

NUM_IMAGES_DEFAULT = 12   # rango del slider de indice; ajusta a cuantas imagenes tengas

# 5 macros en orden de ROL. (slot, role, uniform, par_name, kind, default, (min,max))
# slot 1 (intensidad) lo usamos como SELECTOR de imagen: cambia cual se ve.
FIVE_SLOTS = [
    (1, 'intensity',  'u_image_index', 'Imageindex',  'f', 0.0,  (0.0, float(NUM_IMAGES_DEFAULT - 1))),
    (2, 'speed',      'u_strobe_speed','Strobespeed', 'f', 0.0,  (0.0, 30.0)),
    (3, 'distortion', 'u_stripes',     'Stripes',     'f', 0.0,  (0.0, 64.0)),
    (4, 'color',      'u_klein_mix',   'Kleinmix',    'f', 1.0,  (0.0, 1.0)),
    (5, 'signature',  'u_scale',       'Scale',       'f', 1.0,  (0.2, 3.0)),
]

SIGNATURE_EXTRAS = [
    ('u_invert', 'Invert', 'f', 0.0, (0.0, 1.0)),  # strobo a negativo blanco/negro
]

# Colores. color1 = Klein por default; color2/3 = blanco/negro para strobos.
COLOR_UNIFORMS = [
    ('u_color1', 'Color1', (0.0, 0.184, 0.655, 1.0)),  # Yves Klein Blue #002FA7
    ('u_color2', 'Color2', (1.0, 1.0, 1.0, 1.0)),       # blanco
    ('u_color3', 'Color3', (0.0, 0.0, 0.0, 1.0)),       # negro
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
    missing = []
    for name in _re.findall(r"parent\(\)\.par\.([A-Za-z_]\w*)", str(expr_str)):
        if not hasattr(owner.par, name):
            missing.append(name)
    return missing


def _bind_uniform(glsl, uniform, expr_or_tuple, slot, owner=None):
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
    managed = ['image_folder', 'audio_in', GLSL_NAME, 'shader_pixel',
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

    # --- Movie File In en modo CARPETA: recorre todas las imagenes ---
    img = _create(base, moviefileinTOP, 'image_folder', -860, 0)
    img_abs = f'{_proj_folder()}/{IMAGE_DIR}'
    # Modo carpeta + indice controlado por Imageindex
    _set_par_any(img, (('moviefolder', img_abs, 'val'),
                       ('folder', img_abs, 'val'),
                       ('file', img_abs, 'val')))
    # Reproducir por indice (no por tiempo): si el TOP soporta 'index'/'cuepoint'
    _set_par_any(img, (('playmode', 'index', 'val'),))
    _set_par_any(img, (('index', "int(parent().par.Imageindex)", 'expr'),
                       ('cuepoint', "int(parent().par.Imageindex)", 'expr')))

    # --- audio_in (mismo contrato) ---
    audio = _create(base, selectCHOP, 'audio_in', -860, 220)
    _set_par_any(audio, (('chop', '../../project1/null4', 'val'),
                         ('chopop', '../../project1/null4', 'val')))
    _set_par_any(audio, (('channames', 'low mid high', 'val'),
                         ('channelnames', 'low mid high', 'val')))

    # --- pagina Visual: 5 macros + extras + colores + Bypass ---
    page = base.appendCustomPage('Visual')
    for (slot, role, uniform, par_name, kind, default, rng) in FIVE_SLOTS:
        _add_float(page, par_name, default, rng)
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        _add_float(page, par_name, default, rng)
    for (uniform, par_name, default) in COLOR_UNIFORMS:
        _add_rgba(page, par_name, default)
    _add_toggle(page, 'Bypass', default=False)

    # --- pagina Audio ---
    apage = base.appendCustomPage('Audio')
    _add_toggle(apage, 'Audioreact', default=True)
    _add_toggle(apage, 'Low',  default=True)
    _add_toggle(apage, 'Mid',  default=False)
    _add_toggle(apage, 'High', default=False)
    slot_names = [s[3] for s in FIVE_SLOTS]
    _add_menu(apage, 'Audiotarget', slot_names, slot_names, default_index=1)  # default: strobo
    _add_float(apage, 'Audiomult', 1.0, (0.0, 3.0))

    # --- shader + GLSL ---
    shader_abs = f'{_proj_folder()}/{SHADER_RELDIR}/{SHADER_FILE}'
    dat = _create(base, td.textDAT, 'shader_pixel', -860, -320)
    _set_par_any(dat, (('file', shader_abs, 'val'),))
    if hasattr(dat.par, 'syncfile'):
        dat.par.syncfile = True
    try: dat.par.loadonstartpulse.pulse()
    except Exception: pass

    glsl = _create(base, glslTOP, GLSL_NAME, -240, 0)
    _set_par_any(glsl, (('pixeldat', dat.name, 'val'), ('pixelshader', dat.name, 'val')))
    # La imagen entra como input 0; el shader la trata (Klein/strobo/stripes).
    _set_par_any(glsl, (('outputresolution', 'useinput', 'val'),
                        ('outputres', 'useinput', 'val')))
    _connect(img, glsl, 0)

    # uniforms base + macros + extras + colores
    total = 3 + len(FIVE_SLOTS) + len(SIGNATURE_EXTRAS) + len(COLOR_UNIFORMS)
    _ensure_vec_rows(glsl, total + 1)
    vslot = 0
    _bind_uniform(glsl, 'u_time', 'absTime.seconds', vslot); vslot += 1
    _bind_uniform(glsl, 'u_res', ('me.width', 'me.height'), vslot); vslot += 1
    _bind_uniform(glsl, 'u_bass', f"({_audio_energy_expr()})", vslot); vslot += 1

    for (slot_index, role, uniform, par_name, kind, default, rng) in FIVE_SLOTS:
        _bind_uniform(glsl, uniform, _slot_driven_expr(slot_index, par_name, rng), vslot, owner=base)
        vslot += 1
    for (uniform, par_name, kind, default, rng) in SIGNATURE_EXTRAS:
        _bind_uniform(glsl, uniform, f'parent().par.{par_name}', vslot, owner=base); vslot += 1
    for (uniform, par_name, default) in COLOR_UNIFORMS:
        _bind_uniform(glsl, uniform,
                      (f'parent().par.{par_name}r', f'parent().par.{par_name}g',
                       f'parent().par.{par_name}b'), vslot, owner=base)
        vslot += 1

    # bypass: dry = imagen cruda (sin tratamiento)
    sw = _create(base, switchTOP, 'switch1', 300, 0)
    _connect(glsl, sw, 0)
    _connect(img, sw, 1)
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

    print(f'[ok] {base.path} listo — {VISUAL_NAME} (reproductor de carpeta: {IMAGE_DIR})')
    print(f'     Imageindex cambia la imagen en vivo; 5 macros: '
          + ', '.join(s[3] for s in FIVE_SLOTS))
    print(f'     SVG -> exportar a PNG transparente y poner en {IMAGE_DIR}')


def run():
    for path in (f'/{TARGET_BASE}', f'/project2/{TARGET_BASE}'):
        base = td.op(path)
        if base is not None:
            build(base)
            return
    print(f'[error] no encontre {TARGET_BASE} en /project2')


run()
