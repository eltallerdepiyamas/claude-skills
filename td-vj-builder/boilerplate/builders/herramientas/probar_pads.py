# probar_pads.py — simula los pads (llama onOffToOn de cada chopexec) y revisa que muevan su switch; deja todo como estaba.
R = op('/project2')
s2, s23 = R.op('switch2'), R.op('switch23')
antes = (s2.par.index.eval(), s23.par.index.eval())
mal = []
for d in sorted(R.findChildren(type=chopexecuteDAT, depth=1), key=lambda d: d.name):
    if d.name.startswith(('vis_knobs', 'fx_knobs')):
        continue
    t = d.text
    sw = s2 if "op('switch2')" in t else (s23 if "op('switch23')" in t else None)
    if sw is None:
        continue
    import re
    m = re.search(r"op\('switch2?3?'\)\.par\.index=(\d+)", t)
    want = int(m.group(1)) if m else None
    try:
        d.module.onOffToOn(None, 0, 1, 0)
    except Exception as e:
        mal.append('%s: %s' % (d.name, e)); continue
    if want is not None and int(sw.par.index.eval()) != want:
        mal.append('%s: index %d (esperaba %d)' % (d.name, sw.par.index.eval(), want))
s2.par.index, s23.par.index = antes
op('/project2/play').par.value0 = 0
print('pads probados · con problema: %d %s' % (len(mal), mal[:6]))
# errores vivos (sin _respaldo ni audioAnalysis de terceros)
n = []
for root in (op('/project1'), op('/project2')):
    for o in [root] + list(root.findChildren()):
        if '/_respaldo' in o.path or '/audioAnalysis/' in o.path:
            continue
        e = (o.errors(recurse=False) or o.scriptErrors(recurse=False) or '').strip()
        if e:
            n.append('%s | %s' % (o.path, e.splitlines()[0][:90]))
print('errores vivos: %d' % len(n))
for x in n[:10]:
    print('  ', x)
