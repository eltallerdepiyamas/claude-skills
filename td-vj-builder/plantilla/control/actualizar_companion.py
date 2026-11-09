# =============================================================
# actualizar_companion.py  —  TD -> control/show.json (lo que el Stream Deck debe mostrar de ESTE show)
#
# 1. Copia control/oscin1_callbacks.py al DAT de callbacks de oscin1 (router de Companion).
# 2. Corre setup_companion_feedback.py (TD -> Companion: escena, camaras, slots) y setup_mix_feedback.py
#    (pagina MIX: los 5 parametros de lo activo con su porcentaje).
# 3. Escribe control/show.json:
#      layouts  = opciones del menu Modoescena (etiqueta = lo que manda el boton) y su familia
#                 (multiview / singlecam)
#      visuales = base1-16 que tienen contrato (pagina Visual / Contrato)
#      fx       = entradas de switch23 que llegan a un base con contrato (0 = base17 sin FX)
#      slots    = Slot1..5 de escena_modular y sus camaras
#      unica    = camaras de "Camara unica" (Menu2): la que se ve en los layouts single cam
# Despues, FUERA de TD:  python control/gen_companion.py  -> importar control/streamdeck.companionconfig
#
# Uso (Textport):
#   exec(open(project.folder + '/control/actualizar_companion.py', encoding='utf-8').read())
# =============================================================

import json, os, re

SCENE_PATH = '/project2/base17/escena_modular'
FX_SWITCH  = '/project2/switch23'
PAGES_OK   = ('Visual', 'Filter', 'Contrato')   # paginas que dicen "este base tiene contenido"
CTRL       = project.folder + '/control'


def _nombre(b):
    """Nombre para el boton: del builder (setup_baseN_<nombre>.py) o 'Base N'."""
    for d in b.findChildren(type=DAT, depth=1):
        f = getattr(d.par, 'file', None)
        m = re.search(r'setup_base\d+_(\w+)\.py', str(f.eval()) if f is not None else '')
        if m:
            return m.group(1).replace('_', ' ').title()
    for sub in ('visuales', 'efectos'):
        folder = project.folder + '/builders/' + sub
        for fname in (sorted(os.listdir(folder)) if os.path.isdir(folder) else []):
            m = re.match(r'setup_%s_(\w+)\.py$' % b.name, fname)
            if m:
                return m.group(1).replace('_', ' ').title()
    return b.name.replace('base', 'Base ')


def _tiene_contrato(b):
    return b is not None and any(pg.name in PAGES_OK for pg in b.customPages)


def _resolve(o):
    for _ in range(8):
        if o is None:
            return None
        if o.isCOMP and o.name.startswith('base'):
            return o
        if o.OPType == 'outTOP' and o.parent().name.startswith('base'):
            return o.parent()
        if o.OPType == 'selectTOP':
            o = o.par.top.eval()
            continue
        o = o.inputs[0] if o.inputs else None
    return None


def run():
    scene = op(SCENE_PATH)

    # 1. router OSC
    osc = scene.op('oscin1')
    cb = osc.par.callbacks.eval() if osc is not None and hasattr(osc.par, 'callbacks') else None
    if cb is not None:
        with open(CTRL + '/oscin1_callbacks.py', encoding='utf-8') as f:
            cb.text = f.read()
        print('[ok] router OSC actualizado (%s)' % cb.path)
    else:
        print('[aviso] no encontre oscin1 / su DAT de callbacks en', SCENE_PATH)

    # 2. feedback TD -> Companion (escena, camaras, slots) + pagina MIX (5 parametros de lo activo)
    # demo automatico de escenas + grabacion (pestaña Demo; botones DEMO / REC / FUENTE del MENU).
    # Va primero: companion_feedback vigila sus parametros
    exec(open(CTRL + '/setup_demo.py', encoding='utf-8').read(), dict(globals()))
    exec(open(CTRL + '/setup_companion_feedback.py', encoding='utf-8').read(), dict(globals()))
    exec(open(CTRL + '/setup_mix_feedback.py', encoding='utf-8').read(), dict(globals()))

    # 3. show.json
    p = scene.par.Modoescena
    def fam(n):
        c = scene.op(n)
        tag = next((t for t in (c.tags if c is not None else []) if t.startswith('tdvj_fam_')), '')
        if tag:
            return tag[len('tdvj_fam_'):]
        # sin tag (construido con una version vieja): single cam si todas sus camaras son SLOT_UNICA
        sels = [s for s in (c.findChildren(name='cam_in_*', depth=1) if c is not None else [])]
        tops = {s.par.top.eval().name for s in sels if s.par.top.eval() is not None}
        return 'singlecam' if tops == {'SLOT_UNICA'} else 'multiview'
    layouts = [{'name': n, 'label': l, 'familia': fam(n)} for n, l in zip(p.menuNames, p.menuLabels)]
    visuales = [{'base': n, 'nombre': _nombre(op('/project2/base%d' % n))}
                for n in range(1, 17) if _tiene_contrato(op('/project2/base%d' % n))]
    if os.path.exists(CTRL + '/bancos.json'):       # el show define sus paginas (ui_bancos.py)
        visuales = json.load(open(CTRL + '/bancos.json', encoding='utf-8'))
    fx = [{'index': 0, 'nombre': 'Sin FX'}]
    sw = op(FX_SWITCH)
    for i, src in enumerate(sw.inputs if sw is not None else []):
        b = _resolve(src)
        if i > 0 and _tiene_contrato(b):
            fx.append({'index': i, 'nombre': _nombre(b)})
    slots = [{'par': 'Slot%d' % i, 'opciones': list(getattr(scene.par, 'Slot%d' % i).menuLabels)}
             for i in range(1, 6) if getattr(scene.par, 'Slot%d' % i, None) is not None]
    m2 = getattr(scene.par, 'Menu2', None)
    unica = {'par': 'Menu2', 'opciones': list(m2.menuLabels)} if m2 is not None else None
    show = {'layouts': layouts, 'visuales': visuales, 'fx': fx, 'slots': slots, 'unica': unica}
    # nombres para la pagina MENU del Stream Deck (mix_feedback manda lo activo de cada pagina)
    scene.store('menu_nombres', {'fam': {l['label']: l['familia'] for l in layouts},
                                 'vis': {str(v['base']): v['nombre'] for v in visuales},
                                 'fx': {str(f['index']): f['nombre'] for f in fx}})
    with open(CTRL + '/show.json', 'w', encoding='utf-8') as f:
        json.dump(show, f, ensure_ascii=False, indent=1)
    print('[ok] control/show.json: %d layouts, %d visuales, %d FX, %d slots' % (
        len(layouts), len(visuales), len(fx) - 1, len(slots)))
    print('   ahora, fuera de TD:  python control/gen_companion.py   -> importar control/streamdeck.companionconfig')


run()
