# revisar_audio_ui.py — SOLO LEE: que escena, visual y FX tengan pagina Audio y su pestana en la UI.
E = op('/project2/base17/escena_modular')
obj = [op('/project2/base%d' % i) for i in (1, 2, 18)] + [o for o in E.children if o.isCOMP and o.name.startswith('layout_')]
falta = [o.path for o in obj if 'Audio' not in [g.name for g in o.customPages]]
print('revisados', len(obj), '· sin pagina Audio:', falta)
U = op('/project2/ui_perform')
for n in ('par_visual', 'par_escena', 'par_fx'):
    c = U.op(n)
    if c is None:
        print(n, 'no existe')
        continue
    print(n, '|', c.par.pagescope.eval(), '| pestanas', c.par.pagenames.eval(), '| op', c.par.op.eval(), '|', c.par.parscope.eval()[-90:])
