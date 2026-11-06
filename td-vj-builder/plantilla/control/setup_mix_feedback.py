# =============================================================
# setup_mix_feedback.py  —  TD -> Companion: los 5 parametros de lo activo, con su porcentaje (pagina MIX)
#
# "Foco" = lo ultimo que cambiaste: el layout (Escena activa), el visual (switch2) o el FX (switch23).
# Desde el Stream Deck tambien se elige el foco a mano (botones LAYOUT / VISUAL / FX -> /td/foco).
# Manda a Companion (custom variables):
#   mix_foco         LAYOUT / VISUAL / FX
#   mix_foconombre   nombre de lo enfocado (p. ej. Luna, base1)
#   mix_p1n..p5n     nombre de cada parametro      mix_p1v..p5v   su valor en %
#   mix_audio        que parametro empuja el audio (1-5, 0 = audio apagado)
#   mix_audioon      ON / OFF (Audioreact)         mix_audiomult  sensibilidad (Audiomult)
#   visual / fx      base del visual activo / entrada de switch23: el boton correcto se enciende
#                    aunque el cambio venga del Beatstep o del mouse
#   mix_ir           sube 1 cada vez que cambia la escena, el visual o el FX
# Salto a MIX desde el Beatstep / mouse: TD manda /location/1/1/0/press (la etiqueta "IR A MIX" de la
# pagina 1, que hace Set page MIX en el Stream Deck). No hace falta ningun Trigger en Companion.
# Los 5 parametros: los del contrato (Mezcla... Firma) o los 5 primeros de su pagina Layout / Visual /
# Filter (orden de rol). Manda lo que cambio unas 6 veces por segundo, y todo cada ~2 s.
#
# Requiere: setup_companion_feedback.py (crea companion_out). Lo corre actualizar_companion.py.
# Uso (Textport):
#   exec(open(project.folder + '/control/setup_mix_feedback.py', encoding='utf-8').read())
# Se puede volver a correr: recrea solo su propio operador.
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'

