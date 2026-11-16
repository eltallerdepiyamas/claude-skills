# leer_audio_gain.py — SOLO LEE: gain de audio mapeado, warning de null4 y referencias a master_out / null4.
A = op('/project2/audio')
E = op('/project2/base17/escena_modular')
print('escena.Gain:', E.par.Gain.mode, E.par.Gain.expr, E.par.Gain.eval() if hasattr(E.par, 'Gain') else None)
n = A.op('null4')
print('null4 export pars:', [(p.name, p.eval()) for p in n.pars() if 'export' in p.name.lower()])
print('null4_export existe:', [o.path for r in (op('/project1'), op('/project2')) for o in r.findChildren(name='null4_export')])
sw = A.op('switch6')
print('switch6 inputs', [i.name for i in sw.inputs], 'index', sw.par.index.eval())
print('audio hijos:', [o.name for o in A.children])
aa = A.op('audioAnalysis')
for p in aa.customPars:
    if p.mode != ParMode.CONSTANT and 'ain' in p.name:
        print('  aa', p.name, p.mode, p.expr)
for r in (op('/project2'), op('/project1')):
    for o in r.findChildren():
        if '/_respaldo' in o.path:
            continue
        for p in o.pars():
            try:
                if p.mode == ParMode.EXPRESSION and ('.par.Gain' in p.expr or 'par.Audiogain' in p.expr):
                    print('GAIN ->', o.path, p.name, p.expr[:90])
                if p.mode == ParMode.EXPRESSION and 'ch1ctrl' in p.expr and o.path.startswith('/project2/audio'):
                    print('MIDI audio ->', o.path, p.name, p.expr[:90])
            except Exception:
                pass
cnt = {'master_out': 0, 'audio/null4': 0}
for o in op('/project2').findChildren():
    if '/_respaldo' in o.path:
        continue
    for p in o.pars():
        try:
            t = p.expr if p.mode == ParMode.EXPRESSION else (p.val if isinstance(p.val, str) else '')
            for k in cnt:
                if k in (t or ''):
                    cnt[k] += 1
        except Exception:
            pass
print('referencias:', cnt)
