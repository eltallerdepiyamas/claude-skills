# leer_zonas.py — SOLO LEE: caja de cada recuadro zona_* de /project2 y si se enciman.
R = op('/project2')
z = sorted([o for o in R.children if o.OPType == 'annotateCOMP'], key=lambda a: -a.nodeY)
cajas = []
for a in z:
    x0, y0, x1, y1 = a.nodeX, a.nodeY, a.nodeX + a.nodeWidth, a.nodeY + a.nodeHeight
    cajas.append((a.name, x0, y0, x1, y1))
    print('%-22s %-48s x %6d..%6d   y %6d..%6d' % (a.name, a.par.Titletext.eval()[:48], x0, x1, y0, y1))
for i in range(len(cajas)):
    for j in range(i + 1, len(cajas)):
        a, b = cajas[i], cajas[j]
        if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
            print('ENCIMADAS:', a[0], b[0])
fuera = [o.name for o in R.children if o.OPType != 'annotateCOMP' and not any(c[1] <= o.nodeX <= c[3] and c[2] <= o.nodeY <= c[4] for c in cajas)]
print('nodos fuera de todo recuadro:', fuera)
