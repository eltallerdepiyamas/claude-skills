# ui_tabs_default.py — UI en ESCENA + CORRECCION; dice si Destellos reacciona al audio.
m = op('/project2/ui_perform/ui_lib').module
m.tab('show', 'color'); m.tab('media', 'escena')
b = op('/project2/base2')
print('Destellos: Energy', round(b.par.Energy.eval(), 3), 'Audioreact', b.par.Audioreact.eval(), 'bandas L/M/H', b.par.Low.eval() if hasattr(b.par,'Low') else '?')
print('FX Trama errores:', (op('/project2/base18/glsl1').errors() or 'OK')[:90], '· src', op('/project2/base18/src_in').par.top.eval())
b18 = op('/project2/base18')
pg = next(g for g in b18.customPages if g.name == 'Filter')
print('Filter:', [(p.name, p.style, p.isFloat) for p in pg.pars][:9])
print('mix five:', [p.name if p else None for p in op('/project2/base17/escena_modular/mix_feedback').module.five(b18)])
