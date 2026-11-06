# ─────────────────────────────────────────────────────────────
# aplicar_resolucion.py — UNA resolución para todo el show.
#
# La resolución MAESTRA vive en escena_modular → pestaña Resolucion. Este script liga a ella:
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
SALIDAS = 'fit'            # prefijo de los TOPs de salida en /project2 que siguen a la maestra


def run():
    m = tdvj_core.master_res_pars()
    if m is None:
        print('[error] escena_modular no tiene pestaña Resolucion con ancho y alto')
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

    scene = rw.owner
    lay = [c for c in scene.children if c.name.startswith('layout_')]
    sueltos = []
    for c in lay:
        g = c.op('glsl_layout')
        if g is not None and rw.name not in (g.par.resolutionw.expr or ''):
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


run()
