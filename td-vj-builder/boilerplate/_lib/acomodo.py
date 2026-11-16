"""
acomodo.py — regla unica de acomodo del INTERIOR de cualquier COMP (visual, FX, escena).
SOLO mueve y pone recuadros: no conecta, no borra, no cambia parametros ni colores.

  · Nunca se mezclan tipos de nodo: un bloque por tipo, de ARRIBA a ABAJO: TOP · CHOP · SOP · MAT · COMP · DAT.
  · Dentro de cada bloque la senal va de izquierda a derecha (una columna por paso de la cadena).
  · Lo que alimenta a un mismo nodo (o va en paralelo) se apila en UNA columna hacia abajo.
  · Nada encimado: cada columna y cada fila se abren segun el nodo mas grande que tengan.

  interior(comp)          -> acomoda lo que hay dentro de comp. Lo llaman build_visual / build_effect / build_layout.
  posiciones(comp)        -> {ruta: [x, y]} para respaldar antes de mover.
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass

DX, DY, GAP = 220, 150, 320
TIPOS = ('TOP', 'CHOP', 'SOP', 'MAT', 'COMP', 'DAT')
TITULOS = {'TOP': 'TOP  ·  imagen', 'CHOP': 'CHOP  ·  audio y control', 'SOP': 'SOP', 'MAT': 'MAT',
           'COMP': 'COMP', 'DAT': 'DAT  ·  shaders y scripts'}
GRIS = (0.45, 0.45, 0.45)


def tipo(o):
    return TIPOS.index(o.family) if o.family in TIPOS else len(TIPOS)


def posiciones(comp):
    return {o.path: [o.nodeX, o.nodeY] for o in comp.children}


def _caja(comp, clave, titulo, x0, ytop, x1, ybot):
    name = 'zona_' + clave.lower()
    a = comp.op(name)
    if a is None:
        a = comp.create(annotateCOMP)
        a.name = name                       # create() ignora el nombre en los annotate
    a.nodeX, a.nodeY = x0 - 80, ybot - 90
    a.nodeWidth, a.nodeHeight = (x1 - x0) + 160, (ytop - ybot) + 240
    a.par.Titletext = titulo
    a.par.Backcolorr, a.par.Backcolorg, a.par.Backcolorb = [c * 0.35 for c in GRIS]
    a.par.Backcoloralpha = 0.22


def _columnas(ops):
    """Reparte un grupo del mismo tipo en columnas siguiendo los cables: fuentes a la izquierda."""
    paths = {o.path for o in ops}
    prof = {}

    def p(o, pila=()):
        if o.path in prof:
            return prof[o.path]
        if o.path in pila:                  # lazo (feedback): no cuenta
            return 0
        ins = [i for i in o.inputs if i is not None and i.path in paths]
        prof[o.path] = (1 + max(p(i, pila + (o.path,)) for i in ins)) if ins else 0
        return prof[o.path]

    cols = {}
    for o in ops:
        cols.setdefault(p(o), []).append(o)
    orden = {}                              # fila ya asignada, para que cada nodo quede cerca de quien lo alimenta
    out = []
    for k in sorted(cols):
        def clave(o):
            filas = [orden[i.path] for i in o.inputs if i is not None and i.path in orden]
            return (min(filas) if filas else 999, o.name)
        col = sorted(cols[k], key=clave)
        for j, o in enumerate(col):
            orden[o.path] = j
        out.append(col)
    return out


def interior(comp, caja=True):
    """Acomoda el interior de comp. Devuelve cuantos nodos movio."""
    if comp is None or not hasattr(comp, 'children'):
        return 0
    for a in [o for o in comp.children if o.OPType == 'annotateCOMP' and o.name.startswith('zona_')]:
        a.destroy()
    kids = [o for o in comp.children if o.OPType != 'annotateCOMP']
    y, n = 0, 0
    for t in range(len(TIPOS) + 1):
        ops = [o for o in kids if tipo(o) == t]
        if not ops:
            continue
        alto_fila = max(DY, max(o.nodeHeight for o in ops) + 60)
        x, ybot = 0, y
        for col in _columnas(ops):
            for j, o in enumerate(col):
                o.nodeX, o.nodeY = x, y - j * alto_fila
                n += 1
            ybot = min(ybot, y - (len(col) - 1) * alto_fila)
            x += max(DX, max(o.nodeWidth for o in col) + 90)
        if caja:
            nombre = TIPOS[t] if t < len(TIPOS) else 'OTROS'
            _caja(comp, nombre, TITULOS.get(nombre, nombre), 0, y, x, ybot)
        y = ybot - alto_fila - GAP
    return n
