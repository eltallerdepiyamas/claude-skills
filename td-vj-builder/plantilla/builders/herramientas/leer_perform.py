# leer_perform.py — SOLO LEE: que hay en la raiz y como esta el perform mode / midiin del MIDImix.
print('raiz:', [(c.name, c.OPType) for c in op('/').children])
for n in ('/perform', '/local', '/ui'):
    o = op(n)
    print(n, o.OPType if o else None)
p = op('/perform')
if p is not None:
    print('  winop=', p.par.winop.eval(), 'size', p.par.winw.eval(), p.par.winh.eval())
m = op('/project1/midiin1')
print('midiin1:', m.OPType if m else None, [(x.name, x.eval()) for x in m.pars('device', 'normalize', 'id', 'channel', 'controlind')] if m else '')
for n in ('Recaudio', 'Recaudiochop'):
    p = getattr(op('/project2/base17/escena_modular').par, n, None)
    print(n, p.eval() if p is not None else None, p.style if p is not None else '')
print('La_Magia file', op('/project1/Little_Jesus___La_Magia').par.file.eval())
print('ui container1 parent panel:', op('/project2/container1').par.w.eval())
