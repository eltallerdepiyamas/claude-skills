# =============================================================
# buscar_script_viejo.py  —  encuentra el script viejo de LJ que rehace las pestanas de escena_modular
#
# Sintoma: vuelven las pestanas Gridwall / Pip / Splitasim... y desaparece "Escena activa" (Modoescena).
# Lo hace un DAT que vino en el .toe de LJ (imprime "TODOS los layouts listos ... switch_FINAL") y que
# probablemente corre solo al abrir el .toe (Execute DAT con Start).
#
#   exec(...)                 -> SOLO busca e imprime los DATs sospechosos
#   APPLY = True; exec(...)   -> los saca del camino: Execute DAT -> Active off; Text DAT -> se copia a
#                                /project2/_respaldo/scripts_viejos y se quita (no se borra nada).
# Uso (Textport):
#   exec(open(project.folder + '/control/escena_modular/buscar_script_viejo.py', encoding='utf-8').read())
# =============================================================

MARCAS = ('TODOS los layouts', 'switch_FINAL', '_expose_to_scene', 'setup_all_layouts', 'Escenaactiva')
PROPIOS = ('/control/', '/builders/', '/_lib/')   # DATs que leen archivos de este show: no se tocan

try:
    APPLY
except NameError:
    APPLY = False


def _respaldo():
    root = op('/project2/_respaldo') or op('/project2').create(baseCOMP, '_respaldo')
    return root.op('scripts_viejos') or root.create(baseCOMP, 'scripts_viejos')


def _file(d):
    f = getattr(d.par, 'file', None)
    return str(f.eval()).replace('\\', '/') if f is not None else ''


def run():
    print('MODO:', 'DESACTIVAR' if APPLY else 'SOLO BUSCAR (no cambia nada)')
    hits = 0
    for root in (op('/project1'), op('/project2')):
        for d in root.findChildren(type=DAT, depth=None):
            if d.path.startswith('/project2/_respaldo') or any(s in _file(d) for s in PROPIOS):
                continue
            try:
                txt = d.text
            except Exception:
                continue
            found = [m for m in MARCAS if m in txt]
            if not found:
                continue
            hits += 1
            start = getattr(d.par, 'start', None)
            info = ' · corre al abrir el .toe (Start on)' if start is not None and start.eval() else ''
            print('   %-60s [%s] %s%s' % (d.path, d.OPType, ', '.join(found), info))
            if APPLY:
                if d.OPType in ('executeDAT', 'chopexecuteDAT', 'datexecuteDAT', 'parameterexecuteDAT',
                                'opexecuteDAT', 'panelexecuteDAT') and hasattr(d.par, 'active'):
                    d.par.active = False
                    print('      -> desactivado (Active off)')
                else:
                    # un Text DAT se corre con Run Script aunque este en Bypass: se manda al respaldo
                    dest = _respaldo()
                    old = dest.op(d.name)
                    if old is not None:
                        old.destroy()
                    dest.copyOPs([d])
                    d.destroy()
                    print('      -> movido a %s' % dest.path)
    print('[ok] %d sospechosos%s' % (hits, '' if APPLY or not hits else ' · para desactivarlos: APPLY = True; exec(...)'))


run()
APPLY = False
