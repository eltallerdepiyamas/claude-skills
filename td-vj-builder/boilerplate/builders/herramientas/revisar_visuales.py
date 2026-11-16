# revisar_visuales.py — revision automatica de todos los pads de BANCOS (brillo, negro, saturado, movimiento,
# reaccion al audio, FPS, errores). Correr con musica sonando, antes de ensayar y antes de un show sin operador.
# Tarda ~5 s por visual (corre sola, cuadro por cuadro). Resultado: control/revision_visuales.md (y .json).
# Textport: exec(open(project.folder + '/builders/herramientas/revisar_visuales.py', encoding='utf-8').read())
S = op('/project2/show')
lib = S.op('revisar_visuales_lib')
if lib is None:
    lib = S.create(textDAT, 'revisar_visuales_lib')
    lib.nodeX, lib.nodeY = 0, -400
lib.text = open(project.folder + '/builders/herramientas/revisar_visuales_lib.py', encoding='utf-8').read().lstrip('﻿')
st = lib.fetch('rv', None, search=False)
if st and not st.get('fin') and st['i'] < len(st['lista']):
    print('ya hay una revision corriendo: %d/%d' % (st['i'], len(st['lista'])))
else:
    lib.module.arrancar()
    st = lib.fetch('rv', None, search=False)
    print('revision arrancada: %d visuales, ~%d s. Resultado en control/revision_visuales.md' % (len(st['lista']), len(st['lista']) * 5.5))
