# setup_feedback_salto.py — interruptor que salta el Feedback global de /project1.
# feedback_HSV1 a 4608x1280 costaba ~17 ms de GPU por cuadro aunque el show no lo usa.
# /project1/feedback_salto (Switch TOP): index 0 = la senal pasa directo (Feedback sin cocinar)
#                                         index 1 = pasa por feedback_HSV1, como antes.
# Idempotente. QUITAR = True lo desmonta y deja la cadena original.
QUITAR = False
NOM = 'feedback_salto'

P = op('/project1')
F = P.op('feedback_HSV1')
sw = P.op(NOM)
if sw is not None and len(sw.inputs) < 2 and not sw.outputs:   # quedo a medias: rehacer
    sw.destroy()
    sw = None

if F is None:
    print('[fallo] no existe /project1/feedback_HSV1')
elif QUITAR:
    if sw is not None:
        for c in list(sw.outputConnectors[0].connections):
            c.connect(F)
        sw.destroy()
    print('[ok] feedback_salto quitado: cadena original')
elif sw is not None:
    print('[ok] feedback_salto ya estaba | index', int(sw.par.index.eval()))
elif not F.inputs:
    print('[fallo] feedback_HSV1 no tiene entrada')
else:
    src = F.inputs[0]
    destinos = list(F.outputConnectors[0].connections)
    sw = P.create(switchTOP, NOM)
    sw.nodeX, sw.nodeY = F.nodeX, F.nodeY - 160
    sw.inputConnectors[0].connect(src)
    sw.inputConnectors[1].connect(F.outputConnectors[0])
    sw.par.index = 0
    for c in destinos:
        c.connect(sw)
    sw.comment = '0 = sin Feedback (directo) · 1 = con Feedback'
    print('[ok] feedback_salto puesto | entrada', src.name, '| destinos', len(destinos))

# Video suelto de base17: sin salidas, costaba ~16 ms de CPU por cuadro.
m = op('/project2/base17/moviefilein1')
if m is not None and not QUITAR:
    if m.outputs:
        print('[aviso] moviefilein1 tiene salidas, no lo toco')
    else:
        m.par.play = False
        print('[ok] moviefilein1 en pausa')
