# recocinar_p1.py — fuerza cook de lo que tenia error en /project1 y dice si sigue fallando.
for path in ('/project1/V2_COLOR', '/project1/blend_switch', '/project1/curcuitBending', '/project1/curcuitBending1',
             '/project1/switch1', '/project1/switch5', '/project1/switch10', '/project1/switch12'):
    o = op(path)
    for p in o.customPars:
        if p.mode == ParMode.EXPRESSION:
            try:
                p.eval()
            except Exception:
                pass
    o.cook(force=True, recurse=True)
    e = (o.errors(recurse=True) or o.scriptErrors(recurse=True) or '').strip()
    print('%-28s %s' % (path, e.splitlines()[0][:110] if e else 'OK'))
