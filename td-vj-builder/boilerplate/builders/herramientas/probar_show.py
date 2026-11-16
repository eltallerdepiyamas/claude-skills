# probar_show.py — prueba el hub /project2/show y deja todo como estaba.
S = op('/project2/show')
for o in (op('/project1/color_final'), op('/project1/audio_fuente'), op('/project1/audio_gain'), op('/project1/switch6'), op('/project1/null4'), S.op('color_midi')):
    e = (o.errors() or o.warnings() or '').strip()
    print('%-28s %s' % (o.path, e.splitlines()[0][:120] if e else 'OK'))
n4 = op('/project1/null4')
print('audio null4:', {c.name: round(c.eval(), 3) for c in n4.chans()[:4]})
print('audio_gain chans:', [c.name for c in op('/project1/audio_gain').chans()], 'rate', op('/project1/audio_gain').rate)
def res():
    return dict(escena=(op('/project2/base17/escena_modular').par.W.eval(), op('/project2/base17/escena_modular').par.H.eval()),
                layout=(op('/project2/base17/escena_modular/master_video').width, op('/project2/base17/escena_modular/master_video').height),
                base1=(op('/project2/base1/out1').width, op('/project2/base1/out1').height),
                ndi=(op('/project1/ndiout1').width, op('/project1/ndiout1').height))
w0, h0 = S.par.W.eval(), S.par.H.eval()
print('antes  ', res())
S.par.W, S.par.H = 1280, 720
for o in (op('/project1/ndiout1'), op('/project2/base17/escena_modular/master_video'), op('/project2/base1/out1')):
    o.cook(force=True)
print('1280x720', res())
S.par.W, S.par.H = w0, h0
print('regresado a %dx%d' % (w0, h0))
print('REC audio:', op('/project2/base17/escena_modular').par.Recaudiochop.eval())
