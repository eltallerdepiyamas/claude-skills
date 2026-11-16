# =============================================================
# diag_escena.py  —  SOLO LECTURA: como estan armados el menu Modoescena, master_switch y blend_switch
# Imprime todo lo necesario para que los layouts se registren solos (menu + entradas de los switches).
# Uso (Textport):
#   exec(open(project.folder + '/control/escena_modular/diag_escena.py', encoding='utf-8').read())
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'
m = op(SCENE_PATH)


def src(o, i):
    ins = o.inputConnectors
    if i < len(ins) and ins[i].connections:
        c = ins[i].connections[0].owner
        return c.parent().name + '/out1' if c.name == 'out1' and c.parent() is not m else c.name
    return '-'


def pars(o):
    out = []
    for p in o.pars():
        if p.isCustom or p.page is None or p.page.name in ('Common', 'Extensions', 'Layout', 'Look', 'Panel', 'Children'):
            continue
        if p.mode == ParMode.EXPRESSION:
            out.append('%s = `%s` (%s)' % (p.name, p.expr, p.eval()))
        elif p.mode == ParMode.BIND:
            out.append('%s bind `%s`' % (p.name, p.bindExpr))
        elif p.mode == ParMode.EXPORT:
            out.append('%s export' % p.name)
        elif p.isNumber and p.eval() != p.default:
            out.append('%s=%s' % (p.name, p.eval()))
    return out


p = m.par.Modoescena
print('=== menu Modoescena (%d opciones), ahora: %s [%d]' % (len(p.menuNames), p.eval(), p.menuIndex))
print('    menuSource: %r' % getattr(p, 'menuSource', ''))
for i, (n, l) in enumerate(zip(p.menuNames, p.menuLabels)):
    print('   %2d %-28s %-24s %s' % (i, n, l, 'existe' if m.op(n) is not None else '(no existe op)'))

print('\n=== hijos de escena_modular (COMPs)')
print('   ' + ', '.join(sorted(c.name for c in m.children if c.isCOMP)))

ms = m.op('master_switch')
if ms is not None:
    print('\n=== master_switch [%s]  index: %s' % (ms.OPType, pars(ms)))
    for i in range(len(ms.inputConnectors)):
        print('   in %2d <- %s' % (i, src(ms, i)))
    print('   sale a: %s' % [c.owner.path for oc in ms.outputConnectors for c in oc.connections])

b = m.op('blend_switch')
if b is not None:
    print('\n=== blend_switch [%s]  custom: %s' % (b.OPType, ['%s=%s' % (q.name, q.eval()) for q in b.customPars]))
    print('   entradas del COMP:')
    for i, ic in enumerate(b.inputConnectors):
        print('   in %2d (%s) <- %s' % (i, ic.inOP.name if ic.inOP is not None else '?', src(b, i)))
    print('   sale a: %s' % [c.owner.path for oc in b.outputConnectors for c in oc.connections])
    print('   --- adentro:')
    for o in sorted(b.children, key=lambda o: (o.nodeY * -1, o.nodeX)):
        ins = [x.name for x in o.inputs]
        print('   %-14s [%s] <- %s  %s' % (o.name, o.OPType, ins, '; '.join(pars(o))[:300]))
        if o.isDAT and o.OPType in ('chopexecuteDAT', 'parameterexecuteDAT', 'executeDAT', 'textDAT'):
            print('      texto: %s' % o.text.strip().replace('\n', ' | ')[:400])

print('\n=== otros que leen Modoescena / blend_switch / master_switch')
for o in op('/project2').findChildren(depth=None):
    if o.path.startswith(SCENE_PATH + '/blend_switch') or o.path.startswith('/project2/_respaldo'):
        continue
    for q in o.pars():
        t = q.expr if q.mode == ParMode.EXPRESSION else ''
        if t and ('Modoescena' in t or 'blend_switch' in t or 'master_switch' in t):
            print('   %s.%s = %s' % (o.path, q.name, t))
