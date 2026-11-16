# click1.py — simula el click real (onOffToOn) en la escena 2 y guarda la escena anterior.
U = op('/project2/ui_perform'); E = op('/project2/base17/escena_modular')
E.store('antes_prueba', E.par.Modoescena.eval())
c = U.op('th_escena_1')
class V: owner = c
U.op('th_click').module.onOffToOn(V())
print('tras click:', E.par.Modoescena.eval(), '| Scene blend:', E.op('blend_switch').par.Scene.expr or E.op('blend_switch').par.Scene.eval())
print('pars panel exec:', [(p.name, p.eval()) for p in U.op('th_click').pars('offtoon', 'ontooff', 'whileon', 'valuechange', 'panelvalue')])
print('hijo enable:', c.op('img_p').par.enable.eval(), '| ui enable', U.par.enable.eval())
