# setup_beatstep_canal.py — recuerda el canal del ultimo pad tocado en el Beatstep (9, 10 u 11).
# Nodos bs_canal_* en /project2; bs_canal (Constant, canal 'canal') lo lee la barra de la UI. Idempotente.
R = op('/project2')
MIDI = R.op('midi_midiin3')


def nuevo(tipo, nombre, x, y):
    o = R.op(nombre)
    if o is not None:
        o.destroy()
    o = R.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


x, y = MIDI.nodeX, MIDI.nodeY - 120
val = nuevo(constantCHOP, 'bs_canal', x + 600, y)
val.par.const0name = 'canal'
val.par.const1name = 'pad'
sel = nuevo(selectCHOP, 'bs_canal_in', x, y)
sel.par.chop = MIDI.path
sel.par.channames = 'ch9n* ch10n* ch11n*'
ex = nuevo(chopexecuteDAT, 'bs_canal_exec', x + 200, y)
ex.text = '''# generado por control/setup_beatstep_canal.py
def onOffToOn(channel, sampleIndex, val, prev):
	n = channel.name.index('n')
	nota = int(channel.name[n + 1:])
	op('bs_canal').par.const0value = int(channel.name[2:n])
	op('bs_canal').par.const1value = nota - 44 if nota >= 45 else nota - 28   # 1-8 arriba, 9-16 abajo
	return
'''
ex.par.chop = sel.path
for t in ('ontooff', 'whileon', 'whileoff', 'valuechange'):
    setattr(ex.par, t, False)
ex.par.offtoon = True
ck = nuevo(executeDAT, 'bs_canal_cook', x + 400, y)
ck.text = "def onFrameStart(frame):\n\top('bs_canal_in').cook()\n\treturn\n"
for t in ('start', 'create', 'exit', 'frameend', 'playstatechange', 'devicechange', 'projectpresave', 'projectpostsave'):
    if hasattr(ck.par, t):
        setattr(ck.par, t, False)
ck.par.framestart = True
print('[ok] bs_canal; canales vistos:', sel.numChans)
