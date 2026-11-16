# vaciar_bases.py — deja vacias y sin cook las bases de BASES (solo se queda out1). Idempotente.
# Para cuando un visual cambia de base: vaciar la vieja y luego correr build_all.py.
BASES = []          # p. ej. [3] : las bases a vaciar
R = op('/project2')
for n in BASES:
    b = R.op('base%d' % n)
    if b is None:
        continue
    for c in list(b.children):
        if c.valid and c.name != 'out1':
            c.destroy()
    for g in list(b.customPages):
        g.destroy()
    b.allowCooking = False
    print('[ok] base%d vacia' % n)
