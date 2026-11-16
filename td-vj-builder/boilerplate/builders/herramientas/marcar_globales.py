# marcar_globales.py — hace GRANDES y turquesa los operadores de datos globales, para hallarlos al abrir
# un show, y reporta los nodos que mas tiempo de cook gastan (solo lee en esa parte). Idempotente.
GLOBALES = {
    '/project2/show': 'HUB: resolucion · audio · color',
    '/project2/ui_perform': 'UI de perform',
    '/project2/audio': 'Audio: dispositivo y analisis',
    '/project2/control_p1': 'MIDI / control de FX globales',
    '/project2/table1': 'Notas de los pads',
    '/project2/base17/escena_modular': 'Camaras · lugares · escenas · demo/REC',
}
for path, txt in GLOBALES.items():
    o = op(path)
    if o is None:
        print('[!] no existe', path)
        continue
    x, y = o.nodeCenterX, o.nodeCenterY
    o.nodeWidth, o.nodeHeight = 320, 220
    o.nodeCenterX, o.nodeCenterY = x, y
    o.color = (0.08, 0.72, 0.72)
    o.comment = 'GLOBAL · ' + txt
    print('[ok] grande:', path)

filas = []
for r in (op('/project1'), op('/project2')):
    for o in r.findChildren(depth=4):
        if '/_respaldo' in o.path or o.isCOMP:
            continue
        filas.append((o.cookTime if hasattr(o, 'cookTime') else 0.0, o.path))
filas.sort(reverse=True)
print('fps', round(project.cookRate, 1), '· nodos mas caros (ms):')
for t, p in filas[:12]:
    print('  %7.2f  %s' % (t, p))
r = op('/project2/_respaldo')
print('respaldo con cook:', [c.name for c in r.children if c.isCOMP and c.allowCooking])
