# pads_seguros.py — un pad de visual o FX sin contenido no hace nada (asi no deja la salida en negro).
# Crea pad_lib y cambia cada chopexecN para que pase por ahi. Idempotente; prueba al final y deja todo como estaba.
import re
R = op('/project2')
L = R.op('pad_lib') or R.create(textDAT, 'pad_lib')
L.nodeX, L.nodeY = R.op('table1').nodeX, R.op('table1').nodeY - 160
L.text = '''# generado por builders/herramientas/pads_seguros.py
LIB = {'switch2': ('vis_knobs_lib', 'Visual'), 'switch23': ('fx_knobs_lib', 'Filter')}

def tiene_contenido(sw, k):
	if sw.name == 'switch23' and k == 0:      # sin FX
		return True
	if k >= len(sw.inputs):
		return False
	lib, pag = LIB[sw.name]
	b = op('/project2/' + lib).module.resolve(sw.inputs[k])
	return b is not None and any(p.name == pag for p in b.customPages)

def elegir(nombre, k):
	sw = op('/project2/' + nombre)
	if tiene_contenido(sw, k):
		sw.par.index = k
'''
pat = re.compile(r"op\('(switch2|switch23)'\)\.par\.index=(\d+)")
n = 0
for x in R.findChildren(name='chopexec*', depth=1):
    t = pat.sub(lambda m: "op('pad_lib').module.elegir('%s', %s)" % m.groups(), x.text)
    if t != x.text:
        x.text = t
        n += 1
print('chopexec cambiados', n)
m = L.module
s2, s23 = R.op('switch2'), R.op('switch23')
v, f = int(s2.par.index.eval()), int(s23.par.index.eval())
print('visuales con contenido', [k for k in range(16) if m.tiene_contenido(s2, k)])
print('FX con contenido', [k for k in range(16) if m.tiene_contenido(s23, k)])
m.elegir('switch23', 7)
print('pad vacio: fx sigue en', s23.par.index.eval(), '(esperado %d)' % f)
m.elegir('switch23', 1)
print('pad Trama: fx en', s23.par.index.eval(), '(esperado 1)')
s23.par.index = f
s2.par.index = v
print('restaurado visual', v, 'fx', f)
