# respaldo_sin_cook.py — apaga el cook de lo que esta en /project2/_respaldo (no corre, no marca errores).
# Para revivir algo: copiarlo de vuelta a su lugar (o allowCooking = True en su COMP).
r = op('/project2/_respaldo')
for c in r.children:
    if c.isCOMP:
        c.allowCooking = False
print('[ok] sin cook:', ', '.join(c.name for c in r.children if c.isCOMP))
print('--- chopexec9 ---')
print(op('/project2/chopexec9').text.split('def whileOn')[0])
print('switch2 inputs:', [i.name for i in op('/project2/switch2').inputs], 'index', op('/project2/switch2').par.index.eval())
