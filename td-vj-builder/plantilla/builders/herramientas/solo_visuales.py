# solo_visuales.py — show sin camaras ni FX: quita los ejemplos y manda los visuales a la salida. Idempotente.
import os
# Lo corre armar.py cuando modulos.escena_modular = false.
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core, escena_registro
importlib.reload(tdvj_core)
importlib.reload(escena_registro)
R = op('/project2')
E = R.op('base17/escena_modular')
for c in [x.name for x in E.children if x.isCOMP and x.name.startswith('layout_')]:
    escena_registro.retirar([c])
for c in list(R.op('_respaldo').children):
    c.destroy()
for n in (1, 18):
    b = R.op('base%d' % n)
    if not any(os.path.exists(x) for x in __import__('glob').glob(project.folder + '/builders/*/setup_base%d_*.py' % n)):
        for c in list(b.children):
            if c.name != 'out1':
                c.destroy()
        for g in list(b.customPages):
            g.destroy()
        b.allowCooking = False
escena_registro.sincronizar(orden=[])
R.op('switch23').par.index = 0
op('/project1/select2').par.top = '/project2/master_visuales'
print('salida: visuales ->', op('/project1/select2').par.top.eval())
