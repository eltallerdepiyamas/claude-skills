# ─────────────────────────────────────────────────────────────
# mover_midi_a_project2.py — el MIDI vive en /project2 (bloque CONTROL) sin romper nada. Idempotente.
# Por cada MIDI In CHOP de /project1 (midiin1...):
#   1. se copia a /project2 como midi_<nombre> (mismos parametros: dispositivo, canales...)
#   2. en /project1 queda un Select CHOP con EL MISMO NOMBRE que lee esa copia, con sus mismas
#      salidas (cables) -> op('midiin1'), '/project1/midiin1' y los selects que lo leen siguen igual.
# Lo de /project2 que leia /project1/midiin1 (vis_knobs_in, fx_knobs_in, show/color_midi) se
# apunta directo a la copia. No borra knobs ni botones. El original va a _respaldo/project1_midi.
# ─────────────────────────────────────────────────────────────
P1, P2 = op('/project1'), op('/project2')
ancla = P2.op('MIDI')
x0, y0 = (ancla.nodeX, ancla.nodeY - 260) if ancla is not None else (0, 0)
movidos = []
for k, m in enumerate([o for o in P1.children if o.OPType == 'midiinCHOP']):
    nombre, dest = m.name, 'midi_' + m.name
    nuevo = P2.op(dest) or P2.copy(m, name=dest)
    nuevo.nodeX, nuevo.nodeY = x0 + k * 200, y0
    nuevo.color = (0.45, 0.45, 0.45)
    nuevo.comment = 'MIDI movido de /project1/%s (alli queda un Select con ese nombre)' % nombre
    salidas = [(c.owner, c.index) for oc in m.outputConnectors for c in oc.connections]
    x, y = m.nodeX, m.nodeY
    r = P2.op('_respaldo')
    d = r.op('project1_midi') or r.create(baseCOMP, 'project1_midi')
    d.allowCooking = False
    d.copyOPs([m])
    m.destroy()
    s = P1.create(selectCHOP, nombre)
    s.par.chops = nuevo.path
    s.nodeX, s.nodeY = x, y
    s.comment = 'Lee %s (el MIDI vive en /project2)' % nuevo.path
    for owner, idx in salidas:
        owner.inputConnectors[idx].connect(s)
    movidos.append((nombre, nuevo.path, len(salidas)))
# lo de /project2 que leia /project1/midiin1 -> directo a la copia
for path, par in (('/project2/vis_knobs_in', 'chops'), ('/project2/fx_knobs_in', 'chops'), ('/project2/show/color_midi', 'chops')):
    o = op(path)
    if o is not None and str(o.par.chops.eval() or o.par.chops.val).endswith('/project1/midiin1') and P2.op('midi_midiin1'):
        o.par.chops = '/project2/midi_midiin1'
for n, p, c in movidos:
    print('[ok] /project1/%s -> %s  (en /project1 queda Select "%s" con %d cables)' % (n, p, n, c))
for path in ('/project2/vis_knobs_in', '/project2/fx_knobs_in', '/project2/show/color_midi'):
    o = op(path)
    if o is not None:
        print('    %s lee %s · canales %d' % (path, o.par.chops.eval(), o.numChans))
print('[ok] originales en /project2/_respaldo/project1_midi')
