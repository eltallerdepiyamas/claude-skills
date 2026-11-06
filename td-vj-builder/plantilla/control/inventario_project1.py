# =============================================================
# inventario_project1.py  —  SOLO LECTURA
# Mapa de /project1 para decidir que se queda, que se mueve y que se borra:
#   - cadena de TOPs desde lo que llega de /project2 hasta las salidas
#   - cada operador de primer nivel: tipo, entradas, salidas, parametros con
#     expresion (MIDI, otros ops) y referencias a /project2
#   - PrismTop4 a detalle: pestañas, parametros y de donde lee / a donde sale
# Escribe control/inventario_project1.md
#
# Uso (Textport):
#   exec(open(project.folder + '/control/inventario_project1.py', encoding='utf-8').read())
# =============================================================

ROOT   = '/project1'
FOCUS  = 'PrismTop4'
REPORT = project.folder + '/control/inventario_project1.md'


def _up(o):
    return [cn.owner for ic in o.inputConnectors for cn in ic.connections]


def _down(o):
    return [cn.owner for oc in o.outputConnectors for cn in oc.connections]


def _refs(o):
    """Parametros con expresion/bind/ruta a otro operador."""
    out = []
    for p in o.pars():
        if p.mode == ParMode.EXPRESSION:
            out.append('%s=`%s`' % (p.name, p.expr))
        elif p.mode == ParMode.BIND:
            out.append('%s bind `%s`' % (p.name, p.bindExpr))
        elif p.style in ('TOP', 'CHOP', 'OP', 'COMP') and p.eval() is not None and p.val:
            out.append('%s→`%s`' % (p.name, p.val))
    return out


def _cell(text, n=110):
    text = text.replace('|', '\\|').replace('\n', ' ')
    return text if len(text) <= n else text[:n] + '…'


def run():
    root = op(ROOT)
    L = ['# Inventario de /project1', '']

    # 1. que entra de /project2 y que sale
    L += ['## Entradas desde /project2', '']
    for o in root.children:
        r = [x for x in _refs(o) if '/project2' in x]
        if r:
            L.append('- `%s` (%s): %s' % (o.name, o.OPType, _cell(', '.join(r), 200)))
    L += ['', '## Salidas (sin nada despues, o Window/Spout/NDI)', '']
    for o in root.children:
        if o.isTOP and not _down(o) or o.OPType in ('windowCOMP', 'spoutoutTOP', 'syphonspoutoutTOP', 'ndioutTOP'):
            L.append('- `%s` (%s) ← %s' % (o.name, o.OPType, ', '.join(u.name for u in _up(o)) or '—'))

    # 2. todos los TOPs/COMPs de primer nivel (la cadena de imagen)
    L += ['', '## Cadena de imagen (TOPs y COMPs)', '',
          '| Operador | Tipo | Entra de | Sale a | Expresiones / referencias |', '|---|---|---|---|---|']
    for o in sorted(root.children, key=lambda x: (x.nodeY, x.nodeX)):
        if not (o.isTOP or o.isCOMP):
            continue
        L.append('| `%s` | %s | %s | %s | %s |' % (
            o.name, o.OPType, ', '.join(u.name for u in _up(o)) or '—',
            ', '.join(d.name for d in _down(o)) or '—', _cell('; '.join(_refs(o)))))

    # 3. resumen de lo demas
    counts = {}
    for o in root.children:
        if not (o.isTOP or o.isCOMP):
            counts[o.OPType] = counts.get(o.OPType, 0) + 1
    L += ['', '## Otros operadores (conteo)', '']
    L += ['- %s: %d' % kv for kv in sorted(counts.items(), key=lambda kv: -kv[1])]

    # 4. PrismTop4
    pr = root.op(FOCUS)
    L += ['', '## %s' % FOCUS, '']
    if pr is None:
        L.append('no existe')
    else:
        L.append('- Tipo: %s · entra de: %s · sale a: %s' % (
            pr.OPType, ', '.join(u.path for u in _up(pr)) or '—', ', '.join(d.path for d in _down(pr)) or '—'))
        chain, o = [], pr
        for _ in range(6):
            ups = _up(o)
            if not ups:
                break
            o = ups[0]
            chain.append('%s (%s)' % (o.name, o.OPType))
        L.append('- Hacia atras: %s' % (' ← '.join(chain) or '—'))
        L += ['', '| Pestaña | Parametro | Etiqueta | Valor | Rango | Modo |', '|---|---|---|---|---|---|']
        for p in pr.customPars:
            rng = '%s..%s' % (p.normMin, p.normMax) if p.isNumber else ''
            mode = '' if p.mode == ParMode.CONSTANT else (
                'expr `%s`' % p.expr if p.mode == ParMode.EXPRESSION else 'bind `%s`' % p.bindExpr)
            L.append('| %s | %s | %s | %s | %s | %s |' % (p.page.name, p.name, p.label,
                                                          _cell(str(p.eval()), 30), rng, _cell(mode, 60)))

    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print('[ok] inventario de %s -> %s' % (ROOT, REPORT))


run()
