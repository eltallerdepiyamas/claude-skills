# fix_project1_final.py — curcuitBending lee el MIDI de /project2/control_p1 · V2_COLOR: null42 -> entrada 1, lookup2 -> entrada 2.
import re
P1, C = op('/project1'), op('/project2/control_p1')
names = sorted([o.name for o in C.children], key=len, reverse=True)
REL = re.compile(r"""op\((['"])(%s)\1\)""" % '|'.join(re.escape(n) for n in names))
ABS = re.compile(r"/project1/(%s)(?=[/\W]|$)" % '|'.join(re.escape(n) for n in names))
n = 0
for o in [P1.op('curcuitBending')] + list(P1.op('curcuitBending').findChildren()) + [P1.op('V2_COLOR'), P1.op('curcuitBending1')]:
    for p in o.pars():
        if p.mode == ParMode.EXPRESSION:
            t2 = ABS.sub(lambda m: '/project2/control_p1/' + m.group(1), REL.sub(lambda m: "op('/project2/control_p1/%s')" % m.group(2), p.expr))
            if t2 != p.expr:
                p.expr = t2
                n += 1
print('[ok] expresiones reescritas:', n)
v2 = P1.op('V2_COLOR')
v2.inputConnectors[1].connect(P1.op('null42'))
v2.inputConnectors[2].connect(P1.op('lookup2'))
print('V2_COLOR inputs:', [i.name for i in v2.inputs])
bad = []
for o in [P1] + list(P1.findChildren()):
    try:
        o.cook(force=True)
    except Exception:
        pass
for o in [P1] + list(P1.findChildren()):
    e = (o.errors(recurse=False) or o.scriptErrors(recurse=False) or '').strip()
    if e:
        bad.append('%s | %s' % (o.path, e.splitlines()[0][:110]))
print('errores en /project1:', len(bad))
for b in bad[:8]:
    print('  ', b)
