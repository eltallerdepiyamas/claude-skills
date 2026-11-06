# inspeccionar_onda.py — prueba el interruptor de onda/analisis y lo deja como estaba.
S = op('/project2/show'); U = op('/project2/ui_perform')
ver = S.par.Vermonitor.eval()
def e():
    print('Ver', S.par.Vermonitor.eval(), 'onda', U.op('onda').par.display.eval(), 'bandas', U.op('bandas').par.display.eval(), 'h', U.op('par_show_hub').par.h.eval())
for v in (False, True):
    S.par.Vermonitor = v
    U.op('ui_lib').module.ondas()
    e()
S.par.Vermonitor = ver
U.op('ui_lib').module.ondas()
x = U.op('onda_toggle')
print(x.errors() or 'sin errores')
