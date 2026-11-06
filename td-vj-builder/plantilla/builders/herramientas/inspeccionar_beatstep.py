# inspeccionar_beatstep.py — SOLO LEE: luces, canal/pad y lo activo.
x = op('/project2/bs_luces_exec')
print('luces', x.fetch('prendidos', None, search=False), '|', (x.errors() or x.scriptErrors() or 'sin errores').strip()[:150])
b = op('/project2/bs_canal')
print('canal', b['canal'].eval(), 'pad', b['pad'].eval())
print('activo', op('/project2/base17/escena_modular').par.Modoescena.eval(), op('/project2/switch2').par.index.eval(), op('/project2/switch23').par.index.eval())
