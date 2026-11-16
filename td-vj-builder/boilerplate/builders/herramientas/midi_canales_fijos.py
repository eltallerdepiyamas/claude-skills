# midi_canales_fijos.py — un MIDI In CHOP solo crea un canal cuando llega ese mensaje: si arranca vacio,
# las expresiones op('nullN')['ch1n25'] dan None y fallan switches / COMPs de /project1. Idempotente.
# En /project1, cada midiinN (Select que lee /project2/midi_midiinN) pasa a ser:
#   midiinN_cero (Constant: ch[1-16]n[0-127] y ch[1-16]ctrl[0-127] en 0) ─┐
#   midiinN_sel  (Select -> /project2/midi_midiinN, el MIDI en vivo)     ─┴─> midiinN (Merge, gana el vivo)
# El nombre midiinN y sus cables de salida no cambian.
P1 = op('/project1')
for i in (1, 2, 3):
    n = 'midiin%d' % i
    cur = P1.op(n)
    if cur is None:
        continue
    if cur.OPType == 'mergeCHOP':
        print('[=]', n, 'ya es merge')
        continue
    salidas = [(c.owner, c.index) for oc in cur.outputConnectors for c in oc.connections]
    x, y = cur.nodeX, cur.nodeY
    cur.name = n + '_sel'
    cero = P1.op(n + '_cero') or P1.create(constantCHOP, n + '_cero')
    cero.par.name0, cero.par.value0 = 'ch[1-16]n[0-127]', 0
    cero.par.name1, cero.par.value1 = 'ch[1-16]ctrl[0-127]', 0
    m = P1.create(mergeCHOP, n)
    m.inputConnectors[0].connect(cero)
    m.inputConnectors[1].connect(cur)
    dup = getattr(m.par, 'duplicate', None)
    if dup is not None:
        last = [v for v in dup.menuNames if 'last' in v.lower()]
        dup.val = last[0] if last else dup.menuNames[-1]
    for owner, idx in salidas:
        owner.inputConnectors[idx].connect(m)
    cero.nodeX, cero.nodeY = x - 200, y + 60
    cur.nodeX, cur.nodeY = x - 200, y - 60
    m.nodeX, m.nodeY = x, y
    m.comment = 'MIDI: canales fijos en 0 + MIDI en vivo de /project2/midi_%s (gana el vivo)' % n
    print('[ok] %s = merge(%s, %s) · %d canales · %d cables · duplicate=%s' % (
        n, cero.name, cur.name, m.numChans, len(salidas), dup.eval() if dup is not None else '?'))
