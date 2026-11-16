# hoja_contacto.py: deja correr las bases indicadas unos segundos (feedback y simulaciones arrancan) y guarda una imagen
# de cada una en control/hoja/ (baseN_a.jpg a la mitad, baseN_b.jpg al final). Modulo en /project2/show/hoja_lib.
# Bases y cuadros: control/hoja/pedido.txt ("50 51 52 | 180"); si no existe, base50-65 y 90 cuadros.
import os
D = project.folder + '/control/hoja'
os.makedirs(D, exist_ok=True)
BASES, CUADROS = list(range(50, 66)), 90
if os.path.exists(D + '/pedido.txt'):
    t = open(D + '/pedido.txt').read().split('|')
    BASES = [int(x) for x in t[0].split()]
    if len(t) > 1 and t[1].strip():
        CUADROS = int(t[1])
CODE = '''import os
D = project.folder + '/control/hoja'

def paso(faltan, bases, total):
    for n in bases:
        b = op('/project2/base%d' % n)
        o = b.op('out1') if b else None
        if o is None:
            continue
        o.cook(force=True)
        if faltan in (total // 2, 0):
            o.save('%s/base%d_%s.jpg' % (D, n, 'a' if faltan else 'b'))
    if faltan > 0:
        run("op('%s').module.paso(%d, %r, %d)" % (me.path, faltan - 1, bases, total), delayFrames=1)
    else:
        open(D + '/listo.txt', 'w').write('ok')
'''
if os.path.exists(D + '/listo.txt'):
    os.remove(D + '/listo.txt')
S = op('/project2/show')
lib = S.op('hoja_lib') or S.create(textDAT, 'hoja_lib')
lib.nodeX, lib.nodeY = 200, -400
lib.text = CODE
lib.module.paso(CUADROS, BASES, CUADROS)
print('hoja de contacto en marcha:', BASES, CUADROS, 'cuadros')
