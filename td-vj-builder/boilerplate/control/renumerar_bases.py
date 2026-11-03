# =============================================================
# BOILERPLATE: MAP es el de Little Jesus (38-45 -> 25-32). Ajustar MAP antes de usar.
# renumerar_bases.py  —  FX seguidos: base38-45 -> base25-32
#   (la capa vieja base25-37 / switch5 ya se borro)
#
# 1. Revisa que base38-45 existan y que base25-32 esten libres.
# 2. Renombra base38 -> base25 ... base45 -> base32.
#    Los cables (switch23, pads) no cambian: van por cable, no por nombre.
# 3. Cambia el nombre viejo por el nuevo en expresiones, binds, parametros de texto
#    y DATs de todo el proyecto (p. ej. las del contrato: op('/project2/base45')).
# 4. Actualiza las rutas en control/fase2_backup.json.
#
# Antes de aplicar guarda todo lo que cambia en control/fase2b_backup.json.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/renumerar_bases.py', encoding='utf-8').read())
#       -> solo revisa e imprime, NO cambia nada
#   APPLY = True; exec(open(r'...\renumerar_bases.py', encoding='utf-8').read())
#       -> aplica
# =============================================================

import json, os, re

ROOT    = '/project2'
CTRL    = project.folder + '/control'
BACKUP  = os.path.join(CTRL, 'fase2b_backup.json')
CONTRATO_BACKUP = os.path.join(CTRL, 'fase2_backup.json')
SKIP    = ('local', 'sys', 'ui', 'perform')
MAP     = {38 + i: 25 + i for i in range(8)}          # 38->25 ... 45->32
NAME_RE = re.compile(r'\bbase(%s)\b' % '|'.join(str(n) for n in MAP))

try:
    APPLY
except NameError:
    APPLY = False


def _ops():
    for top in op('/').children:
        if top.name in SKIP:
            continue
        yield top
        if top.isCOMP:
            for o in top.findChildren(depth=None):
                yield o


def _sub(text):
    return NAME_RE.sub(lambda m: 'base%d' % MAP[int(m.group(1))], text)


def run():
    root = op(ROOT)
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')

    # 1. chequeo
    missing = ['base%d' % n for n in MAP if root.op('base%d' % n) is None]
    taken = ['base%d' % n for n in MAP.values() if root.op('base%d' % n) is not None]
    if missing:
        print('[!] no existen: %s' % ', '.join(missing))
    if taken:
        print('[!] ya existen (hay que borrarlos o moverlos antes): %s' % ', '.join(taken))
        print('    No se cambia nada.')
        return
    left = [n for n in ('switch5', 'null42') if root.op(n) is not None]
    if left:
        print('    (aviso: siguen en /project2: %s, de la capa vieja)' % ', '.join(left))

    print('\n--- 1. Renombrar')
    for old, new in MAP.items():
        if root.op('base%d' % old) is not None:
            print('   base%d -> base%d' % (old, new))

    # 2. referencias por nombre
    print('\n--- 2. Referencias que cambian')
    changes = []
    for o in _ops():
        for p in o.pars():
            if p.mode == ParMode.EXPRESSION:
                kind, src = 'expr', p.expr or ''
            elif p.mode == ParMode.BIND:
                kind, src = 'bind', p.bindExpr or ''
            elif p.isString:
                kind, src = 'valor', p.val or ''
            else:
                continue
            new = _sub(src)
            if new != src:
                changes.append((o, p.name, kind, src, new))
        if o.isDAT:
            try:
                src = o.text
            except Exception:
                continue
            new = _sub(src)
            if new != src:
                changes.append((o, None, 'texto', src, new))
    for o, pn, kind, src, new in changes:
        if kind == 'texto':
            print('   %s (texto DAT)' % o.path)
        elif len(changes) <= 60:
            print('   %s.%s (%s): %s  ->  %s' % (o.path, pn, kind, src[:70], new[:70]))
    if len(changes) > 60:
        print('   ... %d cambios en total (solo se listan los DATs)' % len(changes))

    if not APPLY:
        print('\n[revision] %d referencias, nada se cambio. Para aplicar: APPLY = True; exec(...)' % len(changes))
        return

    backup = {'renombres': {}, 'refs': []}
    for o, pn, kind, src, new in changes:
        backup['refs'].append({'op': o.path, 'par': pn, 'kind': kind, 'old': src})
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)

    # primero el texto (las rutas viejas siguen siendo validas mientras se edita)
    for o, pn, kind, src, new in changes:
        if kind == 'texto':
            o.text = new
            continue
        p = getattr(o.par, pn)
        if kind == 'expr':
            p.expr = new
        elif kind == 'bind':
            p.bindExpr = new
        else:
            p.val = new
    for old, new in MAP.items():
        o = root.op('base%d' % old)
        if o is not None:
            o.name = 'base%d' % new
            backup['renombres']['base%d' % old] = 'base%d' % new
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)

    # rutas del respaldo del contrato
    if os.path.exists(CONTRATO_BACKUP):
        with open(CONTRATO_BACKUP, encoding='utf-8') as f:
            cb = json.load(f)
        cb = {_sub(k): {_sub(kk): vv for kk, vv in v.items()} for k, v in cb.items()}
        with open(CONTRATO_BACKUP, 'w', encoding='utf-8') as f:
            json.dump(cb, f, ensure_ascii=False, indent=1)

    print('\n[ok] %d bases renombradas, %d referencias actualizadas. Respaldo -> %s'
          % (len(backup['renombres']), len(changes), BACKUP))
    print('     Siguiente: correr gen_companion.py (fuera de TD) e importar el .companionconfig nuevo.')


try:
    run()
finally:
    APPLY = False
