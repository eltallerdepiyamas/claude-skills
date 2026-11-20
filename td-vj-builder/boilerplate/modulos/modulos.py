# modulos.py — gestor de modulos del boilerplate (piezas que se agregan a un show solo si se usan).
# Cada modulo es una carpeta en modulos/ con modulo.json (nombre, requiere, detecta, ui), instalar.py y LEEME.md.
#
# Desde el Textport o el MCP (correr este archivo), cambiando ACCION y NOMBRES:
#   ACCION = 'lista'      -> catalogo: que hay, version, si esta instalado en este .toe
#   ACCION = 'instalar'   -> instala NOMBRES con sus dependencias (idempotente: re-instalar = actualizar)
#   ACCION = 'proyecto'   -> instala lo que proyecto.json -> "modulos" tenga en true (armar.py lo usa)
#   ACCION = 'ui'         -> corre el ui.py de los modulos instalados (setup_ui.py lo usa al final)
# Desde otro script:  exec(open(project.folder + '/modulos/modulos.py', encoding='utf-8').read(),
#                          dict(globals(), ACCION='proyecto'))
import json, os

CARPETA = project.folder + '/modulos'
try:
    ACCION
except NameError:
    ACCION = 'lista'
try:
    NOMBRES
except NameError:
    NOMBRES = []


def catalogo():
    out = {}
    if not os.path.isdir(CARPETA):
        return out
    for n in sorted(os.listdir(CARPETA)):
        f = os.path.join(CARPETA, n, 'modulo.json')
        if os.path.isfile(f):
            try:
                out[n] = json.load(open(f, encoding='utf-8'))
            except Exception as e:
                print('[aviso] %s/modulo.json no se pudo leer: %s' % (n, e))
    return out


def instalado(m):
    d = m.get('detecta')
    d = d if isinstance(d, list) else ([d] if d else [])     # varias rutas: basta una (p. ej. ledfx en slices o en LED)
    return any(op(x) is not None for x in d)


def _correr(nombre, archivo):
    ruta = os.path.join(CARPETA, nombre, archivo)
    exec(compile(open(ruta, encoding='utf-8').read(), ruta, 'exec'), dict(globals(), __file__=ruta))


def orden(nombres, cat):
    """Dependencias primero, sin repetir."""
    vistos, out = set(), []

    def visita(n):
        if n in vistos:
            return
        if n not in cat:
            print('[aviso] no existe el modulo %s' % n)
            return
        vistos.add(n)
        for r in cat[n].get('requiere', []):
            visita(r)
        out.append(n)
    for n in nombres:
        visita(n)
    return out


def instalar(nombres):
    cat = catalogo()
    hechos = []
    for n in orden(nombres, cat):
        print('---- modulo %s' % n)
        try:
            _correr(n, 'instalar.py')
            hechos.append(n)
        except Exception:
            import traceback
            traceback.print_exc()
            print('[X] %s fallo; los que dependen de el se saltan' % n)
            break
    # UI al dia: setup_ui.py completo, de una vez y en este mismo cuadro (corre los ui.py de todos los modulos).
    # NO usar tdvj_core.refresh_ui() (reconstruccion diferida) desde un instalador: con show_titulos dejo a TD
    # colgado dos veces (2026-11-18).
    if hechos and op('/project2/ui_perform') is not None:
        p = project.folder + '/builders/herramientas/setup_ui.py'
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p))
    return hechos


def ui(nombres=None):
    """ui.py de los modulos instalados (o de los dados), si existe la UI de perform."""
    if op('/project2/ui_perform') is None:
        return []
    cat = catalogo()
    hechos = []
    for n, m in cat.items():
        if m.get('ui') and (n in nombres if nombres is not None else instalado(m)):
            try:
                _correr(n, m['ui'])
                hechos.append(n)
            except Exception:
                import traceback
                traceback.print_exc()
    return hechos


def del_proyecto():
    ruta = project.folder + '/proyecto.json'
    if not os.path.exists(ruta):
        return []
    mods = json.load(open(ruta, encoding='utf-8')).get('modulos', {})
    cat = catalogo()
    return [n for n, v in mods.items() if v and n in cat]     # visuales / fx / escena_modular no son carpetas


def lista():
    cat = catalogo()
    pedidos = set(del_proyecto())
    print('MODULOS en %s' % CARPETA)
    for n, m in cat.items():
        print('  %-14s v%-4s %-11s %-9s %s' % (n, m.get('version', '?'),
              'INSTALADO' if instalado(m) else '-', 'json' if n in pedidos else '', m.get('descripcion', '')))
        if m.get('requiere'):
            print('  %14s requiere: %s' % ('', ', '.join(m['requiere'])))


if ACCION == 'lista':
    lista()
elif ACCION == 'instalar':
    print('[ok] instalados:', instalar(NOMBRES))
elif ACCION == 'proyecto':
    p = del_proyecto()
    print('[ok] modulos del proyecto:', instalar(p) if p else '(ninguno en proyecto.json)')
elif ACCION == 'ui':
    print('[ok] ui de modulos:', ui())
