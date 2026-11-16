# quitar_lookup.py — quita el lookup de color de /project1 (referencia: research/referencia_lookup_color.md).
# lookup2, base6, switch5, blend_switch2/3, ramp1-32 (+ keys), V2_COLOR y null42 -> _respaldo/project1_lookup_color.
# Cadena: feedback_HSV1 -> curcuitBending1 -> color_final -> ndiout1. Idempotente.
P1 = op('/project1')
nombres = ['lookup2', 'base6', 'switch5', 'blend_switch2', 'blend_switch3', 'V2_COLOR', 'null42']
nombres += ['ramp%d' % i for i in range(1, 33)] + ['ramp%d_keys' % i for i in range(1, 33)]
ops = [P1.op(n) for n in nombres if P1.op(n) is not None]
if ops:
    r = op('/project2/_respaldo')
    d = r.op('project1_lookup_color') or r.create(baseCOMP, 'project1_lookup_color')
    d.allowCooking = False
    d.copyOPs(ops)
    for o in ops:
        if o.valid:
            o.destroy()
    print('[ok] al respaldo: %d nodos' % len(ops))
fb, cb = P1.op('feedback_HSV1'), P1.op('curcuitBending1')
cb.inputConnectors[0].connect(fb.outputConnectors[0])
print('curcuitBending1 <-', [i.path for i in cb.inputs])
for o in list(P1.findChildren()):
    try:
        o.cook(force=True)
    except Exception:
        pass
bad = [o.path for o in [P1] + list(P1.findChildren()) if (o.errors(recurse=False) or o.scriptErrors(recurse=False))]
print('errores en /project1:', len(bad), bad[:6])
print('/project1:', sorted(o.name for o in P1.children))
