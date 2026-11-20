# ledfx_comun.py — lo que comparten los efectos de la SEGUNDA CAPA (ledfx_*): donde van, paginas y registro.
# Los instaladores lo cargan con: exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
#   host() -> (COMP, 'slices' | 'led'): /project1/slices (led_slices) si existe; si no la LED (led_salida).
#            proyecto.json -> "ledfx": {"en": "led"} lo fuerza a la LED.
#   par(H, pg, tipo, nombre, etiqueta, default, rango)  ·  menu(H, pg, nombre, etiqueta, nombres, etiquetas, default)
#   tinta_exprs(g, vec, par_menu) -> la tinta A / B de la paleta del show o blanco en vecN (xyz)
#   registrar(H, g, orden, on_par, var_par, nombre) -> tag ledfx, orden, encadena y avisa a auto_capa
import json

SHOW = '/project2/show'


def host():
    try:
        pref = json.load(open(project.folder + '/proyecto.json', encoding='utf-8')).get('ledfx', {}).get('en', '')
    except Exception:
        pref = ''
    S_, L_ = op('/project1/slices'), op('/project1/led')
    s_ok = S_ is not None and S_.op('slices_cadena') is not None
    l_ok = L_ is not None and L_.op('led_cadena') is not None
    if pref == 'led' and l_ok:
        return L_, 'led'
    if s_ok:
        return S_, 'slices'
    if l_ok:
        return L_, 'led'
    return None, ''


def nuevo(H, tipo, nombre, x, y):
    o = H.op(nombre) or H.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def pagina(H, nombre):
    return next((p for p in H.customPages if p.name == nombre), None) or H.appendCustomPage(nombre)


def par(H, pg, tipo, nombre, etiqueta, default=None, rango=None):
    if not hasattr(H.par, nombre):
        getattr(pg, 'append' + tipo)(nombre, label=etiqueta)
        p = getattr(H.par, nombre)
        if default is not None:
            p.default = default
            p.val = default
    p = getattr(H.par, nombre)
    p.label = etiqueta
    if rango:
        p.normMin, p.normMax = rango
    return p


def menu(H, pg, nombre, etiqueta, nombres, etiquetas, default):
    if not hasattr(H.par, nombre):
        pg.appendMenu(nombre, label=etiqueta)
        getattr(H.par, nombre).default = default
    p = getattr(H.par, nombre)
    v = p.eval()                                  # cambiar menuNames mueve el valor: se guarda y se regresa
    p.menuNames, p.menuLabels = nombres, etiquetas
    p.val = v if v in nombres else default
    return p


def tinta_exprs(g, vec, par_menu):
    for c, k in (('r', 'x'), ('g', 'y'), ('b', 'z')):
        getattr(g.par, '%svalue%s' % (vec, k)).expr = (
            "[op('%s').par.Colora%s, op('%s').par.Colorb%s, 1.0][parent().par.%s.menuIndex] "
            "if hasattr(op('%s').par, 'Colora%s') else 1.0" % (SHOW, c, SHOW, c, par_menu, SHOW, c))


def registrar(H, g, orden, on_par, var_par, nombre):
    g.tags.add('ledfx')
    g.store('orden', orden)
    g.store('on_par', on_par)
    g.store('var_par', var_par)
    g.store('nombre', nombre)
    cad = H.op('slices_cadena') or H.op('led_cadena')
    cadena = cad.module.encadenar() if cad is not None else []
    if H.op('capa_lib') is not None:              # auto_capa instalado: que lo conozca (su pagina Capa)
        p = project.folder + '/modulos/auto_capa/instalar.py'
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
    return cadena
