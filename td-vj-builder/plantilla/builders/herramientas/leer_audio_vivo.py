# leer_audio_vivo.py — SOLO LEE: por que no llega audio.
A = op('/project2/audio')
m = A.op('Little_Jesus___La_Magia')
print('archivo', m.par.file.eval(), 'existe', __import__('os').path.exists(project.folder + '/' + m.par.file.eval()), 'errores', m.errors(), m.warnings())
print('play', m.par.play.eval(), 'playmode', m.par.playmode.eval(), 'repeat', m.par.repeat.eval() if hasattr(m.par,'repeat') else '', 'chans', m.numChans, 'len', m.numSamples, 'rate', m.rate)
for n in ('Little_Jesus___La_Magia', 'audio_fuente', 'audio_gain', 'switch6'):
    o = A.op(n)
    v = [abs(x) for c in o.chans() for x in c.vals]
    print(n, 'pico', round(max(v), 4) if v else None, 'muestras', len(v))
f = A.op('audio_fuente'); print('fuente index', f.par.index.eval(), 'Audiofuente', op('/project2/show').par.Audiofuente.eval(), 'gain', op('/project2/show').par.Audiogain.eval())
print('timeline play', root.time.play, 'seg', round(absTime.seconds, 1), 'index expr', m.par.index.expr, 'val', m.par.index.eval())
n = A.op('master_audio'); print({c.name: round(c.eval(), 3) for c in n.chans()[:4]})
