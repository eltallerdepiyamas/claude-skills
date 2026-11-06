# click2.py — revisa si el cambio se sostuvo y regresa la escena.
E = op('/project2/base17/escena_modular')
print('sigue en:', E.par.Modoescena.eval(), '| blend Scene =', E.op('blend_switch').par.Scene.eval(), '| index menu =', E.par.Modoescena.menuIndex)
E.par.Modoescena = E.fetch('antes_prueba')
