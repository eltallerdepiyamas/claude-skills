# ─────────────────────────────────────────────────────────────
# aplicar_resolucion.py — pone la misma resolución (Salida → Resw/Resh) en todas las bases
# construidas. Cada base sigue teniendo la suya: después puedes cambiar una sola a mano.
#
# Uso: ajusta W/H (y BASES si quieres solo algunas) → Text DAT con File = este .py → Run Script.
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core
importlib.reload(tdvj_core)

W, H = 1920, 1080
BASES = tdvj_core.VISUAL_BASES + tdvj_core.EFFECT_BASES   # o p.ej. [1, 2]


def run():
    done = []
    for n in BASES:
        name = 'base%d' % n
        try:
            comp = tdvj_core.find_base(name)
        except ValueError:
            continue
        if getattr(comp.par, 'Resw', None) is None:
            continue   # base sin construir con tdvj_core
        comp.par.Resw = W
        comp.par.Resh = H
        done.append(name)
    tdvj_core.log('resolución %dx%d en: %s' % (W, H, ', '.join(done) or '(ninguna)'))

run()
