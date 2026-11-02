# ─────────────────────────────────────────────────────────────
# build_all.py — construye TODAS las bases (visuales, efectos) y luego las herramientas del show.
#
# Uso: Text DAT con File = builders/build_all.py → clic derecho → Run Script.
# Cada builder es idempotente: re-ejecutar este script es seguro (conserva sliders/MIDI).
# Si un builder falla, se reporta y se sigue con los demás.
# ─────────────────────────────────────────────────────────────
import glob, os, traceback

HERE = project.folder + '/builders'


def _by_base(paths):
    return sorted(paths, key=lambda p: int(os.path.basename(p).split('_')[1].replace('base', '')))


BUILDERS = _by_base(glob.glob(HERE + '/visuales/setup_base*.py'))
BUILDERS += _by_base(glob.glob(HERE + '/efectos/setup_base*.py'))
# herramientas propias del show (si existen): salidas a Resolume, previz…
for tool in ('setup_salidas.py', 'setup_previz.py'):
    if os.path.exists(HERE + '/herramientas/' + tool):
        BUILDERS.append(HERE + '/herramientas/' + tool)


def run():
    ok, failed = [], []
    for path in BUILDERS:
        name = os.path.basename(path)
        print('[build_all] ── %s' % name)
        try:
            with open(path, encoding='utf-8') as f:
                code = compile(f.read(), path, 'exec')
            exec(code, dict(globals(), __file__=path, __name__='__tdvj_builder__'))
            ok.append(name)
        except Exception:
            traceback.print_exc()
            failed.append(name)
    print('[build_all] listos: %d · fallaron: %d %s' % (len(ok), len(failed), failed if failed else ''))

run()
