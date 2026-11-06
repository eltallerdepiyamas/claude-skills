# inspeccionar_ui.py — SOLO LEE (cambia de pagina y regresa): thumbs por pagina de ESCENA.
U = op('/project2/ui_perform')
m = U.op('ui_lib').module
def ver():
    print([c.name for c in U.children if c.name.startswith('th_escena_') and c.par.display.eval()])
m.elegir('PAG', 2); ver()
m.elegir('PAG', 1); ver()
t = U.op('th_escena_0')
print('tam', t.par.w.eval(), t.par.h.eval(), 'y', t.par.y.eval(), 'par_escena h', U.op('par_escena').par.h.eval())
m.tab('media', 'fx'); ver(); print('pag visible en fx', U.op('btn_pag_1').par.display.eval())
m.tab('media', 'escena'); ver()
print('click', (U.op('th_click').errors() or 'ok'), 'lib', (U.op('ui_lib').errors() or 'ok'))
