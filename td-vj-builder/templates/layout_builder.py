"""
TEMPLATE — Layout CCTV (multi-camara) dentro de escena_modular
==============================================================
Construye un layout_<name> como Base COMP DENTRO de
/project2/base17/escena_modular. Arregla 2-5 camaras con un GLSL multi TOP.
Camaras = sTD2DInputs[0..4] (NUNCA uniform sampler2D).

A diferencia de visuales/efectos, el layout NO va en un baseXX numerado: vive
en escena_modular junto a los otros layout_*. Igual respeta el contrato de
5 macros + pagina Audio, expuestos en la RAIZ del layout COMP.

Pasos manuales tras correr (se imprimen): conectar layout_<name>/out1 al switch
de seleccion de layouts y agregarlo al menu Modelayout. El script NO toca menus
ni renombra nada.

Ejecucion (Text DAT, o Textport):
  exec(open(<ruta>).read())
"""

import td

selectTOP     = td.selectTOP
selectCHOP    = td.selectCHOP
glslmultiTOP  = td.glslmultiTOP
outTOP        = getattr(td, 'outTOP', None)
baseCOMP      = td.baseCOMP

# ----------------------------- CONFIG -----------------------------
SCENE_PATH  = '/project2/base17/escena_modular'
LAYOUT_NAME = 'layout_breathing_grid'
SHADER_FILE = 'layout_breathing_grid.frag'   # vive en layouts_glsl/shaders/
SHADER_RELDIR = 'layouts_glsl/shaders'
NUM_CAMS = 5

# 5 macros en orden de ROL. (slot, role, uniform, par_name, default, (min,max))
FIVE_SLOTS = [
    (1, 'intensity',  'uBreathAmt',   'Breathamt',   0.12, (0.0, 0.4)),
    (2, 'speed',      'uSpeed',       'Speed',       0.3,  (0.0, 2.0)),
    (3, 'distortion', 'uPhaseOffset', 'Phaseoffset', 1.0,  (0.0, 3.0)),
    (4, 'color',      'uBgColor',     'Bgcolor',     None, None),   # RGBA
    (5, 'signature',  'uGap',         'Gap',         0.0,  (0.0, 16.0)),
]

CAMCOUNT_CANDS = ['Camerasenmulticam', 'Camarasenmulticam', 'Camcount']
RESW_CANDS = ['Resw', 'ResW']
RESH_CANDS = ['Resh', 'ResH']
# ------------------------------------------------------------------


def _proj_folder():
    return td.project.folder.replace('\\', '/')


def _find_par(comp, cands):
    for n in cands:
        if hasattr(comp.par, n):
            return getattr(comp.par, n)
    return None


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


def _add_float(page, name, default, rng):
    p = page.appendFloat(name, label=name)[0]
    p.default, p.val = float(default), float(default)
    if rng:
        p.normMin, p.normMax = rng
    return p


def _add_rgba(page, name, default=(0.0, 0.0, 0.0, 1.0)):
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


