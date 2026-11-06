# inspeccionar_salida_negra.py — si visual o FX quedaron en una entrada vacia, los regresa a Formas / sin FX.
R = op('/project2')
s2, s23 = R.op('switch2'), R.op('switch23')
m = R.op('pad_lib').module
if not m.tiene_contenido(s2, int(s2.par.index.eval())):
    s2.par.index = 0
if not m.tiene_contenido(s23, int(s23.par.index.eval())):
    s23.par.index = 0
print('visual', s2.par.index.eval(), 'fx', s23.par.index.eval())
a = op('/project1/color_final').numpyArray()
print('brillo medio salida', round(float(a[..., :3].mean()), 3))
