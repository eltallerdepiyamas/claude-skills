# auditoria.py — SOLO LEE: revision completa del .toe para el boilerplate.
import re
vivos = [o for r in (op('/project1'), op('/project2')) for o in [r] + list(r.findChildren()) if '/_respaldo' not in o.path]
print('nodos vivos:', len(vivos), '· fps', round(project.cookRate, 1))
# 1 errores reales
for tit, f in (('errores', lambda o: o.errors(recurse=False) or o.scriptErrors(recurse=False)), ('avisos', lambda o: o.warnings(recurse=False))):
    l = [o.path for o in vivos if f(o) and '/audioAnalysis/' not in o.path]
    print(tit, len(l), l[:14])
# 2 referencias rotas / a cosas viejas
pat = re.compile(r"/project1/(null4|audio|midiin|Little|switch6)|/project2/(null19|null28|switch1\b|switch3\b)|master_out|escena_modular/switch1|lumalevel|V2_COLOR|lookup2")
malas, rotas = [], []
for o in vivos:
    for p in o.pars():
        try:
            t = p.expr if p.mode == ParMode.EXPRESSION else (p.bindExpr if p.mode == ParMode.BIND else (p.val if isinstance(p.val, str) else ''))
        except Exception:
            continue
        if t and pat.search(t):
            malas.append('%s.%s = %s' % (o.path, p.name, t[:70]))
        if p.mode == ParMode.CONSTANT and p.style in ('TOP', 'CHOP', 'DAT', 'COMP', 'OP') and p.val and not p.eval():
            rotas.append('%s.%s = %s' % (o.path, p.name, str(p.val)[:50]))
print('refs viejas', len(malas), malas[:12])
print('OP params rotos', len(rotas), rotas[:12])
for d in vivos:
    if d.isDAT and d.OPType in ('textDAT', 'executeDAT', 'chopexecuteDAT', 'parameterexecuteDAT', 'panelexecuteDAT'):
        try:
            if pat.search(d.text):
                print('  DAT con ref vieja:', d.path, pat.search(d.text).group(0))
        except Exception:
            pass
# 3 pads
R = op('/project2')
s2, s23 = R.op('switch2'), R.op('switch23')
print('switch2 entradas', len(s2.inputs), 'switch23', len(s23.inputs))
# 4 quien cocina caro ahora
E = op('/project2/base17/escena_modular'); f = absTime.frame
tops = sorted([(o.cookTime, o.path) for o in vivos if o.isTOP and f - o.cookAbsFrame <= 2], reverse=True)[:8]
print('caros AHORA:', [(round(t, 2), p.replace('/project2/base17/escena_modular', 'E')) for t, p in tops])
print('total TOPs cocinando', sum(1 for o in vivos if o.isTOP and f - o.cookAbsFrame <= 2))
pesados = [(o.path, o.width, o.height) for o in vivos if o.OPType == 'moviefileinTOP' and o.width > 1920]
print('videos >1080p:', pesados[:8])
# 5 estado
S = R.op('show')
print('Fuente', E.par.Fuente.eval(), '| audio', S.par.Audiofuente.eval(), 'gain', S.par.Audiogain.eval(), '| Master', S.par.Master.eval(), 'Brillo', S.par.Brillo.eval(), 'Sat', S.par.Saturacion.eval(), 'Contraste', S.par.Contraste.eval(), 'Negros', S.par.Negros.eval())
print('Demo', E.par.Demo.eval(), 'Rec', E.par.Rec.eval(), 'Readonly mcp', R.op('td_mcp').par.Readonly.eval(), 'perform', op('/perform').par.winop.eval())
print('respaldo con cook:', [c.name for c in R.op('_respaldo').children if c.isCOMP and c.allowCooking])
print('Text DATs con archivo faltante:', [o.path for o in vivos if o.isDAT and hasattr(o.par, 'file') and o.par.file.eval() and not __import__('os').path.exists(project.folder + '/' + str(o.par.file.eval())) and not __import__('os').path.isabs(str(o.par.file.eval()))][:8])
