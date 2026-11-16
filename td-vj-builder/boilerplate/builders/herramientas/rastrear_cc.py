# rastrear_cc.py — SOLO LEE: quien usa un canal o nodo en toda la red viva (cambiar CANALES).
CANALES = ('null40', 'null44', 'count8', 'limit9', 'math19')
vivos = [o for r in (op('/project1'), op('/project2')) for o in r.findChildren() if '/_respaldo' not in o.path]
for o in vivos:
    for p in o.pars():
        try:
            t = p.expr if p.mode == ParMode.EXPRESSION else (p.val if isinstance(p.val, str) else '')
        except Exception:
            continue
        if t and any(c in t for c in CANALES):
            print('PAR', o.path, p.name, '=', str(t)[:100], '->', p.eval())
    if o.isDAT:
        try:
            if any(c in o.text for c in CANALES):
                print('DAT', o.path)
        except Exception:
            pass
    if o.isCHOP and o.numChans < 40:
        for c in o.chans():
            if False:
                print('CHOP', o.path, c.name, round(c.eval(), 3), '| salidas', [k.owner.path for oc in o.outputConnectors for k in oc.connections][:5])
