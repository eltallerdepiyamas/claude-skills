# fix_null4_warning.py — quita el warning de null4 y muestra como estaba ligado el gain viejo.
A = op('/project2/audio')
n = A.op('null4')
p = n.par.exporttable
print('exporttable antes:', p.mode, repr(p.expr), repr(p.val))
p.expr = ''
p.mode = ParMode.CONSTANT
p.val = 'null4_export'
n.cook(force=True)
print('warning null4:', (n.warnings() or 'ninguno').strip()[:100])
m = op('/project2/_respaldo/project1_hub/math30')
g = m.par.gain
print('math30.gain:', g.mode, repr(g.expr), repr(g.bindExpr), g.eval())
E = op('/project2/base17/escena_modular')
G = E.par.Gain
print('escena.Gain:', G.mode, 'bindExpr', repr(G.bindExpr), 'pagina', G.page.name, 'bindReferences', len(G.bindReferences) if hasattr(G, 'bindReferences') else '?')
print('  refs:', [str(r) for r in getattr(G, 'bindReferences', [])][:5])
for r in (op('/project2'), op('/project1')):
    for o in r.findChildren():
        for q in o.pars():
            if q.mode == ParMode.BIND and 'Gain' in q.bindExpr:
                print('BIND', o.path, q.name, q.bindExpr[:80])
