# leer_click.py — diagnostico del click en thumbs de escena; deja la escena como estaba.
U = op('/project2/ui_perform')
E = op('/project2/base17/escena_modular')
m = U.op('ui_lib').module
c = U.op('th_escena_1')
print('th_escena_1 display', c.par.display.eval(), 'enable', c.par.enable.eval(), 'tags', list(c.tags), 'tipo', c.fetch('tipo', None, search=False), 'dato', c.fetch('dato', None, search=False), 'xywh', c.par.x.eval(), c.par.y.eval(), c.par.w.eval(), c.par.h.eval())
antes = E.par.Modoescena.eval()
m.elegir(c.fetch('tipo'), c.fetch('dato'))
print('elegir ->', E.par.Modoescena.eval(), '(antes', antes, ')')
E.par.Modoescena = antes
x0, y0, x1, y1 = c.par.x.eval(), c.par.y.eval(), c.par.x.eval() + c.par.w.eval(), c.par.y.eval() + c.par.h.eval()
print('encima:', [o.name for o in U.children if o.isCOMP and o != c and o.par.display.eval() and o.par.x.eval() < x1 and x0 < o.par.x.eval() + o.par.w.eval() and o.par.y.eval() < y1 and y0 < o.par.y.eval() + o.par.h.eval()])
px = U.op('th_click')
print('panels:', px.par.panels.eval(), 'value', px.par.panelvalue.eval(), 'active', px.par.active.eval(), 'exec', px.par.executeloc.eval(), 'err', px.scriptErrors()[:150])
for n in ('th_visual_0', 'th_fx_1'):
    q = U.op(n)
    print(n, q.par.display.eval() if q else None)
