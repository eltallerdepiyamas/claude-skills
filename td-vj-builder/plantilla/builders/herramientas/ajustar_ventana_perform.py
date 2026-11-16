# ajustar_ventana_perform.py — la UI (1920x1080) se ve cortada en Perform Mode cuando Windows tiene
# la pantalla escalada (125 %, 150 %...): TD multiplica la UI por esa escala y ya no cabe.
# Pone la ventana /perform en resolucion nativa (1 px de la UI = 1 px de la pantalla), sin bordes,
# en el monitor principal. Solo toca parametros de /perform. Imprime lo que encontro y lo que cambio.
# Textport:  exec(open(project.folder + '/builders/herramientas/ajustar_ventana_perform.py', encoding='utf-8').read())
w = op('/perform')
u = op('/project2/ui_perform')
print('monitores:', ['%dx%d dpi=%s%s' % (m.width, m.height, getattr(m, 'dpiScale', '?'), ' (principal)' if m.isPrimary else '') for m in monitors])
if w is None or u is None:
    print('[fallo] falta /perform o /project2/ui_perform')
else:
    print('UI: %dx%d' % (u.par.w.eval(), u.par.h.eval()))
    antes = {}
    def pon(nombre, pista):
        p = getattr(w.par, nombre, None)
        if p is None:
            return
        antes[nombre] = p.eval()
        for n in p.menuNames:
            if pista in n.lower():
                p.val = n
                return
    pon('dpiscaling', 'native')
    if hasattr(w.par, 'borders'):
        antes['borders'] = w.par.borders.eval()
        w.par.borders = False
    w.par.winop = u.path
    print('[ok] /perform ajustada | antes:', antes, '| dpiscaling ahora:', w.par.dpiscaling.eval() if hasattr(w.par, 'dpiscaling') else 'no existe')
    prim = [m for m in monitors if m.isPrimary]
    if prim and (prim[0].width < u.par.w.eval() or prim[0].height < u.par.h.eval()):
        print('[aviso] la pantalla principal (%dx%d) es mas chica que la UI: no va a caber completa sin escalarla' % (prim[0].width, prim[0].height))
    print('Sal de Perform Mode (Esc) y vuelve a entrar (F1) para que tome el cambio.')
