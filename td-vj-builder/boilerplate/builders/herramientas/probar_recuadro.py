# probar_recuadro.py — reinicia la extension de los recuadros zona_* y cuenta cuantos marcan error.
R = op('/project2')
z = [o for o in R.children if o.OPType == 'annotateCOMP']
for a in z:
    a.par.reinitextensions.pulse()
print('reiniciados', len(z))
print('con error:', [a.name[:30] for a in z if (a.scriptErrors() or a.errors())])
