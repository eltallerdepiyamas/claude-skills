# =============================================================
# diag_beatstep.py  —  SOLO LECTURA: por que los pads del canal 9 no cambian la Escena activa
# Toca (y deja presionado) un pad del canal 9 mientras corres esto, o tocalo y correlo enseguida.
# Uso (Textport):
#   exec(open(project.folder + '/control/diag_beatstep.py', encoding='utf-8').read())
# =============================================================

midi = op('/project2/midi_midiin3')
scene = op('/project2/base17/escena_modular')
print('midiin3:', 'FALTA' if midi is None else '%d canales' % midi.numChans)
if midi is not None:
    por_canal = {}
    for c in midi.chans():
        canal = c.name.split('n')[0] if c.name.startswith('ch') and 'n' in c.name else c.name[:4]
        por_canal.setdefault(canal, []).append(c.name)
    for canal in sorted(por_canal):
        notas = [n for n in por_canal[canal] if 'n' in n and 'aftertouch' not in n and 'ctrl' not in n]
        if notas:
            print('   %-6s notas: %s' % (canal, ', '.join(notas[:20])))
    ch9 = [c for c in midi.chans() if c.name.startswith('ch9n')]
    print('canal 9:', 'NO LLEGA NADA (revisa que los pads del Beatstep esten en el canal 9)' if not ch9 else
          'llegan %s' % ', '.join('%s=%g' % (c.name, c.eval()) for c in ch9))
for n in ('bs_escenas_in', 'bs_escenas_exec', 'bs_escenas_cook'):
    o = scene.op(n)
    print('%-16s %s' % (n, 'FALTA (corre setup_beatstep_escenas.py)' if o is None else
                        'ok  errores: %s' % ((o.errors() or '') + (o.scriptErrors() if o.isDAT else '') or 'ninguno')))
sel = scene.op('bs_escenas_in')
if sel is not None:
    print('bs_escenas_in recibe:', [(c.name, c.eval()) for c in sel.chans()] or 'nada (las notas no coinciden con 37-52)')
