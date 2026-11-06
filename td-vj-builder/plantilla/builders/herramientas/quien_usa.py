# quien_usa.py — SOLO LEE: quien consume cada canal MIDI (selects y destino final por expresion).
import re
C = op('/project2/control_p1')
CH = ['ch1ctrl51', 'ch1ctrl55', 'ch1ctrl59', 'ch1ctrl52', 'ch1ctrl63', 'ch1n27']
sels = {c: [o for o in C.children if o.OPType == 'selectCHOP' and c in o.par.channames.eval().split()] for c in CH}
for c in CH:
    print(c, 'selects:', [o.name for o in sels[c]])
    for o in sels[c]:
        o2, chain = o, []
        for _ in range(8):
            nx = [k.owner for oc in o2.outputConnectors for k in oc.connections]
            if not nx:
                break
            o2 = nx[0]; chain.append('%s(%s)' % (o2.name, o2.OPType[:-4]))
        print('   cadena:', ' > '.join(chain))
        for t in [o] + [C.op(x.split('(')[0]) for x in chain]:
            for r in (op('/project1'), op('/project2')):
                for q in r.findChildren():
                    if '/_respaldo' in q.path:
                        continue
                    for p in q.customPars if q.isCOMP else q.pars():
                        if p.mode == ParMode.EXPRESSION and ("/%s'" % t.name) in p.expr and c in p.expr:
                            print('   PARAM', q.path, p.name)
for o in C.children:
    if o.OPType == 'oscoutCHOP':
        print('OSC', o.name, 'active', o.par.active.eval(), 'ip', o.par.address.eval() if hasattr(o.par,'address') else '', [i.name for i in o.inputs], [c.name for c in o.chans()][:5])
