# ─────────────────────────────────────────────────────────────
# limpiar_bases.py — quita de cada baseX lo que quedó de proyectos anteriores.
# Correr UNA vez, ANTES de build_all.py.
#
# Por base (1–24, 38–45):
#   - Páginas custom: si la base tiene builder en este proyecto se quedan solo Visual / Filter / Audio /
#     Salida / Secuencia (build_all limpia lo viejo DENTRO de esas). Si no tiene builder, se quitan todas.
#   - Nodos sin tag 'tdvj' (lo del show anterior: escena_modular, cámaras, GLSLs viejos…) NO se borran:
#     se MUEVEN a /project2/_respaldo/baseN. Si algo hacía falta, se copia de ahí de regreso.
#   - Nodos 'tdvj' en bases SIN builder (p.ej. base19, que tuvo un visual de prueba) se borran:
#     se regeneran con su builder si algún día vuelven.
#   - Siempre se quedan: out1, el Text DAT de un builder y cualquier nodo con tag 'mio'.
#   - Los valores de las páginas quitadas se pierden (eran del show anterior).
#
# Uso: Text DAT con File = este .py → Run Script. Textport: [tdvj] lo hecho, [WARN] lo que no se pudo.
# ─────────────────────────────────────────────────────────────
import sys, importlib, glob, os
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core
importlib.reload(tdvj_core)

BASES = tdvj_core.VISUAL_BASES + tdvj_core.EFFECT_BASES
KEEP_PAGES = {'Visual', 'Filter', 'Audio', 'Salida', 'Secuencia'}
KEEP_NAMES = {'out1'}
KEEP_TAG = 'mio'
RESPALDO = tdvj_core.ROOT + '/_respaldo'


def _with_builder():
    nums = set()
    for path in glob.glob(project.folder + '/builders/*/setup_base*.py'):
        try:
            nums.add(int(os.path.basename(path).split('_')[1].replace('base', '')))
        except ValueError:
            pass
    return nums


def _is_builder_dat(o):
    f = getattr(o.par, 'file', None) if o.family == 'DAT' else None
    return f is not None and '/builders/' in str(f.eval()).replace('\\', '/')


def _keep(o):
    return (o.name in KEEP_NAMES or KEEP_TAG in o.tags or _is_builder_dat(o)
            or o == me or o.path == me.path)


def _backup_comp(n):
    root = tdvj_core.ensure_comp(tdvj_core.ROOT, '_respaldo', x=-1200, y=-1200)
    b = root.op('base%d' % n)
    if b is None:
        b = root.create(baseCOMP, 'base%d' % n)
        b.nodeX, b.nodeY = (n % 8) * 200, -(n // 8) * 200
    return b


def limpiar(n, has_builder):
    try:
        comp = tdvj_core.find_base('base%d' % n)
    except ValueError:
        return None
    pages, moved, dropped = [], [], []

    for pg in list(comp.customPages):
        if has_builder and pg.name in KEEP_PAGES:
            continue
        name = pg.name
        try:
            pg.destroy()
            pages.append(name)
        except Exception as e:
            tdvj_core.warn('base%d: no pude quitar la página %s (%s)' % (n, name, e))

    kids = [c for c in comp.children if c.valid and getattr(c, 'dock', None) is None and not _keep(c)]
    managed = [c for c in kids if tdvj_core.TAG in c.tags]
    old = [c for c in kids if tdvj_core.TAG not in c.tags]

    if not has_builder:                       # regenerables: fuera
        for c in managed:
            if c.valid:
                dropped.append(c.name)
                c.destroy()

    if old:
        try:
            _backup_comp(n).copyOPs(old)       # mover = copiar al respaldo (con sus cables) + quitar
            for c in old:
                if c.valid:
                    moved.append(c.name)
                    c.destroy()
        except Exception as e:
            tdvj_core.warn('base%d: no pude respaldar %s (%s) — no se tocó nada' % (n, [c.name for c in old], e))

    if pages or moved or dropped:
        tdvj_core.log('base%d%s: páginas quitadas %s · al respaldo %s · borrados %s' % (
            n, '' if has_builder else ' (sin builder)', pages or '-', moved or '-', dropped or '-'))
    return comp


def run():
    built = _with_builder()
    touched = 0
    for n in BASES:
        if limpiar(n, n in built) is not None:
            touched += 1
    tdvj_core.refresh_salidas()
    tdvj_core.log('limpieza lista (%d bases revisadas). Respaldo en %s. Ahora corre build_all.py' % (touched, RESPALDO))

run()
