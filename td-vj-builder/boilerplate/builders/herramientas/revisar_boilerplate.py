# revisar_boilerplate.py — fuente en solidos, cuenta errores reales y guarda.
E = op('/project2/base17/escena_modular')
E.par.Fuente = 'solido' if 'solido' in E.par.Fuente.menuNames else E.par.Fuente.menuNames[0]
print('Fuente', E.par.Fuente.eval(), E.par.Fuente.menuNames)
vivos = [o for r in (op('/project1'), op('/project2')) for o in r.findChildren() if o.name != 'td_mcp']
print('errores', [(o.path, (o.errors(recurse=False) or '').strip()[:70]) for o in vivos if o.errors(recurse=False)][:12])
a = op('/project1/color_final').numpyArray()
print('brillo salida', round(float(a[..., :3].mean()), 3), '| respaldo', len(op('/project2/_respaldo').children))
project.save(project.folder + '/BOILERPLATE.toe')
print(project.name)
