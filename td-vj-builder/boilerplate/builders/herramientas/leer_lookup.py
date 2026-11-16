# leer_lookup.py — SOLO LEE: como estaba armado el lookup de color (V2_COLOR entrada 2) para dejar referencia.
P1 = op('/project1')


def pars(o, solo_custom=False, todos=False):
    out = []
    for p in (o.customPars if solo_custom else o.pars()):
        if p.mode in (ParMode.EXPRESSION, ParMode.BIND, ParMode.EXPORT):
            v = p.expr if p.mode == ParMode.EXPRESSION else (p.bindExpr if p.mode == ParMode.BIND else 'export')
            out.append('%s=[%s] %s' % (p.name, str(p.mode).split('.')[-1][:4], v))
        elif todos and p.page and p.page.name not in ('Common',) and p.eval() != p.default:
            out.append('%s=%s' % (p.name, p.eval()))
    return out


for n in ('lookup2', 'switch5', 'base6', 'blend_switch2', 'blend_switch3', 'V2_COLOR'):
    o = P1.op(n)
    if o is None:
        continue
    print('==', n, o.OPType, 'in=', [i.name for i in o.inputs], 'comment=', o.comment[:60])
    for l in pars(o, solo_custom=o.isCOMP, todos=not o.isCOMP)[:14]:
        print('   ', l[:150])
    if o.isCOMP:
        print('    pags:', [(pg.name, [p.name for p in pg.pars][:10]) for pg in o.customPages])
        print('    hijos:', sorted(set(c.OPType for c in o.children)), [c.name for c in o.children][:14])
        for c in o.children:
            ex = pars(c)
            if ex:
                print('     ', c.name, '|', ' · '.join(ex)[:160])
r = P1.op('ramp1')
print('== ramp1', 'pars:', pars(r, todos=True)[:12])
k = P1.op('ramp1_keys')
if k is not None:
    print('   ramp1_keys:', [[c.val for c in row] for row in k.rows()][:6])
# donde se mueven "period" / "phase" (knobs)
print('== quien tiene period / phase con expresion ==')
for o in [P1] + list(P1.findChildren()):
    for p in o.pars():
        if ('period' in p.name.lower() or 'phase' in p.name.lower()) and p.mode != ParMode.CONSTANT:
            v = p.expr if p.mode == ParMode.EXPRESSION else (p.bindExpr if p.mode == ParMode.BIND else 'export')
            print('  ', o.path, p.name, '|', v[:140])
