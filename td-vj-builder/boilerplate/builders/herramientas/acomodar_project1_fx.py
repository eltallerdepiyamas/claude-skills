# acomodar_project1_fx.py — /project1 = FX globales: una fila de izquierda a derecha + rampas abajo. Solo mueve.
P1 = op('/project1')
for a in [o for o in P1.children if o.OPType == 'annotateCOMP']:
    a.destroy()
print('V2_COLOR inputs:', [i.name for i in P1.op('V2_COLOR').inputs])
fila = ['select47', 'select2', 'feedback_HSV1', 'null42', 'lookup2', 'V2_COLOR', 'curcuitBending1', 'color_final', 'ndiout1']
for k, n in enumerate(fila):
    o = P1.op(n)
    if o is not None:
        o.nodeX, o.nodeY = k * 260, 0 if n != 'select47' else 260
        o.color = (0.91, 0.45, 0.11)
P1.op('null42').nodeY, P1.op('lookup2').nodeY = 160, -160
for n, (x, y) in {'color_final_frag': (7 * 260, -200), 'color_final_info': (7 * 260, -330), 'color_final_pixel': (7 * 260, -460),
                  'color_final_compute': (7 * 260, -590), 'ndiout1_grouptable': (8 * 260, -200),
                  'switch5': (4 * 260, -420), 'base6': (4 * 260, -300), 'blend_switch2': (3 * 260, -560), 'blend_switch3': (3 * 260, -700)}.items():
    o = P1.op(n)
    if o is not None:
        o.nodeX, o.nodeY = x, y
for i in range(1, 33):
    r, k = P1.op('ramp%d' % i), P1.op('ramp%d_keys' % i)
    c, row = (i - 1) % 16, (i - 1) // 16
    if r is not None:
        r.nodeX, r.nodeY = c * 160, -900 - row * 300
        r.color = (0.85, 0.64, 0.0)
    if k is not None:
        k.nodeX, k.nodeY = c * 160, -1020 - row * 300
err = []
for o in [P1] + list(P1.findChildren()):
    e = (o.errors(recurse=False) or o.scriptErrors(recurse=False) or '').strip()
    if e:
        err.append('%s | %s' % (o.path, e.splitlines()[0][:110]))
print('errores en /project1: %d' % len(err))
for e in err[:12]:
    print('  ', e)
for p in ('/project2/control_p1', '/project2/audio'):
    o = op(p)
    n = sum(1 for c in o.findChildren() if (c.errors(recurse=False) or c.scriptErrors(recurse=False)))
    print(p, 'hijos', len(o.children), 'con error', n)
