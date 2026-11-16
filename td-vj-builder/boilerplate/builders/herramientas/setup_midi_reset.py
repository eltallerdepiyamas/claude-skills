# setup_midi_reset.py: mapea dos notas del MIDImix a resets utiles.
#   ch1n27  -> Reset correccion de color (/project2/show.Resetcolor.pulse())
#   ch1n26  -> Reset parametros del visual (switch2) + FX (switch23) activos
# Idempotente. Crea en /project2:
#   reset_midi_sel  (selectCHOP de MIDI con ch1n27 y ch1n26)
#   reset_midi_exec (chopexecuteDAT que dispara en off-to-on)
MIDI = '/project2/midi_midiin1'   # MIDImix (el /project2/MIDI es el Beatstep; ch1n26/27 vienen de aqui)

p2 = op('/project2')
sel = p2.op('reset_midi_sel') or p2.create(selectCHOP, 'reset_midi_sel')
sel.par.chops = MIDI
sel.par.channames = 'ch1n27 ch1n26'
sel.nodeX, sel.nodeY = -800, -600

xx = p2.op('reset_midi_exec') or p2.create(chopexecuteDAT, 'reset_midi_exec')
xx.par.chops = sel
xx.par.offtoon = True
xx.par.ontooff = xx.par.whileon = xx.par.whileoff = xx.par.valuechange = False
xx.nodeX, xx.nodeY = -600, -600
xx.text = '''# generado por setup_midi_reset.py
# ch1n27 = reset correccion de color
# ch1n26 = reset parametros del visual (switch2) + FX (switch23) activos

def _reset_pars(comp):
    if comp is None:
        return 0
    n = 0
    for par in comp.customPars:
        try:
            if par.default is None or par.mode != ParMode.CONSTANT:
                continue
            if par.style in ('Pulse', 'Momentary'):
                continue
            par.val = par.default
            n += 1
        except Exception:
            pass
    return n

def _base_desde_switch(sw, offset):
    """Base activa del switch: para switch2 (visuales) la entrada N -> baseN+1;
    para switch23 (FX) la entrada 0 es sin FX, entradas >=1 son FX reales."""
    if sw is None:
        return None, None
    idx = int(sw.par.index.eval())
    if sw is op('/project2/switch23') and idx == 0:
        return None, 'sin FX'
    src = sw.inputs[idx] if idx < len(sw.inputs) else None
    base = src
    while base is not None and not (hasattr(base, 'isCOMP') and base.isCOMP and base.type == 'baseCOMP'):
        base = base.parent() if hasattr(base, 'parent') else None
    if base is None:
        return None, None
    return base, base.name

def onOffToOn(channel, sampleIndex, val, prev):
    name = channel.name
    if name == 'ch1n27':
        show = op('/project2/show')
        if show is not None and hasattr(show.par, 'Resetcolor'):
            show.par.Resetcolor.pulse()
            print('[reset color] /project2/show')
    elif name == 'ch1n26':
        total = 0
        vis_base, vis_name = _base_desde_switch(op('/project2/switch2'), 0)
        if vis_base is not None:
            n = _reset_pars(vis_base)
            total += n
            print('[reset visual] %s: %d pars' % (vis_name, n))
        fx_base, fx_name = _base_desde_switch(op('/project2/switch23'), 0)
        if fx_base is not None:
            n = _reset_pars(fx_base)
            total += n
            print('[reset fx] %s: %d pars' % (fx_name, n))
        elif fx_name == 'sin FX':
            print('[reset fx] sin FX activo, nada que resetear')

def whileOn(channel, sampleIndex, val, prev): return
def onOnToOff(channel, sampleIndex, val, prev): return
def whileOff(channel, sampleIndex, val, prev): return
def onValueChange(channel, sampleIndex, val, prev): return
'''

print('[OK] reset_midi_sel + reset_midi_exec listos.')
print('    ch1n27 -> Reset correccion de color')
print('    ch1n26 -> Reset parametros del visual + FX activos')
