# completar_boilerplate.py — pone al dia el .toe del boilerplate y lo guarda. Idempotente.
R = op('/project2')
E = R.op('base17/escena_modular')
A = R.op('audio')
vieja = A.op('Little_Jesus___La_Magia')
if vieja is not None:
    vieja.name = 'audio_archivo'
    for o in [x for r in (op('/project1'), R) for x in r.findChildren()]:
        for p in o.pars():
            try:
                if p.mode == ParMode.CONSTANT and isinstance(p.val, str) and 'Little_Jesus___La_Magia' in p.val:
                    p.val = p.val.replace('Little_Jesus___La_Magia', 'audio_archivo'); print('ruta', o.path, p.name)
                elif p.mode == ParMode.EXPRESSION and 'Little_Jesus___La_Magia' in p.expr:
                    p.expr = p.expr.replace('Little_Jesus___La_Magia', 'audio_archivo'); print('expr', o.path, p.name)
            except Exception:
                pass
R.op('show').par.Audioarchivo = ''
for s in ('builders/herramientas/pads_seguros.py', 'control/setup_beatstep_canal.py', 'control/setup_beatstep_luces.py',
          'builders/herramientas/vaciar_show.py'):
    exec(open(project.folder + '/' + s, encoding='utf-8').read())
    print('[listo]', s)
R.op('show').par.Audioarchivo = 'assets/audio/silencio.wav'
R.op('base17/moviefilein1').par.file = ''
E.par.Recarchivo = ''
print('fx con contenido', [k for k in range(16) if R.op('pad_lib').module.tiene_contenido(R.op('switch23'), k)])
print('thumbs', len([c for c in R.op('ui_perform').children if c.isCOMP and c.name.startswith('th_')]), 'audio', R.op('audio/audio_gain').numChans)
project.save(project.folder + '/BOILERPLATE.toe')
print('guardado', project.name)
