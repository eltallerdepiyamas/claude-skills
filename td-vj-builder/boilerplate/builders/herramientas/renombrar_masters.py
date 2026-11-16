# renombrar_masters.py — estandar master_<que manda>. Renombra y reescribe referencias (no toca _respaldo). Idempotente.
import re
RN = [('/project2/base17/escena_modular', 'master_out', 'master_video'), ('/project2/audio', 'null4', 'master_audio'),
      ('/project2', 'null19', 'master_visuales'), ('/project2', 'null28', 'master_fx')]
n = 0
def fix(t, o):
    for net, a, b in RN:
        t = re.sub(re.escape(net + '/' + a) + r'(?![\w])', net + '/' + b, t)
        if o.parent().path == net:
            t = re.sub(r"(op\(['\"])%s(['\"]\))" % a, r'\g<1>%s\2' % b, t)
    return t
ops = [o for r in (op('/project1'), op('/project2')) for o in r.findChildren() if '/_respaldo' not in o.path]
for o in ops:
    for p in o.pars():
        try:
            if p.mode == ParMode.EXPRESSION:
                t = fix(p.expr, o)
                if t != p.expr: p.expr = t; n += 1
            elif p.mode == ParMode.BIND:
                t = fix(p.bindExpr, o)
                if t != p.bindExpr: p.bindExpr = t; n += 1
            elif p.mode == ParMode.CONSTANT and isinstance(p.val, str) and p.val:
                t = fix(p.val, o)
                for net, a, b in RN:
                    if o.parent().path == net and t == a and p.style in ('TOP', 'CHOP', 'OP'):
                        t = b
                if t != p.val: p.val = t; n += 1
        except Exception:
            pass
    if o.isDAT and o.OPType in ('textDAT', 'executeDAT', 'chopexecuteDAT', 'parameterexecuteDAT') and not o.par.syncfile.eval() if hasattr(o.par, 'syncfile') else False:
        t = fix(o.text, o)
        if t != o.text: o.text = t; n += 1
for net, a, b in RN:
    x = op(net).op(a)
    if x is not None:
        x.name = b
print('[ok] referencias:', n, '·', [op(net).op(b).path for net, a, b in RN])
