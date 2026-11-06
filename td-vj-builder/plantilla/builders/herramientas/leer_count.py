# leer_count.py — SOLO LEE: que expresion tienen count7 / count12 en Limit Maximum y a quien alimentan.
C = op('/project2/control_p1')
for n in ('count7', 'count12'):
    o = C.op(n)
    p = o.par.limitmax
    outs = [c.owner.name for oc in o.outputConnectors for c in oc.connections]
    print(n, '| limitmax:', p.expr if p.mode == ParMode.EXPRESSION else p.eval(), '| in:', [i.name for i in o.inputs], '| out:', outs)
