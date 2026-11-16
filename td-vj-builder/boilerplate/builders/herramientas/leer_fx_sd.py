# leer_fx_sd.py — SOLO LEE: que ve el Stream Deck / MIDImix del FX activo.
F = op('/project2/fx_knobs_lib').module
sw = op('/project2/switch23')
print('switch23 index', sw.par.index.eval(), 'activo', F.active_base())
print('knob_pars base18:', [p.name if p else None for p in F.knob_pars(op('/project2/base18'))])
E = op('/project2/base17/escena_modular')
print('foco', E.fetch('mix_foco_manual', '', search=False, storeDefault=False), '| mix_comp', E.fetch('mix_comp', '', search=False, storeDefault=False))
