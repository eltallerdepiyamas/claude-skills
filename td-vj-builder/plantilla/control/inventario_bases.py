# =============================================================
# inventario_bases.py  —  SOLO LECTURA (fase 2: contrato de 5)
# Lista, por cada base de /project2, los controles que tiene hoy:
#   - parametros custom de la base y de sus COMPs internos
#   - uniforms de sus GLSL (nombre, valor y expresion)
# para elegir los 5 sliders de cada una. Escribe control/inventario_bases.md
#
# Uso (Textport):
#   exec(open(project.folder + '/control/inventario_bases.py', encoding='utf-8').read())
# =============================================================

import re

ROOT_PATH = '/project2'
REPORT    = project.folder + '/control/inventario_bases.md'
BASES     = list(range(1, 17)) + list(range(18, 46))
SKIP_PAGES = {'About', 'Docs Helper', 'TD Update System', 'Customizations', 'OPs', 'Widget'}


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _fmt(v):
    return ('%.3g' % v) if isinstance(v, float) else str(v)


def _par_row(owner, p, rel):
    mode = _safe(lambda: p.mode)
    src = ''
    if mode == ParMode.EXPRESSION:
        src = 'expr: `%s`' % (p.expr or '')
    elif mode == ParMode.BIND:
        src = 'bind: `%s`' % (p.bindExpr or '')
    elif mode == ParMode.EXPORT:
        src = 'export'
    rng = '%s..%s' % (_fmt(_safe(lambda: p.normMin, '')), _fmt(_safe(lambda: p.normMax, ''))) if p.isNumber else ''
    return '| %s | %s | %s | %s | %s | %s | %s |' % (
        rel, p.page.name, p.name, p.label, p.style, rng, (_fmt(_safe(lambda: p.eval(), '')) + ' ' + src).replace('|', '/')[:90])


def run():
    root = op(ROOT_PATH)
    lines = ['# Inventario de controles por base', '',
             '_Para elegir los 5 sliders (intensidad, velocidad, distorsion, color, firma) de cada base._', '']
    w = lines.append
    for n in BASES:
        b = root.op('base%d' % n)
        if b is None:
            continue
        kind = 'visual' if n <= 16 else ('capa switch5' if 25 <= n <= 37 else 'efecto')
        w('## base%d — %s' % (n, kind))
        w('')
        w('| Donde | Pestana | Nombre | Etiqueta | Tipo | Rango | Valor |')
        w('|---|---|---|---|---|---|---|')
        rows = 0
        for comp in [b] + [c for c in b.findChildren(type=COMP, maxDepth=2)]:
            rel = '.' if comp is b else comp.path[len(b.path) + 1:]
            for pg in _safe(lambda: comp.customPages, []) or []:
                if pg.name in SKIP_PAGES:
                    continue
                for p in pg.pars:
                    if p.isNumber or p.isMenu or p.isToggle:
                        w(_par_row(comp, p, rel))
                        rows += 1
        # uniforms de GLSL (Vectors page)
        for g in b.findChildren(type=TOP, maxDepth=3):
            if not g.OPType.startswith('glsl'):
                continue
            rel = g.path[len(b.path) + 1:]
            for i in range(0, 64):
                name = _safe(lambda: getattr(g.par, 'vec%dname' % i).eval())
                if name is None:
                    break
                if not name:
                    continue
                vx = getattr(g.par, 'vec%dvaluex' % i)
                src = vx.expr if vx.mode == ParMode.EXPRESSION else ''
                w('| %s | uniform | %s |  | vec | | %s %s |' % (rel, name, _fmt(_safe(lambda: vx.eval(), '')),
                                                            ('expr: `%s`' % src).replace('|', '/')[:70] if src else ''))
                rows += 1
        if not rows:
            w('| — | — | sin controles | | | | |')
        w('')
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('[ok] inventario ->', REPORT)


run()
