# inspeccionar_bases.py — SOLO LEE: errores de las bases FX vacias frente a base25.
R = op('/project2')
for n in (43, 44, 50):
    o = R.op('null%d' % n)
    o.cook(force=True)
    print(o.name, repr(o.errors()), 'input', o.inputs[0].path if o.inputs else None, [x.name for x in o.inputs])
for n in (25, 26):
    b = R.op('base%d' % n)
    print(b.name, 'out1 err', repr(b.op('out1').errors()), 'in', [x.name for x in b.op('out1').inputs])
