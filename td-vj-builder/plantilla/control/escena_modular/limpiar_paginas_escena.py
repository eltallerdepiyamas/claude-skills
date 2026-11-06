# =============================================================
# limpiar_paginas_escena.py  —  quita de escena_modular las pestanas de layouts viejos
#
# Se quedan las pestanas globales (KEEP: Escena, Audio, Resolucion, Camaras, Slots).
# Las demas eran los parametros de cada layout de LJ expuestos en escena_modular; esos layouts
# ya estan en /project2/_respaldo. Los layouts nuevos tienen sus parametros en su propia pagina Layout.
# Una pestana cuyos parametros sigue leyendo algo vivo (fuera de _respaldo) NO se quita: se avisa.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/escena_modular/limpiar_paginas_escena.py', encoding='utf-8').read())
#       -> solo revisa e imprime
#   APPLY = True; exec(...)   -> quita las pestanas marcadas "se va"
#   APPLY = True; FORCE = ['Gridwall']; exec(...)   -> quita tambien esa aunque alguien la use
#   (cada pestana en uso lista quien la usa: revisa que sea algo viejo antes de forzar)
# =============================================================

import re

SCENE_PATH = '/project2/base17/escena_modular'
KEEP = ('esce', 'audi', 'reso', 'cam', 'slot')     # prefijos (minusculas) de las pestanas que se quedan

try:
    APPLY
except NameError:
    APPLY = False
try:
    FORCE             # pestanas que se quitan aunque alguien las use, p. ej. FORCE = ['Gridwall']
except NameError:
    FORCE = []


def _refs(scene):
    """Textos de expresiones / binds vivos fuera de _respaldo (para saber que parametros se usan)."""
    out = []
    for o in op('/project2').findChildren(depth=None):
        if o.path.startswith('/project2/_respaldo'):
            continue
        for p in o.pars():
            if p.mode == ParMode.EXPRESSION and p.expr:
                out.append((o, p.expr))
            elif p.mode == ParMode.BIND and p.bindExpr:
                out.append((o, p.bindExpr))
    return out


def run():
    m = op(SCENE_PATH)
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    refs = _refs(m)
    gone = 0
    for pg in list(m.customPages):
        keep = pg.name.lower().startswith(KEEP)
        names = [p.name for p in pg.pars]
        # usado = lo nombra una expresion/bind viva de otro operador (las de escena_modular mismo,
        # p. ej. los "Escena activa" de cada pestana, no cuentan)
        users = sorted({(n, o.path) for n in names for o, t in refs
                        if o is not m and re.search(r'par\.%s\b' % n, t)})
        if keep:
            state = 'se queda'
        elif users and pg.name not in FORCE:
            state = '[!] se queda: la usan otros operadores'
        else:
            state = 'se va'
        print('   %-18s %3d params  %s' % (pg.name, len(names), state))
        for n, path in users[:8]:
            print('        %-20s <- %s' % (n, path.replace(m.path + '/', '')))
        if APPLY and state == 'se va':
            pg.destroy()
            gone += 1
    if APPLY:
        print('[ok] %d pestanas quitadas' % gone)


run()
APPLY = False
FORCE = []
