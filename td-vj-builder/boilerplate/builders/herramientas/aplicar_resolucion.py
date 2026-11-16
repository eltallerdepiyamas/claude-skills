# ─────────────────────────────────────────────────────────────
# aplicar_resolucion.py — UNA resolución para todo el show.
#
# La resolución MAESTRA vive en el hub /project2/show → pestaña Resolucion (W / H). Este script liga a ella:
#   - layouts (layout_*): ya la siguen solos (layout_core), aquí solo se revisa
#   - visuales y FX (baseN → Salida → Resw / Resh): expresión a la maestra
#   - salidas finales de /project2 (fit1, fit2... los Fit TOP de arriba): resolución custom = maestra
# Después basta con cambiar la maestra: todo se ajusta en vivo. La grabación (REC) sigue a lo que graba.
#
# W, H = None  → solo liga (no cambia la maestra).  W, H = 3840, 2160 → pone esa maestra y liga todo.
# Una base que quieras distinta: escríbele su número a mano en Salida (deja de seguir); correr esto la
# vuelve a ligar, salvo que la pongas en SUELTAS.
#
# Textport:  exec(open(project.folder + '/builders/herramientas/aplicar_resolucion.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core
importlib.reload(tdvj_core)

W, H = None, None          # p. ej. 1920, 1080 · 3840, 2160 · 1080, 1920 (vertical)
SUELTAS = []               # bases que conservan su propia resolución, p. ej. ['base3']
NO_TOCAR = ('/project2/_respaldo', '/project2/ui_perform', '/project2/td_mcp', '/project2/audio')   # UI y herramientas: su tamano es propio
SALIDAS = 'fit'            # prefijo de los TOPs de salida en /project2 que siguen a la maestra


def run():
    m = tdvj_core.master_res_pars()
    if m is None:
        print('[error] no encuentro la resolucion maestra (/project2/show → Resolucion: W / H)')
        return
    rw, rh = m
    if W and H:
        rw.val, rh.val = int(W), int(H)
    ew, eh = tdvj_core.master_res_exprs()
    print('Resolucion maestra: %d x %d  (%s / %s)' % (rw.eval(), rh.eval(), rw.name, rh.name))

    bases = []
    for n in tdvj_core.VISUAL_BASES + tdvj_core.EFFECT_BASES:
        try:
            comp = tdvj_core.find_base('base%d' % n)
        except ValueError:
            continue
        if getattr(comp.par, 'Resw', None) is None or comp.name in SUELTAS:
            continue
        comp.par.Resw.expr, comp.par.Resh.expr = ew, eh
        bases.append(comp.name)
    print('  bases ligadas:', ', '.join(bases) or '(ninguna construida)')

    scene = op(tdvj_core.ESCENA)             # sin escena_modular (solo visuales) no hay layouts
    lay = [c for c in scene.children if c.name.startswith('layout_')] if scene is not None else []
    sueltos = []
    for c in lay:
        g = c.op('glsl_layout')
        if g is not None and g.par.resolutionw.mode.name != 'EXPRESSION':
            sueltos.append(c.name)
    print('  layouts: %d siguen a la maestra%s' % (len(lay) - len(sueltos),
          ('; NO la siguen (vuelve a correr su builder): ' + ', '.join(sueltos)) if sueltos else ''))

    outs = []
    for t in op(tdvj_core.ROOT).children:
        if t.name.startswith(SALIDAS) and t.OPType == 'fitTOP':
            t.par.outputresolution = 'custom'
            t.par.resolutionw.expr, t.par.resolutionh.expr = ew, eh
            outs.append(t.name)
    print('  salidas ligadas:', ', '.join(outs) or '(no encontre Fit TOPs %s* en %s)' % (SALIDAS, tdvj_core.ROOT))


    # TOPs sueltos con la resolucion de fabrica escrita a mano (negros de camara, fits, stock): a la maestra
    fijos = []
    for raiz in ('/project1', tdvj_core.ROOT):
        if op(raiz) is None:
            continue
        for t in op(raiz).findChildren(type=TOP):
            if t.path.startswith(NO_TOCAR) or getattr(t.par, 'outputresolution', None) is None:
                continue
            if t.par.outputresolution.eval() != 'custom' or t.par.resolutionw.mode.name != 'CONSTANT':
                continue
            if (int(t.par.resolutionw.eval()), int(t.par.resolutionh.eval())) == tuple(tdvj_core.DEFAULT_RES):
                t.par.resolutionw.expr, t.par.resolutionh.expr = ew, eh
                fijos.append(t.path)
    print('  TOPs fijos en %dx%d ligados:' % tuple(tdvj_core.DEFAULT_RES), ', '.join(fijos) or '(ninguno)')


run()
