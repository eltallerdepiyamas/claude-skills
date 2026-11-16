# inventario_detalle.py — SOLO LEE. Detalle compacto de /project2 por grupos para decidir orden/limpieza.
import re
R = op('/project2')


def pv(o, n):
    p = getattr(o.par, n, None)
    if p is None:
        return None
    if p.mode == ParMode.EXPRESSION:
        return 'expr:' + p.expr
    if p.mode == ParMode.BIND:
        return 'bind:' + p.bindExpr
    return p.eval() if not p.isOP else (p.eval().path if p.eval() else str(p.val))


def io(o):
    ins = [i.name if i.parent() == R else i.path for i in o.inputs]
    outs = sorted(set(c.owner.name if c.owner.parent() == R else c.owner.path for oc in o.outputConnectors for c in oc.connections))
    return ins, outs


print('== senal (TOPs y COMPs) ==')
for o in sorted(R.children, key=lambda o: o.name):
    if o.isTOP or (o.isCOMP and o.OPType == 'baseCOMP'):
        ins, outs = io(o)
        x = ''
        if o.OPType == 'switchTOP': x = 'index=%s' % pv(o, 'index')
        if o.OPType == 'moviefileinTOP': x = 'file=%s play=%s' % (str(pv(o, 'file'))[-40:], pv(o, 'play'))
        if o.OPType == 'outTOP': x = ''
        print('  %-22s %-15s in=%s out=%s %s %s' % (o.name, o.OPType, ins, outs, x, 'BYPASS' if o.bypass else ''))
print('== chopexec / logic / constant ==')
for o in sorted(R.findChildren(type=chopexecuteDAT, depth=1), key=lambda o: o.name):
    ch = pv(o, 'chops')
    tgt = op(o.par.chops.eval()) if o.par.chops.eval() else None
    first = (o.text.strip().splitlines() or [''])
    body = [l.strip() for l in o.text.splitlines() if l.strip().startswith(('op(', 'parent', 'me.', 'run(')) or 'par.' in l][:2]
    print('  %-14s active=%s chops=%s ok=%s  %s' % (o.name, pv(o, 'active'), ch, tgt is not None, ' | '.join(body)[:120]))
for t in (logicCHOP, constantCHOP, nullCHOP, selectCHOP, lagCHOP, countCHOP, midiinCHOP):
    for o in sorted(R.findChildren(type=t, depth=1), key=lambda o: o.name):
        ins, outs = io(o)
        x = ''
        if t == constantCHOP: x = 'name0=%s value0=%s' % (pv(o, 'name0'), pv(o, 'value0'))
        if t == selectCHOP: x = 'chops=%s' % pv(o, 'chops')
        print('  %-14s %-12s in=%s out=%s %s' % (o.name, o.OPType, ins, outs, str(x)[:110]))
print('== DATs / UI / otros ==')
for o in sorted(R.children, key=lambda o: o.name):
    if o.isDAT and o.OPType != 'chopexecuteDAT' or o.OPType in ('parameterCOMP', 'opviewerCOMP', 'buttonCOMP', 'containerCOMP') or o.isCHOP and o.OPType not in ('logicCHOP', 'constantCHOP', 'nullCHOP', 'selectCHOP', 'lagCHOP', 'countCHOP', 'midiinCHOP'):
        ins, outs = io(o)
        x = ''
        if o.isDAT:
            x = 'file=%s active=%s' % (pv(o, 'file'), pv(o, 'active'))
        if o.OPType in ('parameterCOMP', 'opviewerCOMP'):
            x = 'op=%s' % (pv(o, 'op') or pv(o, 'opviewer'))
        print('  %-26s %-20s in=%s out=%s %s' % (o.name, o.OPType, ins, outs, str(x)[:120]))
