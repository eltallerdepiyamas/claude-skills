# leer_expr.py — SOLO LEE: parametros con expresion que hoy fallan en algunos COMPs de /project1.
for path in ('/project1/V2_COLOR', '/project1/blend_switch', '/project1/curcuitBending', '/project1/curcuitBending1'):
    o = op(path)
    for p in o.customPars:
        if p.mode == ParMode.EXPRESSION:
            try:
                v = p.eval()
                ok = v is not None
            except Exception:
                ok = False
            if not ok or p.name in ('Scene', 'Fx2', 'FX2', 'Ty', 'Amount', 'Power'):
                print(path, p.name, '|', p.expr[:110])
for n in ('null2', 'null6', 'null50', 'limit13', 'logic3'):
    o = op('/project1/' + n)
    print(n, o.numChans, [c.name for c in o.chans()][:6], [i.name for i in o.inputs])
