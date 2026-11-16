# acomodar_pads.py — cada cadena de pad (constant -> logic -> chopexec) en la FILA de la base que dispara,
# a la izquierda del visual, como las de base1-16. Arriba de los visuales va todo lo demas; los visuales
# (y sus pads) bajan en vertical, una fila por base. SOLO mueve: no conecta ni borra.
# Separa tambien los DATs que quedaron encimados. Respaldo: control/acomodar_pads_respaldo.json
import json, re
R = op('/project2')
sw = R.op('switch2')
COLS = {'constant': -795, 'logic': -595, 'chopexec': -395}
json.dump({o.path: [o.nodeX, o.nodeY] for o in R.children},
          open(project.folder + '/control/acomodar_pads_respaldo.json', 'w', encoding='utf-8'), indent=0)


def base_de(k):
    """La base que muestra la entrada k de switch2."""
    if k >= len(sw.inputs):
        return None
    o = sw.inputs[k]
    for _ in range(4):
        if o is None:
            return None
        if o.parent() != R:                 # baseN/out1
            return o.parent()
        if re.match(r'base\d+$', o.name):
            return o
        nul = next((i for i in o.inputs if i.OPType == 'nullTOP'), None) if o.OPType == 'switchTOP' else None
        o = nul if nul is not None else (o.inputs[0] if o.inputs else None)
    return None


movidos = 0
for d in R.findChildren(type=chopexecuteDAT, depth=1):
    m = re.search(r"elegir\('switch2', (\d+)\)", d.text)
    if not m:
        continue
    b = base_de(int(m.group(1)))
    if b is None:
        continue
    nombres = [q.name for q in d.pars()]
    pc = d.par.chops if 'chops' in nombres else (d.par.chop if 'chop' in nombres else None)
    lg = op(pc.eval()) if pc is not None and pc.eval() else None
    cs = lg.inputs[0] if lg is not None and lg.inputs else None
    for o, col in ((cs, 'constant'), (lg, 'logic'), (d, 'chopexec')):
        if o is not None and o.parent() == R:
            o.nodeX, o.nodeY = COLS[col], b.nodeY
            movidos += 1
# DATs encimados en la zona de arriba: el segundo de cada par, a la derecha
for a, b in (('pad_lib', 'vis_nombres_tabla'), ('vis_knobs_map', 'midi_monitor_lib')):
    oa, ob = R.op(a), R.op(b)
    if oa is not None and ob is not None and abs(oa.nodeX - ob.nodeX) < 120 and abs(oa.nodeY - ob.nodeY) < 100:
        ob.nodeX, ob.nodeY = oa.nodeX + 200, oa.nodeY
# revisar
cajas = {}
for o in R.children:
    if o.OPType != 'annotateCOMP':
        cajas.setdefault((round(o.nodeX / 60), round(o.nodeY / 60)), []).append(o.name)
enc = [v for v in cajas.values() if len(v) > 1]
print('pads movidos a la fila de su base:', movidos, '| encimados que quedan:', enc)
# regla: todo acomodo termina con los recuadros de titulo de cada grupo
exec(open(project.folder + '/builders/herramientas/recuadros_project2.py', encoding='utf-8').read())
