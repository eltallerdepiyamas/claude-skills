# =============================================================
# ordenar_escena.py  —  deja escena_modular legible: pestanas en orden de uso, nombres y etiquetas claras
#
# Solo cambia NOMBRES DE PESTANA, ORDEN y ETIQUETAS (lo que se lee en el panel). Los nombres internos
# de los parametros (Modoescena, Int, Slot1...) no cambian: OSC, Companion, faders y layouts siguen igual.
# Al final imprime el panel tal como queda.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/escena_modular/ordenar_escena.py', encoding='utf-8').read())
# Se puede volver a correr.
# =============================================================

import re

SCENE_PATH = '/project2/base17/escena_modular'

# pestana vieja -> nueva, en el orden en que se usan en vivo
PAGES = [('Escena_Master', 'Escena'), ('Escena', 'Escena'),
         ('Camaras', 'Camaras'), ('Slots', 'Slots'),
         ('Resolucion', 'Resolucion'), ('Audio', 'Audio')]

# parametro -> etiqueta en el panel
LABELS = {
    'Modoescena': 'Escena activa',
    'Int':        'Camaras en multicam',
    'Menu2':      'Camara unica',
    'Camfit':     'Ajuste (Fill / Fit / Stretch)',
    'Slot1':      'Lugar 1',
    'Slot2':      'Lugar 2',
    'Slot3':      'Lugar 3',
    'Slot4':      'Lugar 4',
    'Slot5':      'Lugar 5',
}


# parametros que ya no se usan: se borran solo si nada vivo los lee
#   Index (camara hero): el hero ahora es la camara del Lugar 1 (pestana Slots)
REMOVE = ['Index']

# etiquetas por posicion en la pestana (sus nombres internos varian entre versiones del rig: W/H, Resw/Resh...)
PAGE_LABELS = {
    'Resolucion': ['Ancho (px)', 'Alto (px)'],
    'Audio':      ['Multiplicador de audio'],
}


def _users(name):
    pat = re.compile(r'par\.%s\b' % name)
    out = []
    for o in op('/project2').findChildren(depth=None):
        if o.path.startswith('/project2/_respaldo'):
            continue
        for p in o.pars():
            t = p.expr if p.mode == ParMode.EXPRESSION else p.bindExpr if p.mode == ParMode.BIND else ''
            if t and pat.search(t):
                out.append('%s.%s' % (o.path, p.name))
    return out


def _show(p):
    if p.isMenu:
        return p.menuLabels[p.menuIndex] if p.menuLabels else p.eval()
    v = p.eval()
    return ('%g' % v) if isinstance(v, float) else v


def run():
    m = op(SCENE_PATH)
    for name in REMOVE:
        p = getattr(m.par, name, None)
        if p is None:
            continue
        users = _users(name)
        if users:
            print('[aviso] %s no se borra, lo usan: %s' % (name, ', '.join(users[:5])))
        else:
            p.destroy()
            print('[ok] %s borrado (ya nadie lo usaba)' % name)
    pages = {pg.name: pg for pg in m.customPages}
    order = []
    for old, new in PAGES:
        pg = pages.get(old)
        if pg is None or new in order:
            continue
        if old != new and new not in pages:
            try:
                pg.name = new
            except Exception as e:
                print('[aviso] no pude renombrar la pestana %s: %s' % (old, e))
                new = old
        order.append(new)
    extra = [pg.name for pg in m.customPages if pg.name not in order]
    try:
        m.sortCustomPages(*(order + extra))
    except Exception as e:
        print('[aviso] no pude ordenar las pestanas: %s' % e)

    for name, label in LABELS.items():
        p = getattr(m.par, name, None)
        if p is not None:
            p.label = label
    for pg in m.customPages:
        # encabezados decorativos viejos (p. ej. "HERO CAMARA CENTRAL"): no son controles
        for p in [q for q in pg.pars if q.style == 'Header']:
            print('[ok] encabezado quitado: %s' % p.label)
            p.destroy()
        labels = PAGE_LABELS.get(pg.name)
        if labels:
            heads, seen = [], set()           # por nombre: comparar Par en TD compara su valor
            for p in pg.pars:
                if p.tuplet[0].name not in seen:
                    seen.add(p.tuplet[0].name)
                    heads.append(p.tuplet[0])
            for p, label in zip(heads, labels):
                p.label = label

    print('escena_modular:')
    for pg in m.customPages:
        print('   [%s]' % pg.name)
        seen = set()
        for p in pg.pars:
            if p.tuplet[0].name in seen:          # colores / XY: una linea por grupo
                continue
            seen.add(p.tuplet[0].name)
            print('      %-30s %s' % (p.label, _show(p)))
    if extra:
        print('   (sin orden fijo: %s)' % ', '.join(extra))


run()
