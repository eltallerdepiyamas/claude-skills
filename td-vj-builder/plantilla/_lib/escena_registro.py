"""
escena_registro.py — mantiene el menu Modoescena y blend_switch iguales a los layouts que existen.

Regla: opcion i del menu Modoescena  <->  entrada TOP i+1 de blend_switch (inN, N = i+1;
la entrada 0 del COMP es el indice CHOP). blend_switch.Numinputs = cantidad de escenas
(su replicator crea / quita las entradas in1..inN y las conecta a switch1 / switch2).

    registrar('layout_rs_luna')        # lo agrega al final del menu si falta y resincroniza
    sincronizar()                      # quita del menu lo que ya no existe y realinea todo
    sincronizar(orden=[...])           # pone el orden del menu (los que existan; el resto al final)
    retirar([...])                     # manda layouts al respaldo y los saca del menu

Familias: MULTIVIEW (varias camaras) y SINGLE CAM (una sola: layout_core lo marca con tdvj_fam_*).
En el menu van primero los multiview y luego los single cam.

Idempotente: correrlo de nuevo no duplica nada. La opcion activa se conserva por nombre.
Las etiquetas del menu son el nombre limpio ('layout_rs_late_show' -> 'Late Show'): el Stream Deck
manda la etiqueta, asi que reordenar no rompe los botones.
master_switch no se usa (no sale a ningun lado): no se toca.
"""
try:
    from td import *  # noqa: F401,F403
except ImportError:
    pass

import tdvj_core as core

PREFIXES = ('layout_mv_', 'layout_sc_', 'layout_rs_', 'layout_')
FAMILIAS = ('multiview', 'singlecam')      # orden en el menu: primero multiview, luego single cam


def familia(comp):
    """'multiview' o 'singlecam' (tag que pone layout_core.build_layout; sin tag = multiview)."""
    for t in comp.tags:
        if t.startswith('tdvj_fam_'):
            return t[len('tdvj_fam_'):]
    return 'multiview'


def label_for(name):
    for p in PREFIXES:
        if name.startswith(p):
            name = name[len(p):]
            break
    return name.replace('_', ' ').title()


def _scene():
    s = op(core.ESCENA)
    if s is None:
        raise ValueError('No existe %s — ajusta ESCENA en _lib/rig.py' % core.ESCENA)
    return s


def _layouts(scene):
    """Layouts de escena_modular por orden de creacion en la red (de arriba a abajo)."""
    found = [c for c in scene.children if c.isCOMP and c.name.startswith('layout_')]
    return [c.name for c in sorted(found, key=lambda c: -c.nodeY)]


def _blend_inputs(b):
    """{N: conector del COMP cuyo In TOP se llama inN}."""
    out = {}
    for ic in b.inputConnectors:
        o = ic.inOP
        if o is not None and o.name.startswith('in') and o.name[2:].isdigit():
            out[int(o.name[2:])] = ic
    return out


def _modoescena(scene):
    """El menu Escena activa (Modoescena). Si algo lo borro (p. ej. un script viejo de LJ), se vuelve a
    crear con el mismo nombre interno en la pestana Escena: OSC, Companion, faders y blend_switch lo leen."""
    p = getattr(scene.par, 'Modoescena', None)
    if p is not None:
        return p
    pg = next((g for g in scene.customPages if g.name in ('Escena', 'Escena_Master')), None) \
        or scene.appendCustomPage('Escena')
    p = pg.appendMenu('Modoescena', label='Escena activa')[0]
    try:
        scene.sortCustomPages(pg.name, *[g.name for g in scene.customPages if g.name != pg.name])
    except Exception:
        pass
    core.warn('Escena activa (Modoescena) no existia en %s: se volvio a crear' % scene.path)
    return p


def _set_menu(scene, names):
    p = _modoescena(scene)
    cur = p.eval()
    labels = [label_for(n) for n in names]
    # el Stream Deck manda la ETIQUETA: si dos se llaman igual (layout_mv_columnas / layout_sc_columnas)
    # al single cam se le agrega "1 Cam"; si aun choca, el numero de opcion
    for i, n in enumerate(names):
        if labels.count(labels[i]) > 1 and scene.op(n) is not None and familia(scene.op(n)) == 'singlecam':
            labels[i] += ' 1 Cam'
    for i in range(len(labels)):
        if labels.count(labels[i]) > 1:
            labels[i] = '%s %d' % (labels[i], i + 1)
    p.menuNames = names
    p.menuLabels = labels
    if names:
        p.val = cur if cur in names else names[0]
    return labels


