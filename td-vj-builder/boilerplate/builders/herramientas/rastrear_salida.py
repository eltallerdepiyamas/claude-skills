# rastrear_salida.py — SOLO LEE: sigue la salida de FX hacia atras e imprime resolucion y tipo de cada paso.
o = op('/project2/null28')
for _ in range(20):
    if o is None:
        break
    extra = ''
    if o.OPType == 'switchTOP':
        extra = 'index=%d' % o.par.index.eval()
    if o.OPType in ('transformTOP', 'fitTOP', 'cropTOP', 'resolutionTOP', 'levelTOP'):
        extra = ' '.join('%s=%s' % (p.name, p.eval()) for p in o.pars() if p.page and p.page.name in ('Transform', 'Fit', 'Crop') and p.eval() != p.default)
    print('%-60s %-16s %dx%d %s %s' % (o.path, o.OPType, o.width, o.height, extra, 'BYPASS' if o.bypass else ''))
    if o.OPType == 'outTOP' and o.inputs:
        o = o.inputs[0]; continue
    if o.isCOMP:
        oo = o.op('out1'); o = oo; continue
    if not o.inputs:
        if o.OPType == 'inTOP':
            p = o.parent(); k = int(o.name.replace('in', '') or 1) - 1
            o = p.inputs[k] if len(p.inputs) > k else None; continue
        if o.OPType == 'selectTOP':
            o = o.par.top.eval(); continue
        break
    k = min(max(int(o.par.index.eval()), 0), len(o.inputs) - 1) if o.OPType == 'switchTOP' else 0
    o = o.inputs[k]
