# quien_cocina.py — SOLO LEE: que layouts cocinaron en los ultimos frames (deben ser solo los activos).
E = op('/project2/base17/escena_modular')
f = absTime.frame
vivos = []
for l in E.children:
    if l.name.startswith('layout_'):
        g = l.op('glsl_layout')
        if g is not None and f - g.cookAbsFrame <= 3:
            vivos.append(l.name)
print('frame', f, '· activa', E.par.Modoescena.eval(), '· cocinando:', vivos)
