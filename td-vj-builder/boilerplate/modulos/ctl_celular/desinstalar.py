# ctl_celular/desinstalar.py — quita el control del celular: PLAY si estaba en pausa, level1 vuelve a recibir lo que
# entraba a pausa_sw, fuera pausa_sw / pausa_cache y /project2/show/celular. La pagina Avisos del hub se queda
# (sus valores, como el tema de ntfy, sirven si se reinstala).
R = op('/project2')
S = R.op('show')
C = S.op('celular') if S is not None else None
hecho = []
if C is not None and C.op('web_callbacks') is not None:
    try:
        C.op('web_callbacks').module.pausar(False)
        hecho.append('PLAY')
    except Exception as e:
        print('[aviso] PLAY:', e)
sw, lv = R.op('pausa_sw'), R.op('level1')
if sw is not None and lv is not None and sw.inputs and lv.inputs and lv.inputs[0] == sw:
    lv.inputConnectors[0].connect(sw.inputs[0])
    hecho.append('level1 <- ' + sw.inputs[0].name)
for n in ('pausa_sw', 'pausa_cache'):
    if R.op(n) is not None:
        R.op(n).destroy()
        hecho.append('fuera ' + n)
if C is not None:
    C.destroy()
    hecho.append('fuera show/celular')
print('[ok] ctl_celular desinstalado:', hecho or 'no habia nada')
