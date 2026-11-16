# setup_beatstep_luces.py — el Beatstep prende lo que esta al aire: canal 9 = escena,
# canales 10 y 11 = visual y FX. Se manda a los 3 canales; se ve el del canal en que este el aparato.
# Requiere Out Device = Arturia BeatStep Pro en el renglon 2 del MIDI Mapper. Idempotente.
R = op('/project2')
d = R.op('bs_luces') or R.create(midioutCHOP, 'bs_luces')
d.par.id = 2
d.par.autonoteoff = 'none' if 'none' in d.par.autonoteoff.menuNames else 'off' if 'off' in d.par.autonoteoff.menuNames else d.par.autonoteoff.menuNames[0]
d.nodeX, d.nodeY = R.op('midi_midiin3').nodeX, R.op('midi_midiin3').nodeY - 240
ex = R.op('bs_luces_exec') or R.create(executeDAT, 'bs_luces_exec')
ex.nodeX, ex.nodeY = d.nodeX + 200, d.nodeY
ex.text = '''# generado por control/setup_beatstep_luces.py
E = '/project2/base17/escena_modular'

def deseados():
	out = set()
	i = op(E).par.Modoescena.menuIndex
	if i is not None and i < 16:
		out.add((9, 45 + i if i < 8 else 29 + i))
	k = int(op('/project2/switch2').par.index.eval())
	if k < 16:
		out.add((10, 45 + k) if k < 8 else (11, 37 + k))
	k = int(op('/project2/switch23').par.index.eval())
	if k < 16:
		out.add((10, 37 + k) if k < 8 else (11, 32 + k) if k < 13 else (11, 24 + k))
	return out

def onFrameEnd(frame):
	if frame % 6:
		return
	d = op('bs_luces')
	antes = me.fetch('prendidos', None, search=False)
	ahora = deseados()
	if antes is None:      # primer paso: apaga lo que hubiera
		antes = {(c, n) for c in (9, 10, 11) for n in range(37, 53)}
	for c, n in antes - ahora:
		d.sendNoteOff(c, n)
	for c, n in ahora:     # se repite: al soltar un pad el aparato apaga su luz
		d.sendNoteOn(c, n, 127)
	me.store('prendidos', ahora)
	return
'''
ex.unstore('prendidos')
for t in ('start', 'create', 'exit', 'framestart', 'playstatechange', 'devicechange', 'projectpresave', 'projectpostsave'):
    if hasattr(ex.par, t):
        setattr(ex.par, t, False)
ex.par.frameend = True
print('autonoteoff', d.par.autonoteoff.menuNames, d.par.autonoteoff.eval())
print('[ok] luces del Beatstep:', ex.module.deseados())