def _wire_blend(scene, names):
    b = scene.op('blend_switch')
    if b is None:
        core.warn('no hay blend_switch en %s: solo se actualizo el menu' % scene.path)
        return
    n = max(len(names), 1)
    if int(b.par.Numinputs.eval()) != n:
        b.par.Numinputs = n
        rep = b.op('replicator1')
        if rep is not None:
            rep.cook(force=True)
    ins = _blend_inputs(b)
    missing = [i + 1 for i in range(len(names)) if i + 1 not in ins]
    if missing:
        core.warn('blend_switch no tiene las entradas %s (el replicator no las creo): revisa Numinputs' % missing)
    for i, name in enumerate(names):
        ic = ins.get(i + 1)
        lay = scene.op(name)
        if ic is None or lay is None:
            continue
        if not lay.outputConnectors:
            # sin out1: su builder fallo a medias. Se deja la entrada vacia (negro) y se avisa.
            core.warn('%s no tiene salida (out1): su builder fallo; corre su setup_layout_*.py y revisa el error'
                      % name)
            continue
        cur = ic.connections[0].owner if ic.connections else None
        if cur is not lay and (cur is None or cur.parent() is not lay):
            ic.connect(lay.outputConnectors[0])
    # Scene lee directo Modoescena (antes iba ligado a un "Escena activa" de una pestana vieja:
    # al quitar la pestana la liga se rompe). Cualquier otra cosa se reemplaza.
    sp = b.par.Scene
    expr = "op('%s').par.Modoescena.menuIndex" % scene.path
    mode = str(sp.mode).split('.')[-1]                   # ParMode no existe en un modulo importado
    cur = sp.expr if mode == 'EXPRESSION' else sp.bindExpr if mode == 'BIND' else ''
    if 'Modoescena' not in cur:
        sp.expr = expr
        sp.mode = type(sp.mode).EXPRESSION
        core.log('blend_switch.Scene -> %s (antes: %s)' % (expr, cur or 'fijo'))


def sincronizar(orden=None, drop_missing=True):
    scene = _scene()
    existing = _layouts(scene)
    menu = list(_modoescena(scene).menuNames)
    if orden:
        names = [n for n in orden if n in existing]
        names += [n for n in menu if n in existing and n not in names]
    else:
        names = [n for n in menu if n in existing] if drop_missing else menu
    names += [n for n in existing if n not in names]      # layouts nuevos al final
    # por familia: multiview primero, single cam despues (dentro de cada una se respeta el orden)
    fam = {n: familia(scene.op(n)) if scene.op(n) is not None else 'multiview' for n in names}
    names.sort(key=lambda n: FAMILIAS.index(fam[n]) if fam[n] in FAMILIAS else 0)
    gone = [n for n in menu if n not in names]
    labels = _set_menu(scene, names)
    _wire_blend(scene, names)
    for f in FAMILIAS:
        items = ['%d %s' % (i, l) for i, (n, l) in enumerate(zip(names, labels)) if fam[n] == f]
        if items:
            core.log('Modoescena · %-9s %s' % (f, ', '.join(items)))
    if gone:
        core.log('quitados del menu (ya no existen): %s' % ', '.join(gone))
    try:                                  # cada escena en la fila de su entrada de blend_switch
        import importlib, orden_escena
        importlib.reload(orden_escena)
        orden_escena.escenas(scene)
    except Exception as e:
        core.warn('no se pudieron acomodar las escenas: %s' % e)
    return names


def retirar(names):
    """Saca layouts del show: los copia a /project2/_respaldo/escena_modular (con cables) y los quita.
    Despues resincroniza menu y blend_switch. Para regresarlos: copiarlos de vuelta o correr su builder."""
    scene = _scene()
    found = [scene.op(n) for n in names if scene.op(n) is not None]
    if not found:
        return
    root = op(core.ROOT + '/_respaldo') or op(core.ROOT).create(baseCOMP, '_respaldo')
    dest = root.op('escena_modular') or root.create(baseCOMP, 'escena_modular')
    for c in found:
        old = dest.op(c.name)
        if old is not None:
            old.destroy()                    # respaldo anterior del mismo layout
    dest.copyOPs(found)
    for c in found:
        core.log('retirado al respaldo: %s' % c.name)
        c.destroy()


def registrar(name):
    """Asegura que el layout este en el menu (al final si es nuevo) y en su entrada de blend_switch."""
    scene = _scene()
    if scene.op(name) is None:
        core.warn('no existe %s/%s: no se registra' % (scene.path, name))
        return
    return sincronizar()
