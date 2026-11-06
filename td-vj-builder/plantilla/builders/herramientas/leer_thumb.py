# leer_thumb.py — SOLO LEE: estado de un thumb.
c = op('/project2/ui_perform/th_escena_0')
i = c.op('img')
print(c.par.top.eval(), c.par.x.eval(), c.par.y.eval(), c.par.w.eval(), c.par.h.eval(), i.par.file.eval(), i.width, i.errors(), i.warnings())
print([p.name for p in c.pars() if 'top' in p.name.lower() or 'bg' in p.name.lower()])
