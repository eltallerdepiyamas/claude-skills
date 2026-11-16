# auditar_resolucion.py — SOLO LECTURA: que sigue a la resolucion del show (/project2/show → Resolucion) y que no.
#   1) salidas clave: su tamano real contra la maestra
#   2) bases (visuales / FX): Salida → Resw / Resh ligados o sueltos
#   3) TOPs con resolucion "custom" escrita a mano (numero fijo): esos NO siguen al show
# Textport:  exec(open(project.folder + '/builders/herramientas/auditar_resolucion.py', encoding='utf-8').read())
S = op('/project2/show')
W, H = int(S.par.W.eval()), int(S.par.H.eval())
print('maestra (show): %d x %d' % (W, H))

CLAVE = ['/project2/master_visuales', '/project2/master_fx', '/project2/base17/out1',
         '/project2/base17/escena_modular/master_out', '/project2/base17/escena_modular/master_video',
         '/project1/select2', '/project1/select47', '/project1/color_final', '/project1/ndiout1']
print('── salidas')
for p in CLAVE:
    o = op(p)
    if o is None:
        continue
    o.cook(force=True)
    print('  %-52s %4d x %-4d %s' % (p, o.width, o.height, 'ok' if (o.width, o.height) == (W, H) else '<< NO COINCIDE'))

print('── bases')
ligadas, sueltas, vacias = [], [], 0
for n in range(1, 33):
    b = op('/project2/base%d' % n)
    if b is None:
        continue
    if getattr(b.par, 'Resw', None) is None:
        vacias += 1
        continue
    if b.par.Resw.mode.name == 'EXPRESSION' and b.par.Resh.mode.name == 'EXPRESSION':
        ligadas.append(b.name)
    else:
        sueltas.append('%s (%dx%d fijo)' % (b.name, b.par.Resw.eval(), b.par.Resh.eval()))
print('  ligadas a la maestra:', ', '.join(ligadas) or '-')
print('  SUELTAS:', ', '.join(sueltas) or '-')
print('  sin contenido:', vacias)

print('── TOPs con resolucion fija (custom en numero)')
SALTAR = ('/project2/_respaldo', '/project2/ui_perform', '/project2/td_mcp', '/project2/audio')
fijos = []
for raiz in ('/project1', '/project2'):
    for o in op(raiz).findChildren(type=TOP):
        if o.path.startswith(SALTAR) or '/thumb' in o.path or 'res_propia' in o.tags:   # res_propia: tamano fijo a proposito
            continue
        pr = getattr(o.par, 'outputresolution', None)
        if pr is None or pr.eval() != 'custom':
            continue
        if o.par.resolutionw.mode.name == 'CONSTANT' or o.par.resolutionh.mode.name == 'CONSTANT':
            fijos.append('  %-64s %d x %d' % (o.path, o.par.resolutionw.eval(), o.par.resolutionh.eval()))
print('\n'.join(fijos) if fijos else '  ninguno')
