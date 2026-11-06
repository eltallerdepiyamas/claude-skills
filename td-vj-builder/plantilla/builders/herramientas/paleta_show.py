# paleta_show.py — pestana Paleta en /project2/show: Color A, Color B y Rampa mandan sobre todos los visuales. Idempotente.
R = op('/project2')
S = R.op('show')
import json
_p = json.load(open(project.folder + '/proyecto.json', encoding='utf-8'))['paleta']['colores']
pg = next((g for g in S.customPages if g.name == 'Paleta'), None) or S.appendCustomPage('Paleta')
if not hasattr(S.par, 'Colorar'):
    for nombre, etiqueta, rgb in (('Colora', 'Color A', tuple(_p[0]['rgb'])), ('Colorb', 'Color B', tuple(_p[1]['rgb']))):
        t = pg.appendRGB(nombre, label=etiqueta)
        for p, v in zip(t, rgb):
            p.default = v
            p.val = v
    p = pg.appendFloat('Rampa', label='Rampa A a B')[0]
    p.normMin, p.normMax, p.min, p.max, p.clampMin, p.clampMax = 0, 1, 0, 1, True, True
    p.default = 0
n = 0
for k in range(1, 17):
    b = R.op('base%d' % k)
    if b is None or not hasattr(b.par, 'Color1r'):
        continue
    for c in 'rgb':
        a, d = 'op("/project2/show").par.Colora%s' % c, 'op("/project2/show").par.Colorb%s' % c
        getattr(b.par, 'Color1' + c).expr = '%s + (%s - %s) * op("/project2/show").par.Rampa' % (a, d, a)
        getattr(b.par, 'Color2' + c).expr = d
    n += 1
S.sortCustomPages('Correccion de color', 'Paleta', 'Audio', 'Resolucion')
print('visuales ligados', n, 'B', S.par.Colorbr.eval(), S.par.Colorbg.eval(), S.par.Colorbb.eval())
print('base1 Color1', R.op('base1').par.Color1r.eval(), R.op('base1').par.Color1g.eval(), R.op('base1').par.Color1b.eval())
