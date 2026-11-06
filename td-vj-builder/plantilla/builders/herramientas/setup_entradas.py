# ─────────────────────────────────────────────────────────────
# setup_entradas.py — ordena las entradas de camara de escena_modular (ver _lib/entradas.py).
# Cada CAM_N = [camN_solido, camN_stock, camN_vivo]; un solo control en la pestana Camaras:
#   Fuente (todas) · Fuente Cam 1..6 (Global o propia) · Vivo prendido.
# Idempotente. Lo que ya no se usa (select*, switch4, base1 del overlay) se va a
# /project2/_respaldo/escena_modular_entradas (no se borra).
# Uso: Text DAT con File = este .py → Run Script (o el MCP: correr_script).
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import paleta, entradas
importlib.reload(paleta)
importlib.reload(entradas)

E = op('/project2/base17/escena_modular')
for linea in entradas.ensure(E):
    print('  ', linea)
print('[ok] entradas: Fuente = %s · Vivo prendido = %s' % (E.par.Fuente.eval(), E.par.Vivoprendido.eval()))
for i in range(1, 7):
    c = E.op('cam%d_fuente' % i)
    v = E.op('cam%d_vivo' % i)
    dev = v.par.device.eval().split('|||')[-1] if v is not None and v.par.device.eval() else '(sin dispositivo)'
    print('   cam%d_fuente  index=%d  [%s]  vivo: %s' % (i, int(c.par.index.eval()), ', '.join(o.name for o in c.inputs), dev))
