# limpiar_muertos_lj.py — quita restos que solo marcaban error o aviso. Idempotente.
C = op('/project2/control_p1')
for o in C.children:
    if o.OPType == 'countCHOP' and o.par.limitmax.mode == ParMode.EXPRESSION and ('POST_VFX' in o.par.limitmax.expr or 'blend_switch' in o.par.limitmax.expr):
        o.par.limitmax.expr = ''
        o.par.limitmax.mode = ParMode.CONSTANT
        o.par.limitmax = 16
        print('[ok]', o.name, 'limitmax fijo')
n = op('/project1/ndiout1')
n.par.grouptable = op('/project1/ndiout1_grouptable').path if op('/project1/ndiout1_grouptable') is not None else ''
for o in (op('/project2/control_p1/count%d' % i) for i in (1, 4, 6, 7, 12)):
    if o is not None:
        o.cook(force=True)
        e = (o.errors(recurse=False) or o.scriptErrors(recurse=False) or '').strip()
        print(o.name, e[:120] if e else 'OK', '| limitmax', o.par.limitmax.expr or o.par.limitmax.eval())
print('ndi aviso:', (n.warnings() or 'ninguno').strip()[:110])
f = op('/project2/base1/shader_frag')
print('base1 shader:', f.par.file.eval(), 'sync', f.par.syncfile.eval(), (f.warnings() or '').strip()[-70:])
print('your_video:', (op('/project2/base17/animated_displacement_map2/your_video').warnings() or '').strip()[:110])
d = op('/project2/base17/animated_displacement_map2')
print('displacement salidas:', [k.owner.path for oc in d.outputConnectors for k in oc.connections])
