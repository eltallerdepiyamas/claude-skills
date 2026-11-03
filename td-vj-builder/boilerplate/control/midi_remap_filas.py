# =============================================================
# BOILERPLATE: ROW1/ROW3 son del MIDImix (canal 1). Mueve lo mapeado de una fila a otra.
# midi_remap_filas.py  —  mueve el glitch de la fila 1 del MIDImix a la fila 3
#   (deja libres fila 1 = visuales y fila 2 = CCTV para la fase 3)
#
# 1. Desconecta lo que habia en la fila 3 (Prism patron 1, feedback alpha,
#    ramp period, switch3 index por CC57, chroma satmin...):
#      - expresiones/binds -> se congelan en su valor actual (modo constante)
#      - nombres en Select/Rename CHOP -> se cambian a knoboffNN (no selecciona nada)
# 2. Cambia fila 1 col N -> fila 3 col N en expresiones, binds, texto y DATs.
# Los DATs con texto que lee la fila 3 solo se avisan (no se tocan).
#
# Antes de aplicar guarda todo en control/midi_remap_filas_backup.json.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/midi_remap_filas.py', encoding='utf-8').read())
#       -> solo revisa e imprime, NO cambia nada
#   APPLY = True; exec(open(r'...\midi_remap_filas.py', encoding='utf-8').read())
#       -> aplica
#   RESTORE = True; exec(open(r'...\midi_remap_filas.py', encoding='utf-8').read())
#       -> deshace con el respaldo
# =============================================================

import json, re

BACKUP  = project.folder + '/control/midi_remap_filas_backup.json'
SKIP    = ('local', 'sys', 'ui', 'perform')
MIDI_CH = 1
ROW1    = [17, 21, 25, 29, 47, 51, 55, 59]   # mismos valores que ROWS en knobs_inventario.py
ROW3    = [19, 23, 27, 31, 49, 53, 57, 61]
MOVE    = dict(zip(ROW1, ROW3))
CC_RE   = re.compile(r'ch%dctrl(\d+)(?!\d)' % MIDI_CH)

try:
    APPLY
except NameError:
    APPLY = False
try:
    RESTORE
except NameError:
    RESTORE = False


def _ops():
    for top in op('/').children:
        if top.name in SKIP:
            continue
        yield top
        if top.isCOMP:
            for o in top.findChildren(depth=None):
                yield o


def _ccs(src):
    return {int(c) for c in CC_RE.findall(src)}


def _move(src):
    return CC_RE.sub(lambda m: 'ch%dctrl%d' % (MIDI_CH, MOVE.get(int(m.group(1)), int(m.group(1)))), src)


def _off(src):
    return CC_RE.sub(lambda m: 'knoboff%s' % m.group(1) if int(m.group(1)) in ROW3 else m.group(0), src)


def plan():
    """[(op, par, kind, old, accion, new)]  accion: freeze | move"""
    out, warn = [], []
    for o in _ops():
        if o.name in ('knob_learn', 'scene_faders_lib'):
            continue
        for p in o.pars():
            if p.mode == ParMode.EXPRESSION:
                kind, src = 'expr', p.expr or ''
            elif p.mode == ParMode.BIND:
                kind, src = 'bind', p.bindExpr or ''
            elif p.isString:
                kind, src = 'valor', p.val or ''
            else:
                continue
            ccs = _ccs(src)
            if kind in ('expr', 'bind') and ccs & set(ROW3):
                out.append((o, p.name, kind, src, 'freeze', p.eval()))
            elif ccs & (set(ROW3) | set(ROW1)):
                out.append((o, p.name, kind, src, 'move', _move(_off(src))))
        if o.isDAT:
            try:
                src = o.text
            except Exception:
                continue
            ccs = _ccs(src)
            if ccs & set(ROW3):
                warn.append(o.path)
            elif ccs & set(ROW1):
                out.append((o, None, 'texto', src, 'move', _move(src)))
    return out, warn


def run():
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    changes, warn = plan()
    print('\n--- 1. Se desconecta (fila 3)')
    for o, pn, kind, src, act, new in changes:
        if act == 'freeze':
            print('   %s.%s: %s  ->  fijo en %s' % (o.path, pn, src, new))
        elif _ccs(src) & set(ROW3):
            print('   %s.%s: %s  ->  %s' % (o.path, pn, src, new))
    print('\n--- 2. Glitch fila 1 -> fila 3')
    for o, pn, kind, src, act, new in changes:
        if act == 'move' and not (_ccs(src) & set(ROW3)):
            if kind == 'texto':
                print('   %s (texto DAT)' % o.path)
            else:
                print('   %s.%s: %s  ->  %s' % (o.path, pn, src, new))
    if warn:
        print('\n[!] DATs que leen la fila 3 en su texto (revisar a mano): %s' % ', '.join(warn))

    if not APPLY:
        print('\n[revision] %d cambios, nada se aplico. Para aplicar: APPLY = True; exec(...)' % len(changes))
        return
    backup = []
    for o, pn, kind, src, act, new in changes:
        backup.append({'op': o.path, 'par': pn, 'kind': kind, 'old': src})
        if kind == 'texto':
            o.text = new
            continue
        p = getattr(o.par, pn)
        if act == 'freeze':
            p.mode = ParMode.CONSTANT
            p.val = new
        elif kind == 'expr':
            p.expr = new
        elif kind == 'bind':
            p.bindExpr = new
        else:
            p.val = new
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)
    print('\n[ok] %d cambios aplicados. Respaldo -> %s' % (len(changes), BACKUP))


def restore():
    with open(BACKUP, encoding='utf-8') as f:
        backup = json.load(f)
    for b in backup:
        o = op(b['op'])
        if o is None:
            print('   no existe', b['op'])
            continue
        if b['kind'] == 'texto':
            o.text = b['old']
            continue
        p = getattr(o.par, b['par'])
        if b['kind'] == 'expr':
            p.expr = b['old']
            p.mode = ParMode.EXPRESSION
        elif b['kind'] == 'bind':
            p.bindExpr = b['old']
            p.mode = ParMode.BIND
        else:
            p.val = b['old']
    print('[ok] restaurados %d cambios desde %s' % (len(backup), BACKUP))


if RESTORE:
    restore()
else:
    run()
APPLY = False
RESTORE = False
