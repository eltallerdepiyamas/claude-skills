# inventario_project1.py — SOLO LEE. La cadena de salida de /project1 (TOPs), audio (CHOPs de dispositivo /
# archivo / analisis), ventanas y lo que tenga MIDI exportado (p. ej. el Luma Level mapeado).
R = op('/project1')


def pv(o, n):
    p = getattr(o.par, n, None)
    if p is None:
        return None
    if p.mode == ParMode.EXPRESSION:
        return 'expr:' + p.expr
    if p.mode == ParMode.BIND:
        return 'bind:' + p.bindExpr
    if p.mode == ParMode.EXPORT:
        return 'export:%s' % (p.exportSource.owner.path + ':' + p.exportSource.name if p.exportSource else '?')
    return p.eval() if not p.isOP else (p.eval().path if p.eval() else str(p.val))


def io(o):
    ins = [i.name if i.parent() == R else i.path for i in o.inputs]
    outs = sorted(set(c.owner.name if c.owner.parent() == R else c.owner.path for oc in o.outputConnectors for c in oc.connections))
    return ins, outs


print('== TOPs / COMPs de /project1 ==')
for o in sorted(R.children, key=lambda o: (o.nodeX, -o.nodeY)):
    if not (o.isTOP or o.isCOMP):
        continue
    ins, outs = io(o)
    x = ''
    t = o.OPType
    if t == 'selectTOP': x = 'top=%s' % pv(o, 'top')
    elif t == 'switchTOP': x = 'index=%s' % pv(o, 'index')
    elif t in ('fitTOP', 'resolutionTOP'): x = 'res=%s x %s (%s)' % (pv(o, 'resolutionw'), pv(o, 'resolutionh'), pv(o, 'outputresolution'))
    elif t == 'windowCOMP': x = 'winop=%s monitor=%s' % (pv(o, 'winop'), pv(o, 'monitor'))
    elif t in ('ndioutTOP', 'syphonspoutoutTOP', 'videodeviceoutTOP'): x = 'active=%s name=%s' % (pv(o, 'active'), pv(o, 'name') or pv(o, 'sendername'))
    elif t == 'levelTOP':
        x = ' '.join('%s=%s' % (n, pv(o, n)) for n in ('brightness1', 'gamma1', 'contrast', 'opacity', 'blacklevel', 'invert') if pv(o, n) not in (None, 1.0, 0.0) or (isinstance(pv(o, n), str)))
    elif t == 'lumalevelTOP':
        x = ' '.join('%s=%s' % (p.name, pv(o, p.name)) for p in o.pars() if p.page and p.page.name in ('Level', 'Pre', 'RGBA') and p.mode != ParMode.CONSTANT)
        x += ' | ' + ' '.join('%s=%s' % (p.name, round(p.eval(), 3) if isinstance(p.eval(), float) else p.eval()) for p in o.pars() if p.page and p.page.name == 'Level')
    if o.isCOMP and t != 'windowCOMP':
        x = 'hijos=%d' % len(o.children)
    print('  %-26s %-20s in=%s out=%s %s %s' % (o.name, t, ins[:4], outs[:4], str(x)[:240], 'BYPASS' if getattr(o, 'bypass', False) else ''))
print('== audio ==')
for o in R.findChildren(depth=1):
    if o.OPType in ('audiodeviceinCHOP', 'audiodeviceoutCHOP', 'audiofileinCHOP', 'audiospectrumCHOP', 'audioanalysisCHOP') or 'audio' in o.name.lower():
        ins, outs = io(o)
        x = ' '.join('%s=%s' % (n, pv(o, n)) for n in ('device', 'driver', 'file', 'play', 'active', 'volume', 'rate', 'chops') if pv(o, n) is not None)
        print('  %-26s %-22s in=%s out=%s %s' % (o.name, o.OPType, ins[:3], outs[:4], str(x)[:200]))
print('== CHOPs que leen MIDI / selects de /project2 ==')
for o in R.findChildren(type=selectCHOP, depth=1):
    print('  ', o.name, pv(o, 'chops'), pv(o, 'channames'))
print('== conteo por tipo ==')
import collections
print(collections.Counter(o.OPType for o in R.children).most_common())
print('== ventanas (todo el proyecto) ==')
for w in op('/').findChildren(type=windowCOMP):
    print('  ', w.path, 'winop=', pv(w, 'winop'), 'monitor=', pv(w, 'monitor'), 'perform?=', w.path == getattr(ui, 'performWindow', None))
