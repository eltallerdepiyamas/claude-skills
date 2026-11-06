# errores_vivos.py — SOLO LEE. Errores / warnings de /project2 y /project1 SIN contar _respaldo.
def scan(root):
    n = 0
    for o in [root] + list(root.findChildren()):
        if '/_respaldo' in o.path:
            continue
        e = (o.errors(recurse=False) or '').strip()
        w = (o.warnings(recurse=False) or '').strip()
        s = (o.scriptErrors(recurse=False) or '').strip()
        if e or w or s:
            n += 1
            print(' ', o.path, '|', (e or s or w).splitlines()[0][:160])
    return n
for r in ('/project2', '/project1'):
    print('==', r, '==')
    print('  total:', scan(op(r)))