CODE = r'''# generado por control/setup_mix_feedback.py — pagina MIX del Stream Deck
SCENE    = op(%(scene)r)
SW_VIS   = op('/project2/switch2')
SW_FX    = op('/project2/switch23')
CONTRACT = ['Mezcla', 'Tiempo', 'Distorsion', 'Color', 'Firma']
EVERY    = 5          # frames entre envios (~6 por segundo a 30 fps)


def resolve(o):
    """Sigue la senal hasta el baseNN: en un Switch TOP la entrada elegida, en un Select TOP su TOP."""
    for _ in range(16):
        if o is None:
            return None
        if o.isCOMP and o.name.startswith('base'):
            return o
        if o.OPType == 'outTOP' and o.parent().name.startswith('base'):
            return o.parent()
        if o.OPType == 'selectTOP':
            o = o.par.top.eval()
            continue
        ins = o.inputs
        if not ins:
            return None
        k = min(max(int(o.par.index.eval()), 0), len(ins) - 1) if o.OPType == 'switchTOP' else 0
        o = ins[k]
    return None


def five(comp):
    if comp is None:
        return []
    if all(getattr(comp.par, n, None) is not None for n in CONTRACT):
        return [getattr(comp.par, n, None) for n in CONTRACT]
    pg = next((g for g in comp.customPages if g.name in ('Layout', 'Visual', 'Filter')), None)
    if pg is None:
        return []
    return [p for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')][:5]


def pct(p):
    lo, hi = p.normMin, p.normMax
    if lo == hi:
        lo, hi = p.min, p.max
    return '' if hi == lo else '%%d%%%%' %% round(max(0.0, min(1.0, (float(p.eval()) - lo) / (hi - lo))) * 100)


def short(label):
    # '1 Glow' -> 'Glow' (el numero ya lo da la posicion del boton)
    parts = label.split(' ', 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else label


def onFrameEnd(frame):
    if frame %% EVERY:
        return
    out = SCENE.op('companion_out')
    if out is None:
        return
    p = getattr(SCENE.par, 'Modoescena', None)
    lay = SCENE.op(p.eval()) if p is not None else None
    vis, fx = resolve(SW_VIS), resolve(SW_FX)
    now = {'layout': lay.path if lay else '', 'visual': vis.path if vis else '', 'fx': fx.path if fx else ''}

    foco = me.fetch('mix_foco', 'layout', storeDefault=True)
    last = me.fetch('mix_last', None, storeDefault=False)
    cambio = False
    if last:
        for k in ('layout', 'visual', 'fx'):
            if last.get(k) != now[k]:
                foco = k                              # lo ultimo que cambio se enfoca solo
                cambio = True
    if cambio:
        # aviso para el Trigger de Companion "cuando cambie mix_ir -> ir a la pagina MIX":
        # asi el Stream Deck salta a MIX aunque el cambio venga del Beatstep
        n = me.fetch('mix_ir', 0, storeDefault=True) + 1
        me.store('mix_ir', n)
        out.sendOSC('/custom-variable/mix_ir/value', [str(n)])
        # cambio desde el Beatstep / mouse: "presiona" el boton MIX de la pagina 1 (MENU) del Stream Deck.
        # Si vino del Stream Deck no hace falta: sus botones ya saltan solos.
        if absTime.seconds - SCENE.fetch('deck_t', -99, search=False, storeDefault=False) > 1.0:
            out.sendOSC('/location/1/1/0/press', [1])
    manual = SCENE.fetch('mix_foco_manual', None, search=False, storeDefault=False)
    orden = ('layout', 'visual', 'fx')
    if manual == 'next':                              # tocar el nombre en MIX: el siguiente
        foco = orden[(orden.index(foco) + 1) %% 3] if foco in orden else 'layout'
    elif manual in orden:
        foco = manual
    if manual is not None:
        SCENE.unstore('mix_foco_manual')
    me.store('mix_last', now)
    me.store('mix_foco', foco)

    comp = {'layout': lay, 'visual': vis, 'fx': fx}[foco]
    if foco == 'layout' and p is not None and comp is not None:
        nombre = p.menuLabels[p.menuIndex]
    else:
        nombre = comp.name if comp is not None else '-'
    SCENE.store('mix_comp', comp.path if comp is not None else '')    # lo usa /td/audio (oscin1)
    # todo en MAYUSCULAS (asi se lee igual en todo el Stream Deck)
    # el layout se muestra como su familia (MULTIVIEW / SINGLE CAM): cada una tiene su color en el Stream Deck
    fams = (SCENE.fetch('menu_nombres', {}, search=False, storeDefault=False) or {}).get('fam', {})
    if foco == 'layout':
        fam_lay = fams.get(p.menuLabels[p.menuIndex], 'multiview') if p is not None else 'multiview'
        foco_txt = 'SINGLE CAM' if fam_lay == 'singlecam' else 'MULTIVIEW'
    else:
        foco_txt = foco.upper()
    vals = {'foco': foco_txt, 'foconombre': nombre.upper()}
    pars = five(comp)
    for i in range(5):
        q = pars[i] if i < len(pars) else None
        vals['p%%dn' %% (i + 1)] = short(q.label).upper() if q is not None else '-'
        vals['p%%dv' %% (i + 1)] = pct(q) if q is not None else ''
    # audio del enfocado: que parametro empuja (1-5, 0 = apagado), on/off y sensibilidad
    on = getattr(comp.par, 'Audioreact', None) if comp is not None else None
    tgt = getattr(comp.par, 'Audiotarget', None) if comp is not None else None
    mult = getattr(comp.par, 'Audiomult', None) if comp is not None else None
    vals['audio'] = str(tgt.menuIndex + 1) if on is not None and on.eval() and tgt is not None else '0'
    vals['audioon'] = ('ON' if on.eval() else 'OFF') if on is not None else '-'
    vals['audiomult'] = ('%%.1f' %% mult.eval()) if mult is not None else '-'

    sent = me.fetch('mix_sent', {}, storeDefault=True)
    if frame %% (EVERY * 12) == 0:
        sent = {}          # reenvia todo cada ~2 s: si Companion se abrio o se importo despues, se pone al dia
        fb = SCENE.op('companion_feedback')   # y la info de camaras / lugares / rotacion
        if fb is not None:
            try:
                fb.module.send_all()
            except Exception:
                pass
    for k, v in vals.items():
        if sent.get(k) != v:
            out.sendOSC('/custom-variable/mix_%%s/value' %% k, [v])
            sent[k] = v
    # visual y FX activos (los cambie el Stream Deck, el Beatstep o el mouse): enciende su boton
    activos = {'visual': vis.name[4:] if vis is not None and vis.name[4:].isdigit() else '',
               'fx': str(int(SW_FX.par.index.eval())) if SW_FX is not None else ''}
    # pagina MENU: en cada boton de pagina, lo que esta activo ahi (vacio = no hay nada activo de esa pagina)
    nm = SCENE.fetch('menu_nombres', {}, search=False, storeDefault=False) or {}
    lbl = p.menuLabels[p.menuIndex] if p is not None and p.menuLabels else ''
    fam = nm.get('fam', {}).get(lbl, 'multiview')
    activos['menu_mv'] = lbl.upper() if fam == 'multiview' else ''
    activos['menu_sc'] = lbl.upper() if fam == 'singlecam' else ''
    activos['menu_vis'] = nm.get('vis', {}).get(activos['visual'], activos['visual']).upper()
    activos['menu_fx'] = '' if activos['fx'] in ('', '0') else nm.get('fx', {}).get(activos['fx'], '').upper()
    bs = op('/project2/bs_canal')
    if bs is not None and int(bs['canal']) in (9, 10, 11):
        activos['bs_canal'] = '%%d-%%d' %% (int(bs['canal']), int(bs['pad'])) + chr(10) + ('ESCENAS' if int(bs['canal']) == 9 else 'VISUALES/FX')
    for k, v in activos.items():
        if sent.get('g_' + k) != v:
            out.sendOSC('/custom-variable/%%s/value' %% k, [v])
            sent['g_' + k] = v
    me.store('mix_sent', sent)
    return
''' % {'scene': SCENE_PATH}


def run():
    scene = op(SCENE_PATH)
    if scene is None:
        print('[error] no encuentro', SCENE_PATH)
        return
    if scene.op('companion_out') is None:
        print('[aviso] falta companion_out: corre primero setup_companion_feedback.py')
    old = scene.op('mix_feedback')
    if old is not None:
        old.destroy()
    ex = scene.create(executeDAT, 'mix_feedback')
    ex.nodeX, ex.nodeY = -1000, -1200
    ex.text = CODE
    for t in ('start', 'create', 'exit', 'framestart', 'playstatechange', 'devicechange',
              'projectpresave', 'projectpostsave'):
        if hasattr(ex.par, t):
            setattr(ex.par, t, False)
    ex.par.frameend = True
    print('[ok] pagina MIX: TD manda a Companion los 5 parametros de lo activo (layout / visual / FX)')


run()
