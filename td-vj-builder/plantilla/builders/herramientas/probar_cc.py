# probar_cc.py — revisa camN_fuente -> CAM_N -> SLOT_N; deja todo como estaba.
E = op('/project2/base17/escena_modular')
for i in range(1, 7):
    g = E.op('CAM_%d' % i)
    g.cook(force=True)
    print(g.name, g.OPType, [x.name for x in g.inputs], '%dx%d' % (g.width, g.height), (g.errors() or 'OK').strip()[:80])
s = op('/project2/show'); b = s.par.Brillo.eval()
print('SLOT_1 ->', E.op('SLOT_1').par.top.eval(), E.op('SLOT_1').width)