def build(scene):
    prev = scene.op(LAYOUT_NAME)
    if prev is not None:
        try: prev.destroy()
        except Exception: pass

    layout = scene.create(baseCOMP, LAYOUT_NAME)
    layout.nodeX, layout.nodeY = 0, -550

    # cam selects -> CAM_1..N de escena_modular
    selects = []
    for i in range(NUM_CAMS):
        sel = layout.create(selectTOP, f'cam_in_{i+1}')
        cam_name = f'CAM_{i+1}' if scene.op(f'CAM_{i+1}') else f'Cam_{i+1}'
        sel.par.top = f'{scene.path}/{cam_name}'
        sel.nodeX, sel.nodeY = -500, -i * 130
        selects.append(sel)

    # audio_in dentro del layout (mismo contrato)
    audio = layout.create(selectCHOP, 'audio_in')
    _set_par_any(audio, (('chop', f'{scene.path}/audio_in', 'val'),
                         ('chopop', f'{scene.path}/audio_in', 'val')))
    _set_par_any(audio, (('channames', 'low mid high', 'val'),
                         ('channelnames', 'low mid high', 'val')))
    audio.nodeX, audio.nodeY = -500, 300

    # shader DAT
    shader_abs = f'{_proj_folder()}/{SHADER_RELDIR}/{SHADER_FILE}'
    dat = layout.create(td.textDAT, 'pixel_dat')
    dat.par.file = shader_abs
    if hasattr(dat.par, 'syncfile'):
        dat.par.syncfile = True
    try: dat.par.loadonstartpulse.pulse()
    except Exception: pass
    dat.nodeX, dat.nodeY = -500, -750

    # GLSL Multi TOP
    glsl = layout.create(glslmultiTOP, 'glsl_layout')
    glsl.par.pixeldat = dat.name
    _set_par_any(glsl, (('outputresolution', 'custom', 'val'),))
    rw = _find_par(scene, RESW_CANDS)
    rh = _find_par(scene, RESH_CANDS)
    for axis, rp in (('w', rw), ('h', rh)):
        gp = getattr(glsl.par, f'resolution{axis}', None)
        if gp is not None and rp is not None:
            gp.expr = f"op('{scene.path}').par.{rp.name}"
            try: gp.mode = ParMode.EXPRESSION
            except Exception: pass
    glsl.nodeX, glsl.nodeY = 0, -300
    for i, sel in enumerate(selects):
        try: glsl.inputConnectors[i].connect(sel)
        except Exception as e: print(f'[warn] input {i}: {e}')

    # pagina Layout: 5 macros + Bypass
    page = layout.appendCustomPage('Layout')
    for (slot, role, uniform, par_name, default, rng) in FIVE_SLOTS:
        if default is None and rng is None:
            _add_rgba(page, par_name)
        else:
            _add_float(page, par_name, default, rng)
    _add_toggle(page, 'Bypass', default=False)

    # pagina Audio
    apage = layout.appendCustomPage('Audio')
    _add_toggle(apage, 'Audioreact', default=False)
    _add_toggle(apage, 'Low',  default=True)
    _add_toggle(apage, 'Mid',  default=False)
    _add_toggle(apage, 'High', default=False)
    slot_names = [s[3] for s in FIVE_SLOTS]
    _add_menu(apage, 'Audiotarget', slot_names, slot_names, default_index=0)
    _add_float(apage, 'Audiomult', 1.0, (0.0, 3.0))

    # uniforms: comunes de layout + macros
    cc = _find_par(scene, CAMCOUNT_CANDS)
    cc_expr = f"op('{scene.path}').par.{cc.name}" if cc else str(NUM_CAMS)
    rw_expr = f"op('{scene.path}').par.{rw.name}" if rw else '1920'
    rh_expr = f"op('{scene.path}').par.{rh.name}" if rh else '1080'

    total = 3 + len(FIVE_SLOTS) + 2
    _ensure_vec_rows(glsl, total + 1)
    vslot = 0
    _bind_uniform(glsl, 'uTime', 'absTime.seconds', vslot); vslot += 1
    _bind_uniform(glsl, 'uResolution', (rw_expr, rh_expr), vslot); vslot += 1
    _bind_uniform(glsl, 'uCamCount', cc_expr, vslot); vslot += 1
    for (slot_index, role, uniform, par_name, default, rng) in FIVE_SLOTS:
        if default is None and rng is None:
            _bind_uniform(glsl, uniform,
                          (f'parent().par.{par_name}r', f'parent().par.{par_name}g',
                           f'parent().par.{par_name}b'), vslot)
        else:
            _bind_uniform(glsl, uniform, _slot_driven_expr(slot_index, par_name, rng), vslot, owner=layout)
        vslot += 1
    # uCamfit / uCamAspect comunes (si el shader los usa)
    camfit = _find_par(scene, ['Camfit'])
    if camfit is not None:
        _bind_uniform(glsl, 'uCamfit', f"op('{scene.path}').par.{camfit.name}", vslot); vslot += 1
    _bind_uniform(glsl, 'uCamAspect', '16.0/9.0', vslot); vslot += 1

    out = layout.create(outTOP, 'out1')
    out.inputConnectors[0].connect(glsl)
    out.nodeX, out.nodeY = 400, -300

    print(f'[ok] {layout.path} creado — {LAYOUT_NAME} ({NUM_CAMS} camaras)')
    print(f'     5 macros: ' + ', '.join(s[3] for s in FIVE_SLOTS) + ' + Bypass + Audio')
    print('PASOS MANUALES:')
    print(f'  1. Conectar {layout.name}/out1 al switch de layouts de base17.')
    print(f'  2. Agregar "{LAYOUT_NAME}" al menu Modelayout (mismo orden que el switch).')


def run():
    scene = td.op(SCENE_PATH)
    if scene is None:
        print(f'[error] no existe {SCENE_PATH}')
        return
    build(scene)


run()
