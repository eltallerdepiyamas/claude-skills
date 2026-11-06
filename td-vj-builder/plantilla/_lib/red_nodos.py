"""red_nodos.py: construye visuales como redes de nodos dentro de una base (no solo shaders).

    b, r = red_nodos.base(n)                     # base prendida, con COMP 'red' limpio
    logo = red_nodos.logo(r)                     # entrada de logo fit a 1080p
    x = red_nodos.nodo(r, td.levelTOP, 'nivel', [logo], opacity=0.9)
    fuente = red_nodos.salida(r, x)              # out1 de la red; pasar a build_visual(source=fuente)

Valores: un str que empieza con '=' es expresion. Audio: audio(r) deja math_low / mid / high / kick en la red.
Los controles se ligan con expresiones a parent(2).par.<Slot>.
"""
import td


def base(n):
    b = td.op('/project2/base%d' % n)
    b.allowCooking = True
    r = b.op('red')
    if r is not None:
        r.destroy()
    return b, b.create(td.baseCOMP, 'red')


def nodo(r, tipo, nombre, entradas=(), **pars):
    o = r.create(tipo, nombre)
    o.nodeX, o.nodeY = len(r.children) * 180, 0
    for i, e in enumerate(entradas):
        o.inputConnectors[i].connect(e)
    for k, v in pars.items():
        p = getattr(o.par, k)
        if isinstance(v, str) and v.startswith('='):
            p.expr = v[1:]
        else:
            p.val = v
    return o


def audio(r):
    s = nodo(r, td.selectCHOP, 'audio', chop='/project2/audio/master_audio', channames='low mid high kick')
    return s


def logo(r, archivo='assets/logo_murcielago.png'):
    m = nodo(r, td.moviefileinTOP, 'logo_in', file=archivo)
    return nodo(r, td.fitTOP, 'logo', [m], outputresolution='custom', resolutionw=1920, resolutionh=1080, fit='fitbest')


def salida(r, x):
    o = nodo(r, td.outTOP, 'out1', [x])
    return o.path
