# ─────────────────────────────────────────────────────────────
# limpiar_project2.py — limpieza de /project2 (2026-11-04). Idempotente.
#  1. MUERTOS -> /project2/_respaldo/project2_limpieza (se copian y se quitan; NO se borran):
#     pads que mandan a 'switch5' (no existe), boton que apaga 'black' (no existe), cadena MIDI sin
#     salida, Text DATs de builders viejos, text1 (vacio; los pads lo corrian sin hacer nada).
#  2. VISUALES en un solo switch: switch2 recibe directo switch6..21 (entrada N-1 = baseN);
#     switch1 y switch3 se van al respaldo. Los pads 1-16 ahora solo mueven switch2.
#  3. Quita de los pads que se quedan la linea op('text1').run(...).
#  Con UI_VIEJA = True tambien manda al respaldo la UI de perform anterior (container1, opviewer1-4,
#  parameter1-4, button2 "Mode Switch" y su cadena).
# ─────────────────────────────────────────────────────────────
import re

UI_VIEJA = False
R = op('/project2')
DEST = 'project2_limpieza'

MUERTOS = (
    ['chopexec%d' % i for i in list(range(25, 33)) + [35, 38, 39]] +      # -> switch5 (no existe)
    ['logic%d' % i for i in list(range(25, 33)) + [69, 71, 73]] +
    ['constant%d' % i for i in list(range(25, 33)) + [33, 35, 36]] +
    ['button1', 'null1', 'logic65', 'logic66', 'chopexec33', 'chopexec34'] +  # -> 'black' (no existe)
    ['select1', 'logic91', 'count1', 'null51'] +                           # MIDI sin salida
    ['setup_base38_liquid_feedback1', 'setup_layout_rs_late_show', 'text1']
)
UI = ['container1', 'opviewer1', 'opviewer2', 'opviewer3', 'opviewer4',
      'parameter1', 'parameter2', 'parameter3', 'parameter4',
      'button2', 'null2', 'logic67', 'logic68', 'chopexec36', 'chopexec37']


def respaldo(nombres):
    ops = [R.op(n) for n in nombres if R.op(n) is not None]
    if not ops:
        return []
    r = R.op('_respaldo') or R.create(baseCOMP, '_respaldo')
    d = r.op(DEST) or r.create(baseCOMP, DEST)
    d.copyOPs(ops)
    out = [o.name for o in ops]
    for o in ops:
        o.destroy()
    return out


def visual_activo():
    """Numero del visual (1-16) que sale hoy por switch2 (esquema viejo o nuevo)."""
    s2 = R.op('switch2')
    ins = s2.inputs
    k = min(max(int(s2.par.index.eval()), 0), len(ins) - 1)
    o = ins[k]
    if o.name in ('switch1', 'switch3'):
        j = min(max(int(o.par.index.eval()), 0), len(o.inputs) - 1)
        return (1 if o.name == 'switch1' else 9) + j
    m = re.match(r'switch(\d+)$', o.name)
    return int(m.group(1)) - 5 if m else 1


def unificar():
    s2 = R.op('switch2')
    sel = ['switch%d' % (i + 5) for i in range(1, 17)]     # switch6 = base1 ... switch21 = base16
    if [i.name for i in s2.inputs] == sel:
        print('[=] switch2 ya tiene los 16 visuales directo')
        return
    n = visual_activo()
    for c in reversed(list(s2.inputConnectors)):
        c.disconnect()
    for k, name in enumerate(sel):
        s2.inputConnectors[k].connect(R.op(name))
    s2.par.index = n - 1
    s2.comment = 'Visuales: entrada N-1 = baseN (pads 1-16, Stream Deck /td/visual)'
    print('[ok] switch2 <- switch6..21 directo · visual activo = base%d' % n)
    print('[ok] al respaldo:', respaldo(['switch1', 'switch3']))


def pads():
    cambiados = []
    for i in range(1, 17):
        d = R.op('chopexec%d' % i)
        if d is None:
            continue
        t = d.text
        t2 = re.sub(r"\top\('switch[13]'\)\.par\.index=\d+\n", '', t)
        t2 = re.sub(r"op\('switch2'\)\.par\.index=\d+", "op('switch2').par.index=%d" % (i - 1), t2)
        if t2 != t:
            d.text = t2
            cambiados.append(d.name)
    for d in R.findChildren(type=chopexecuteDAT, depth=1):
        t = d.text
        t2 = re.sub(r"[ \t]*op\('text1'\)\.run\([^\n]*\)\n", '', t)
        if t2 != t:
            d.text = t2
            if d.name not in cambiados:
                cambiados.append(d.name)
    print('[ok] pads actualizados:', ', '.join(cambiados) or '(ninguno)')


print('==== limpiar_project2 ====')
print('[ok] al respaldo (muertos):', respaldo(MUERTOS))
unificar()
pads()
pe = R.op('vis_knobs_parexec')
if pe is not None and 'switch1' in str(pe.par.op.val):
    pe.par.op = 'switch2'
    print('[ok] vis_knobs_parexec vigila solo switch2')
if UI_VIEJA:
    print('[ok] al respaldo (UI vieja):', respaldo(UI))
print('listo: respaldo en /project2/_respaldo/%s' % DEST)
