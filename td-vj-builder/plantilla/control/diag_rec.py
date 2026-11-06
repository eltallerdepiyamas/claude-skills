# diag_rec.py — por que la grabacion sale sin audio. Solo lee, no cambia nada.
# Textport:  exec(open(project.folder + '/control/diag_rec.py', encoding='utf-8').read())
S = op('/project2/base17/escena_modular')
rec = S.op('demo_rec') if S is not None else None
print('==== diag_rec ====')
if rec is None:
    print('[error] no existe demo_rec: corre actualizar_companion.py')
else:
    print('Recaudio =', S.par.Recaudio.eval() if hasattr(S.par, 'Recaudio') else 'NO EXISTE',
          '| Recaudiochop =', S.par.Recaudiochop.eval() if hasattr(S.par, 'Recaudiochop') else 'NO EXISTE')
    for p in rec.pars():
        t = (p.name + ' ' + p.label).lower()
        if any(k in t for k in ('audio', 'codec', 'type', 'file', 'record')):
            extra = ''
            if p.mode != type(p.mode).CONSTANT:
                extra = '  [%s: %s]' % (p.mode, p.expr)
            if p.isMenu:
                extra += '  opciones=%s' % list(p.menuNames)
            print('  %-18s %-24s = %r%s' % (p.name, p.label, p.eval(), extra))
    ach = None
    for n in ('audiochop', 'audio'):
        if hasattr(rec.par, n):
            ach = getattr(rec.par, n).eval()
    if ach is None:
        print('[!] el grabador NO tiene CHOP de audio asignado')
    else:
        print('CHOP de audio:', ach.path, '| tipo', ach.OPType, '| canales', ach.numChans,
              [c.name for c in ach.chans()][:8], '| rate', ach.rate, '| timeslice', ach.isTimeSlice,
              '| errores', ach.errors() or '-')
        if ach.rate < 8000:
            print('[!] rate', ach.rate, '= NO es audio (es analisis a', ach.rate, 'fps). Usa el Audio Device In, no null4')
    print('errores del grabador:', rec.errors() or '-', '| warnings:', rec.warnings() or '-')
