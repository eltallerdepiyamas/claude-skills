# leer_ui.py — SOLO LEE: que quedo en los paneles de ui_perform (parametros con valor/expresion y errores).
U = op('/project2/ui_perform')
for n in ('tit_escena', 'prev_escena', 'par_escena', 'par_show'):
    o = U.op(n)
    print('==', n, o.OPType, (o.errors() or o.warnings() or o.scriptErrors() or 'sin errores').strip()[:200])
    for p in o.pars():
        if p.page is None or p.page.name in ('Layout', 'Look', 'Panel', 'Children', 'Drag/Drop', 'Extensions', 'Common'):
            continue
        v = p.eval()
        mode = 'expr:' + p.expr if p.mode == ParMode.EXPRESSION else ''
        if mode or (v not in ('', None, 0, False) and v != p.default):
            print('   %-18s %-12s %s %s' % (p.name, p.page.name, str(v)[:60], mode[:100]))
    if o.OPType == 'parameterCOMP':
        print('   todos los pars de', o.OPType, ':', [p.name for p in o.pars() if p.page and p.page.name not in ('Layout', 'Panel', 'Look', 'Children', 'Drag/Drop', 'Extensions', 'Common')][:40])
    if o.OPType == 'textCOMP':
        print('   pars de texto:', [p.name for p in o.pars() if 'text' in p.name.lower()][:20])
