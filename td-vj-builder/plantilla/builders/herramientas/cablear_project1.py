# cablear_project1.py — cadena final de /project1 (FX globales) + regresa las tablas *_keys de las rampas.
P1, C = op('/project1'), op('/project2/control_p1')
# tablas de rampa / docked que se fueron a control_p1 -> de vuelta junto a su nodo
for d in [o for o in C.children if o.name.endswith('_keys') or o.name.endswith('_grouptable')]:
    if P1.op(d.name) is None:
        P1.copyOPs([d])
        print('[ok] regresado', d.name)
    d.destroy()
for i in range(1, 33):
    r, k = P1.op('ramp%d' % i), P1.op('ramp%d_keys' % i)
    if r is not None and k is not None and r.par.dat.eval() != k:
        r.par.dat = k
PARES = [('feedback_HSV1', 0, 'select2'), ('null42', 0, 'feedback_HSV1'), ('lookup2', 0, 'feedback_HSV1'),
         ('V2_COLOR', 0, 'null42'), ('V2_COLOR', 1, 'lookup2'), ('curcuitBending1', 0, 'V2_COLOR'),
         ('color_final', 0, 'curcuitBending1'), ('ndiout1', 0, 'color_final')]
for dst, k, src in PARES:
    d, s = P1.op(dst), P1.op(src)
    ok = False
    for arg in (s, s.outputConnectors[0] if s.outputConnectors else None):
        try:
            d.inputConnectors[k].connect(arg)
            ok = True
            break
        except Exception:
            pass
    print('%-16s <- %-16s entrada %d  %s' % (dst, src, k, 'OK' if ok else 'NO SE PUDO'))
print('/project1:', sorted(o.name for o in P1.children if not o.name.endswith('_keys')))
print('ramps con tabla:', sum(1 for i in range(1, 33) if P1.op('ramp%d_keys' % i)))
