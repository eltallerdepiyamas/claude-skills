# =============================================================
# diag_camaras.py  —  SOLO LECTURA: que camaras hay en escena_modular y que recibe cada layout
# Uso (Textport):
#   exec(open(project.folder + '/control/escena_modular/diag_camaras.py', encoding='utf-8').read())
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'
m = op(SCENE_PATH)

print('=== camaras en escena_modular')
for c in sorted(m.children, key=lambda o: o.name):
    if c.isTOP and ('cam' in c.name.lower() or c.OPType in ('videodeviceinTOP', 'ndiinTOP', 'syphonspoutinTOP')):
        print('   %-12s [%s] %dx%d  ins=%s  errores: %s' % (
            c.name, c.OPType, c.width, c.height, [x.name for x in c.inputs],
            (c.errors() or 'ninguno').strip().splitlines()[0]))

print('\n=== parametros de camaras de escena_modular')
for p in m.customPars:
    if any(k in p.name.lower() for k in ('cam', 'index', 'menu2', 'int')):
        print('   %-22s %-28s = %s' % (p.name, p.label, p.eval()))

print('\n=== entradas de cada layout')
for lay in sorted((c for c in m.children if c.isCOMP and c.name.startswith('layout_')), key=lambda o: o.name):
    g = lay.op('glsl_layout')
    sels = [lay.op('cam_in_%d' % i) for i in range(1, 7) if lay.op('cam_in_%d' % i) is not None]
    desc = ', '.join('%s->%s%s' % (s.name, s.par.top.eval().name if s.par.top.eval() else '-',
                                   ' (ERR)' if s.errors() else '') for s in sels)
    print('   %-22s glsl entradas=%s  %s' % (lay.name, len(g.inputs) if g else '-', desc))
    if g is not None and g.errors():
        print('      glsl error: %s' % g.errors().strip().splitlines()[0])
