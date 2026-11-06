# leer_textos.py — SOLO LEE. Imprime el texto de algunos DATs para revisar antes de cambiarlos.
NOMBRES = ['/project2/chopexec1', '/project2/chopexec9', '/project2/chopexec17', '/project2/chopexec41',
           '/project2/chopexec36', '/project2/vis_knobs_lib', '/project2/folder1_callbacks']
for n in NOMBRES:
    o = op(n)
    print('=' * 20, n, '=' * 20)
    if o is None:
        print('(no existe)')
        continue
    t = o.text
    print(t if len(t) < 6000 else t[:6000] + '\n...[%d chars]' % len(t))
w = op('/perform')
print('== /perform ==', w, [(p.name, p.eval()) for p in w.pars('winop', 'winw', 'winh', 'size', 'borders')] if w else '')
c = op('/project2/container1')
print('== container1 ==', [(p.name, p.eval()) for p in c.pars('w', 'h', 'align')], [ch.name for ch in c.children])
for n in ('opviewer1', 'opviewer2', 'opviewer3', 'opviewer4', 'parameter1', 'parameter2', 'parameter3', 'parameter4', 'button1', 'button2'):
    o = op('/project2/' + n)
    print('  ', n, [(p.name, p.eval()) for p in o.pars('x', 'y', 'w', 'h')], 'panelparent=', o.panelParent())
