# leer_fx_lib.py — SOLO LEE: la funcion knob_pars real de la lib de FX.
t = op('/project2/fx_knobs_lib').text
i = t.index('def knob_pars')
print(t[i:i + 640])
print('knobs dat:', op('/project2/base18').op('knobs'))
print('hay UI:', len(op('/project2/ui_perform').children), [c.name for c in op('/project2/ui_perform').children if c.name.startswith('prev')], op('/project2/ui_perform').errors()[:100])
print('captura:', op('/project2/td_mcp/captura_ui').par.opviewer.eval())
