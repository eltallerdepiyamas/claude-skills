# vaciar_show.py — deja BOILERPLATE.toe sin lo del show y con la estructura intacta.
# Solo corre si la carpeta tiene ES_BOILERPLATE (nunca en la carpeta de un show).
# Conserva de ejemplo: base1 (Formas), base18 (Trama), Multiview y Camara Unica.
# Uso (Textport): exec(open(project.folder + '/builders/herramientas/vaciar_show.py', encoding='utf-8').read())
import os, sys, importlib, re
if not os.path.exists(project.folder + '/ES_BOILERPLATE') or 'LITTLE_JESUS' in project.folder:
    raise SystemExit('[alto] esta carpeta no es el boilerplate: no toque nada')
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core, escena_registro
importlib.reload(tdvj_core)
importlib.reload(escena_registro)
R = op('/project2')
E = R.op('base17/escena_modular')
QUEDAN = ['layout_mv_multiview', 'layout_rs_camara_unica']

# 1 escenas
sobran = [c.name for c in E.children if c.isCOMP and c.name.startswith('layout_') and c.name not in QUEDAN]
escena_registro.retirar(sobran)
escena_registro.sincronizar(orden=QUEDAN)
E.par.Modoescena = QUEDAN[0]
print('escenas fuera:', len(sobran))

# 2 bases: la 2 queda vacia; todas las vacias sin cook
b = R.op('base2')
for c in list(b.children):
    if c.name != 'out1':
        c.destroy()
for g in list(b.customPages):
    g.destroy()
for n in tdvj_core.VISUAL_BASES + tdvj_core.EFFECT_BASES:
    o = R.op('base%d' % n)
    if o is not None and n not in (1, 18):
        o.allowCooking = False
R.op('switch2').par.index = 0
R.op('switch23').par.index = 0

# 3 archivos del show
for i in range(1, 7):
    m = E.op('cam%d_stock' % i)
    if m is not None:
        m.par.file = ''
S = R.op('show')
S.par.Audioarchivo = 'assets/audio/silencio.wav'
for i in range(1, 7):
    p = getattr(E.par, 'Nombre%d' % i, None)
    if p is not None:
        p.val = 'CAM %d' % i

# 4 respaldos
for c in list(R.op('_respaldo').children):
    c.destroy()

# 5 rutas del proyecto anterior
pat = re.compile(r'LITTLE.JESUS|RIO_SALVAJE', re.I)
for o in [x for r in (op('/project1'), R) for x in [r] + list(r.findChildren())]:
    for p in o.pars():
        try:
            t = p.expr if p.mode == ParMode.EXPRESSION else (p.val if isinstance(p.val, str) else '')
        except Exception:
            continue
        if t and pat.search(t):
            print('[ruta vieja]', o.path, p.name, t[:80])

exec(open(project.folder + '/builders/herramientas/setup_ui.py', encoding='utf-8').read())
print('[ok] vacio. Revisa errores, corre control/diag_todo.py y guarda BOILERPLATE.toe')
