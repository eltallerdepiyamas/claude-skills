# ordenar_hub.py — orden del hub show: Reset antes de Ultimo MIDI, separadores por categoria,
# y Ultimo MIDI detecta MIDImix y Beatstep. Idempotente; no cambia valores. Lo corre setup_show.py.
c = op('/project2/show')
ORDEN = {
    'Correccion de color': [('Sepcorreccion', 'Correccion'), 'Colorbypass', 'Brillo', 'Contraste', 'Negros', 'Saturacion',
                            'Master', 'Resetcolor', ('Sepmidi', 'Monitor MIDI'), 'Ultimomidi'],
    'Audio': [('Sepfuente', 'Fuente'), 'Audiofuente', 'Audioarchivo', 'Audiodriver', 'Audiodevice',
              ('Sepnivel', 'Nivel'), 'Audiogain', 'Audiomonitor',
              ('Sepvista', 'Vista'), 'Vermonitor'],
}
if not hasattr(c.par, 'Vermonitor'):
    p = next(g for g in c.customPages if g.name == 'Audio').appendToggle('Vermonitor', label='Ver onda y analisis')[0]
    p.default = True
    p.val = True
for g in c.customPages:
    if g.name in ORDEN:
        nombres = []
        for x in ORDEN[g.name]:
            if isinstance(x, tuple):
                if not hasattr(c.par, x[0]):
                    g.appendHeader(x[0], label=x[1])
                x = x[0]
            nombres.append(x)
        g.sort(*nombres)
u = c.op('midi_ultimo')
u.par.chops = '/project2/midi_midiin1 /project2/midi_midiin3'
u.text = '''# generado por builders/herramientas/ordenar_hub.py
QUIEN = {'midi_midiin1': 'MIDIMIX', 'midi_midiin3': 'BEATSTEP'}

def onValueChange(channel, sampleIndex, val, prev):
	if 'aftertouch' in channel.name:
		return
	parent().par.Ultimomidi = '%s  %s' % (QUIEN.get(channel.owner.name, channel.owner.name), channel.name)
	return
'''
print({g.name: [p.name for p in g.pars] for g in c.customPages})
print('par_show:', [(o.name, o.par.parscope.eval()) for o in op('/project2/ui_perform').findChildren(name='par_show_*', depth=1)])
print('MIDI out:', [[k.val for k in r] for r in op('/local/midi/device').rows()])
