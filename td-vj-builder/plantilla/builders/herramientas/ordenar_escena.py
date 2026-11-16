# ordenar_escena.py — acomoda escena_modular de ARRIBA a ABAJO (ver _lib/orden_escena.py). Solo mueve.
# Respaldo de posiciones: control/ordenar_escena_respaldo.json · RESTAURAR = True lo regresa.
import sys, importlib, json
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import orden_escena
importlib.reload(orden_escena)
RESTAURAR = False
S = op('/project2/base17/escena_modular')
F = project.folder + '/control/ordenar_escena_respaldo.json'
if RESTAURAR:
    for p, (x, y, c) in json.load(open(F, encoding='utf-8')).items():
        if op(p) is not None:
            op(p).nodeX, op(p).nodeY, op(p).color = x, y, tuple(c)
    print('[ok] restaurado')
else:
    json.dump({o.path: [o.nodeX, o.nodeY, list(o.color)] for o in S.children}, open(F, 'w', encoding='utf-8'), indent=0)
    n = orden_escena.acomodar(S)
    xs = [o.nodeX for o in S.children if o.OPType != 'annotateCOMP']
    ys = [o.nodeY for o in S.children if o.OPType != 'annotateCOMP']
    pos = {}
    for o in S.children:
        if o.OPType != 'annotateCOMP' and o.dock is None:
            pos.setdefault((o.nodeX, o.nodeY), []).append(o.name)
    enc = [v for v in pos.values() if len(v) > 1]
    print('[ok] escena_modular acomodada: %d nodos | ancho %d alto %d | encimados %d %s | recuadros %d' % (
        n, max(xs) - min(xs), max(ys) - min(ys), len(enc), enc[:3],
        len([o for o in S.children if o.OPType == 'annotateCOMP'])))
