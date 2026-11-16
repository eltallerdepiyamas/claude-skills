# inspeccionar_entradas.py — SOLO LEE. Imprime como estan armadas las entradas de camara de
# escena_modular (CAM_1..6, sus fuentes, selects, video device in, movie file in, base1).
E = op('/project2/base17/escena_modular')


def _par(o, *names):
    out = []
    for n in names:
        p = getattr(o.par, n, None)
        if p is None:
            continue
        v = p.expr if p.mode == ParMode.EXPRESSION else (p.bindExpr if p.mode == ParMode.BIND else p.eval())
        out.append('%s=%s%s' % (n, 'expr:' if p.mode == ParMode.EXPRESSION else ('bind:' if p.mode == ParMode.BIND else ''), v))
    return ' '.join(out)


def show(o):
    ins = [i.path.split('/')[-1] if i.parent() == E else i.path for i in o.inputs]
    outs = sorted(set(c.owner.path.replace(E.path + '/', '') for oc in o.outputConnectors for c in oc.connections))
    extra = ''
    t = o.OPType
    if t == 'switchTOP': extra = _par(o, 'index', 'blend')
    elif t == 'selectTOP': extra = _par(o, 'top')
    elif t == 'constantTOP': extra = _par(o, 'colorr', 'colorg', 'colorb', 'outputresolution')
    elif t == 'videodeviceinTOP': extra = _par(o, 'active', 'library', 'device', 'signalformat')
    elif t == 'moviefileinTOP': extra = _par(o, 'file', 'play')
    print('  %-34s %-18s pos=(%d,%d)  in=%s  ->%s  %s' % (o.name, t, o.nodeX, o.nodeY, ins, outs, extra))


print('== CAM / SLOT ==')
for n in ['CAM_%d' % i for i in range(1, 7)] + ['SLOT_%d' % i for i in range(1, 6)] + ['SLOT_UNICA']:
    if E.op(n): show(E.op(n))
print('== fuentes ==')
for o in sorted(E.children, key=lambda o: o.name):
    if o.OPType in ('constantTOP', 'videodeviceinTOP', 'moviefileinTOP', 'selectTOP', 'switchTOP') and not o.name.startswith(('CAM_', 'SLOT_', 'demo_')):
        show(o)
print('== base1 (dentro de escena_modular) ==')
b = E.op('base1')
if b:
    print('  comment:', b.comment)
    for o in b.children:
        show(o)
print('== quien lee CAM_ / videodevin desde fuera ==')
import re
for o in op('/project2').findChildren(type=selectTOP):
    p = o.par.top.eval() if o.par.top.eval() else None
    s = o.par.top.expr if o.par.top.mode == ParMode.EXPRESSION else str(o.par.top.val)
    if any(k in s for k in ('CAM_', 'videodevin', 'escena_modular/')) and o.parent() != E:
        print('  ', o.path, '->', s)
print('== pagina custom de escena_modular ==')
for pg in E.customPages:
    print('  ', pg.name, [p.name for p in pg.pars][:40])
