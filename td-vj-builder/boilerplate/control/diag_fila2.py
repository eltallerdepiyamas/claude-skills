# =============================================================
# diag_fila2.py  —  SOLO LECTURA: por que una fila del MIDImix no mueve lo activo
# Gira los knobs 1-5 de la fila un poco antes de correrlo.
# Uso (Textport):
#   exec(open(project.folder + '/control/diag_fila2.py', encoding='utf-8').read())   -> fila 2 (FX)
#   LINE = 'vis'; exec(...)                                                          -> fila 1 (visuales)
# =============================================================

try:
    LINE
except NameError:
    LINE = 'fx'
P, KN, SW = {'fx': ('fx_knobs', ('ch1ctrl18', 'ch1ctrl22', 'ch1ctrl26', 'ch1ctrl30', 'ch1ctrl48'), 'switch23'),
             'vis': ('vis_knobs', ('ch1ctrl17', 'ch1ctrl21', 'ch1ctrl25', 'ch1ctrl29', 'ch1ctrl47'), 'switch2')}[LINE]
LINE = 'fx'

root = op('/project2')
names = [P + s for s in ('_lib', '_map', '_in', '_lag', '_exec', '_parexec', '_cook')]
print('Nodos:', ', '.join('%s=%s' % (n, 'ok' if root.op(n) else 'FALTA') for n in names))

midi = op('/project2/midi_midiin1')
print('midiin1: %d canales; normalize=%s' % (midi.numChans, getattr(midi.par, 'normalize', None) and midi.par.normalize.eval()))
for ch in KN:
    c = midi[ch]
    print('   %s en midiin1: %s' % (ch, 'no llega' if c is None else round(c.eval(), 3)))

sel, lag, ex = root.op(P + '_in'), root.op(P + '_lag'), root.op(P + '_exec')
if sel is not None:
    print('%s_in: %s  errores: %s' % (P, [(c.name, round(c.eval(), 3)) for c in sel.chans()], sel.errors() or 'ninguno'))
if lag is not None:
    print('%s_lag: %s' % (P, [(c.name, round(c.eval(), 3)) for c in lag.chans()]))
if ex is not None:
    print('%s_exec: active=%s chop=%s valuechange=%s  errores: %s' % (
        P, ex.par.active.eval(), ex.par.chop.eval(), ex.par.valuechange.eval(), ex.scriptErrors() or 'ninguno'))

lib = root.op(P + '_lib')
if lib is not None:
    m = lib.module
    sw = op('/project2/' + SW)
    b = m.active_base()
    print('%s index=%s -> activo: %s' % (SW, sw.par.index.eval(), b.path if b else None))
    for i, p in enumerate(m.knob_pars(b)):
        print('   K%d -> %s' % (i + 1, '%s = %s (%.0f%%)' % (p.name, p.eval(), m.get_norm(p) * 100) if p is not None else 'nada'))
    print('takeover: knobs que ya agarraron = %s' % sorted(k + 1 for k in m.state['armed']))
    calls = m.state.get('calls')
    if calls is None:
        print('on_knob: version vieja sin contador (volver a correr el fase3)')
    else:
        print('on_knob: %d llamadas, ultima = %s%s' % (calls, m.state.get('last'),
              '   [!] %s_exec no la esta llamando' % P if calls == 0 else ''))
        print('   estado: base=%s prev=%s' % (m.state['base'], {k + 1: round(v, 3) for k, v in m.state['prev'].items()}))
