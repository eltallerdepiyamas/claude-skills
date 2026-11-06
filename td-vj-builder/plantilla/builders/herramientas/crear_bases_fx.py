# crear_bases_fx.py — base26-32 (FX) vacias y sin cook, cableadas a null44-50 -> switch23.
# Pads de las 3 ultimas: ch11 n37-39 (table1 filas 46-48). Idempotente.
R = op('/project2')
m = R.op('base25')
for i, n in enumerate(range(26, 33)):
    nul = R.op('null%d' % (44 + i))
    b = R.op('base%d' % n)
    if b is None:
        b = R.copy(m, name='base%d' % n)
    b.nodeX, b.nodeY = m.nodeX, nul.nodeY
    b.allowCooking = False
    nul.inputConnectors[0].connect(b.outputConnectors[0])
    print(b.name, '->', nul.name, 'cook', b.allowCooking, [c.name for c in b.children])
t = R.op('table1')
for fila, n in ((45, 37), (46, 38), (47, 39)):
    t[fila, 0] = 'ch11n%d' % n
print('tabla', [t[f, 0].val for f in (45, 46, 47)])
print('errores null', [o.name for o in (R.op('null%d' % k) for k in range(44, 51)) if o.errors()])
print('sin efecto en contenido', [k for k in range(16) if R.op('pad_lib').module.tiene_contenido(R.op('switch23'), k)])
