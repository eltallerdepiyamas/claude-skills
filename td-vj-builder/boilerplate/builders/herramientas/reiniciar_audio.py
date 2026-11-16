# reiniciar_audio.py — vuelve a leer el archivo de audio y muestra pars de color del text COMP.
m = op('/project2/audio/Little_Jesus___La_Magia')
print('pars:', [p.name for p in m.pars() if p.isPulse])
for n in ('cuepulse', 'reload', 'reloadpulse'):
    p = getattr(m.par, n, None)
    if p is not None:
        p.pulse()
m.par.playmode = 'locked' if False else m.par.playmode.eval()
b = op('/project2/ui_perform').findChildren(name='btn_tab_*', depth=1)
print('text pars color:', [p.name for p in b[0].pars() if 'color' in p.name.lower() or 'bg' in p.name.lower()][:14] if b else 'sin botones')
