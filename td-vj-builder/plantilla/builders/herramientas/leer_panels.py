# leer_panels.py — cuantos paneles escucha el click y si incluye las imagenes.
px = op('/project2/ui_perform/th_click')
v = px.par.panels.eval()
print(len(v), [o.path.split('/')[-2] + '/' + o.name for o in v][:3], 'img_p enable', op('/project2/ui_perform/th_escena_1/img_p').par.enable.eval())
