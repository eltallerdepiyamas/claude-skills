# leer_audio_p1.py — SOLO LEE: como entra el audio a audioAnalysis y que CC del MIDImix estan ocupados.
import re
P1 = op('/project1')
for n in ('switch6', 'math30', 'null4', 'null2', 'null6', 'null50', 'trigger1', 'constant3', 'comp3', 'ndiout1', 'lumalevel1'):
    o = P1.op(n)
    if o is None:
        print(n, '(no existe)'); continue
    ins = [i.name for i in o.inputs]
    extra = ''
    if o.OPType == 'switchCHOP': extra = 'index=%s' % (o.par.index.expr or o.par.index.eval())
    if o.isTOP: extra = 'res=%dx%d' % (o.width, o.height)
    if o.isCHOP: extra += ' chans=%s' % [c.name for c in o.chans()][:12]
    print('%-12s %-18s in=%s %s' % (n, o.OPType, ins, extra))
lv = P1.op('lumalevel1')
print('lumalevel1 pars no-default:', [(p.name, p.expr if p.mode == ParMode.EXPRESSION else round(p.eval(), 3) if isinstance(p.eval(), float) else p.eval()) for p in lv.pars() if p.page and p.page.name in ('Level', 'Pre', 'RGBA') and (p.mode != ParMode.CONSTANT or p.eval() != p.default)])
usados = set()
for root in (op('/project1'), op('/project2')):
    for o in root.findChildren():
        if '/_respaldo' in o.path:
            continue
        for p in o.pars():
            try:
                t = p.expr if p.mode == ParMode.EXPRESSION else (str(p.val) if p.style in ('Str', 'StrMenu') else '')
            except Exception:
                t = ''
            for m in re.findall(r'ch1ctrl(\d+)', t or ''):
                usados.add(int(m))
        if o.isDAT:
            try:
                for m in re.findall(r'ch1ctrl(\d+)', o.text):
                    usados.add(int(m))
            except Exception:
                pass
mm = [16, 17, 18, 20, 21, 22, 24, 25, 26, 28, 29, 30, 46, 47, 48, 50, 51, 52, 54, 55, 56, 58, 59, 60, 19, 23, 27, 31, 49, 53, 57, 61, 62]
print('MIDImix CC usados:', sorted(c for c in usados if c in mm))
print('MIDImix CC LIBRES:', [c for c in mm if c not in usados])
print('otros CC ch1 usados:', sorted(c for c in usados if c not in mm))
