# leer_levels.py — SOLO LEE: level1 / level2 y midiin1 activo.
for n in ('level1', 'level2'):
    o = op('/project2/' + n)
    print(n, 'bypass', o.bypass, [(p.name, p.expr if p.mode == ParMode.EXPRESSION else round(p.eval(), 3)) for p in o.pars() if p.page and p.page.name in ('Pre', 'Range', 'Post', 'RGBA') and isinstance(p.eval(), (int, float)) and (p.mode != ParMode.CONSTANT or p.eval() != p.default)][:8])
m = op('/project2/midi_midiin1')
print('ch actuales:', [c.name for c in m.chans()][:60])
print('faders map:', [[c.val for c in r] for r in op('/project2/base17/escena_modular/scene_faders_map').rows()][:7])
