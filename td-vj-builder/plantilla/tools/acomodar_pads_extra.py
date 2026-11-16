"""Acomoda los trios de pads extra (sw 24-31) siguiendo el patron de los originales 17-24.
Idempotente."""
p2 = op('/project2')

# Patron: trios 17-24 usan X=(-820,-620,-420) empezando en Y=-5310, step -140.
# Continuamos despues del trio 24 (Y=-6290) con step -140 para los 8 trios nuevos.
X_C, X_L, X_X = -820, -620, -420
Y_START = -6290 - 140   # un paso debajo del ultimo original
STEP = -140

# (sw_input, constant_name, logic_name, chopexec_name)
MAP = [
    (24, 'constant37', 'logic75', 'chopexec41'),
    (25, 'constant38', 'logic77', 'chopexec42'),
    (26, 'constant25', 'logic25', 'chopexec27'),
    (27, 'constant26', 'logic26', 'chopexec28'),
    (28, 'constant27', 'logic27', 'chopexec29'),
    (29, 'constant28', 'logic28', 'chopexec30'),
    (30, 'constant29', 'logic29', 'chopexec31'),
    (31, 'constant30', 'logic30', 'chopexec32'),
]

for i, (sw, c_name, l_name, x_name) in enumerate(MAP):
    y = Y_START + i * STEP
    for name, x in ((c_name, X_C), (l_name, X_L), (x_name, X_X)):
        n = p2.op(name)
        if n is not None:
            n.nodeX, n.nodeY = x, y
    print(f'  sw{sw:2d}  {c_name:10s} {l_name:8s} {x_name:10s}  y={y}')

# reset_midi_sel / reset_midi_exec: al lado, a la izquierda de los trios, como bloque aparte
sel = p2.op('reset_midi_sel')
ex = p2.op('reset_midi_exec')
if sel: sel.nodeX, sel.nodeY = X_C - 300, Y_START
if ex:  ex.nodeX, ex.nodeY = X_L - 300, Y_START
print(f'  reset_midi_sel / reset_midi_exec a la izquierda en y={Y_START}')
