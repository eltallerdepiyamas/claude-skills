# ui_seguir_aire.py (2026-11-20) — la pestana de thumbs de la UI (CH9 ... CH13) SIGUE al visual al aire.
# Cuando cambia el visual al aire (piloto, cel, pad) y esta en otra pestana, la UI salta a la pestana de su canal.
# Si tu cambias de pestana a mano para buscar algo, no te regresa hasta el siguiente cambio de visual.
# Execute DAT /project2/ui_perform/seguir_aire (cada 10 cuadros, solo lee switch2.index). ui_bancos.py lo corre al final.
U = op('/project2/ui_perform')

CODIGO = r'''# seguir_aire — la pestana de thumbs sigue al visual al aire (builders/herramientas/ui_seguir_aire.py)
def pagina_de(idx):
    m = op('/project2/ui_perform/ui_lib').module
    for n, (canal, inicio, _t) in enumerate(m._PAGINAS):
        for slot in m._BANCOS[canal][inicio:inicio + 16]:
            if slot is not None and slot[1] == idx:
                return n
    return None


def revisar():
    u = op('/project2/ui_perform')
    idx = int(op('/project2/switch2').par.index.eval())
    if idx == me.fetch('ultimo', None, search=False):
        return
    me.store('ultimo', idx)                      # solo al CAMBIAR de visual: navegar a mano no se pelea
    p = pagina_de(idx)
    if p is not None and p != u.fetch('pagina_visual', 0, search=False):
        op('/project2/ui_perform/ui_lib').module.banco_set(p)


def onFrameEnd(frame):
    if frame % 10 == 0:
        try:
            revisar()
        except Exception as e:
            debug('seguir_aire', e)
    return
'''

if U is None or U.op('ui_lib') is None or not hasattr(U.op('ui_lib').module, '_PAGINAS'):
    print('[fallo] falta /project2/ui_perform/ui_lib con BANCOS (ui_bancos.py)')
else:
    e = U.op('seguir_aire') or U.create(executeDAT, 'seguir_aire')
    e.text = CODIGO
    e.par.framestart = False
    e.par.frameend = True
    e.par.active = True
    lib = U.op('ui_lib')
    e.nodeX, e.nodeY = lib.nodeX, lib.nodeY - 150
    e.store('ultimo', None)
    print('[ok] seguir_aire: la pestana de thumbs sigue al visual al aire ·', e.path)
