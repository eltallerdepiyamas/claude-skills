# probar_midi.py — SOLO LEE: canales y errores del MIDI movido y de quien lo lee.
for p in ('/project2/midi_midiin1', '/project2/midi_midiin2', '/project2/midi_midiin3', '/project1/midiin1', '/project1/null6', '/project2/vis_knobs_in'):
    o = op(p)
    e = (o.errors() or o.warnings() or '').strip()
    print('%-28s chans=%3d %s %s' % (p, o.numChans, [c.name for c in o.chans()][:6], e.splitlines()[0][:100] if e else 'OK'))
m = op('/project2/midi_midiin1')
print('device:', m.par.device.eval(), '| id:', m.par.id.eval(), '| active:', m.par.active.eval() if hasattr(m.par, 'active') else '-')
o = op('/project2/_respaldo/project1_midi/midiin1')
print('original (respaldo) device:', o.par.device.eval() if o else None, 'id', o.par.id.eval() if o else None)
