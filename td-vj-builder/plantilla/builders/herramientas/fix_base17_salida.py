# fix_base17_salida.py — la salida de escena en base17 venia de un OP Viewer TOP (opview1) que
# "fotografiaba" la vista del COMP escena_modular: con otra proporcion de panel la imagen salia
# corrida (arriba cortada, franja oscura abajo). Ahora: Select TOP 'escena_out' -> master_out
# (pixeles directos, siempre a la resolucion maestra). opview1 -> /project2/_respaldo/base17_opview.
# base17/switch1 es tambien la fuente por default de los FX (tdvj_core.CAMERA_SWITCH). Idempotente.
B = op('/project2/base17')
sw = B.op('switch1')
sel = B.op('escena_out') or B.create(selectTOP, 'escena_out')
sel.par.top = '/project2/base17/escena_modular/master_out'
ov = B.op('opview1')
if ov is not None:
    sel.nodeX, sel.nodeY = ov.nodeX, ov.nodeY - 120
sw.inputConnectors[0].connect(sel)
sel.comment = 'Salida de escena_modular (master_out), pixeles directos'
if ov is not None:
    r = op('/project2/_respaldo')
    d = r.op('base17_opview') or r.create(baseCOMP, 'base17_opview')
    d.copyOPs([ov])
    d.allowCooking = False
    ov.destroy()
    print('[ok] opview1 -> /project2/_respaldo/base17_opview')
print('[ok] base17/switch1 <-', [i.path for i in sw.inputs], ' %dx%d' % (sel.width, sel.height))
# visor temporal para capturar la UI de perform con el MCP (vive dentro de td_mcp)
t = op('/project2/td_mcp')
cap = t.op('captura_ui') or t.create(opviewerTOP, 'captura_ui')
cap.par.opviewer = '/project2/ui_perform'
cap.par.outputresolution = 'custom'
cap.par.resolutionw, cap.par.resolutionh = 1920, 1080
print('[ok] visor de captura: /project2/td_mcp/captura_ui')
