# =============================================================
# auditoria_project2.py  —  SOLO LECTURA, no cambia nada en el .toe
# Revisa /project2 y escribe un reporte en control/auditoria_project2.md:
#   A. Bases: de donde toman imagen, a donde salen, si leen otras bases
#   B. Switches: indice fuera de rango, sin salida
#   C. Pestanas custom: parametros que nadie usa (pestanas muertas)
#   D. Referencias rotas: op('...') que ya no existe (expresiones y scripts)
#   E. Scripts que ponen un switch en una entrada que no existe
#   F. Operadores con errores
#   G. Contrato de parametros de la skill td-vj-builder (5 sliders + Bypass + Audio)
#
# Uso (Textport):
#   exec(open(project.folder + '/control/auditoria_project2.py', encoding='utf-8').read())
# Puede tardar unos segundos; no lo corras en pleno show.
# =============================================================

import re
import datetime

ROOT_PATH = '/project2'
REPORT    = project.folder + '/control/auditoria_project2.md'

OPREF   = re.compile(r"""op\(\s*['"]([^'"]+)['"]\s*\)""")
PARREF  = re.compile(r'par\.(\w+)')
SETIDX  = re.compile(r"""op\(\s*['"]([^'"]+)['"]\s*\)\.par\.index\s*=\s*(\d+)""")
BASE_RE = re.compile(r'^base\d+$')
SCRIPT_TYPES = ('textDAT', 'scriptDAT')


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _resolve(owner, path):
    """Resuelve op('path') como lo haria una expresion de `owner`."""
    if '/' in path and path.startswith('/'):
        return _safe(lambda: op(path))
    base = owner.parent() if owner.parent() is not None else owner
    return _safe(lambda: base.op(path))


def _par_sources(o):
    """(par, texto) de cada parametro ligado por expresion o bind."""
    out = []
    for p in _safe(lambda: o.pars(), []):
        mode = _safe(lambda: p.mode)
        if mode == ParMode.EXPRESSION:
            out.append((p, _safe(lambda: p.expr, '') or ''))
        elif mode == ParMode.BIND:
            out.append((p, _safe(lambda: p.bindExpr, '') or ''))
    return out


def _is_script(o):
    return o.isDAT and (o.OPType.endswith('executeDAT') or o.OPType in SCRIPT_TYPES
                        or o.name.endswith('callbacks'))


def run():
    root = op(ROOT_PATH)
    if root is None:
        print('[error] no existe', ROOT_PATH)
        return

    every = [root] + list(root.findChildren())
    lines = []
    w = lines.append

    w('# Auditoria de %s' % ROOT_PATH)
    w('_%s — %d operadores revisados. Solo lectura._' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), len(every)))
    w('')

    # referencias a parametros (para detectar pestanas muertas)
    used_pars = set()
    broken = []
    for o in every:
        for p, text in _par_sources(o):
            used_pars.update(PARREF.findall(text))
            for path in OPREF.findall(text):
                if _resolve(o, path) is None:
                    broken.append((o.path, p.name, text))
        if _is_script(o):
            txt = _safe(lambda: o.text, '') or ''
            used_pars.update(PARREF.findall(txt))
            for path in set(OPREF.findall(txt)):
                if _resolve(o, path) is None:
                    broken.append((o.path, '(script)', "op('%s')" % path))

    # ---------------- A. Bases ----------------
    w('## A. Bases de %s' % ROOT_PATH)
    w('')
    w('| Base | Comentario | Entra desde | Sale hacia | Lee otras bases | Errores |')
    w('|---|---|---|---|---|---|')
    bases = sorted([c for c in root.children if c.isCOMP and BASE_RE.match(c.name)],
                   key=lambda c: int(c.name[4:]))
    for b in bases:
        ins  = ', '.join(i.name for i in _safe(lambda: b.inputs, []) if i is not None) or '—'
        outs = ', '.join(sorted({c.owner.name for oc in b.outputConnectors for c in oc.connections})) or '**nada**'
        reads = set()
        for c in b.findChildren():
            for p, text in _par_sources(c):
                reads.update(n for n in re.findall(r'base\d+', text) if n != b.name)
            for pname in ('top', 'chop', 'dat'):
                tp = getattr(c.par, pname, None)
                if tp is not None and c.OPType.startswith('select'):
                    val = str(_safe(lambda: tp.eval(), '') or '')
                    reads.update(n for n in re.findall(r'base\d+', val) if n != b.name)
        errs = (_safe(lambda: b.errors(recurse=True), '') or '').strip()
        nerr = len([l for l in errs.splitlines() if l.strip()])
        w('| %s | %s | %s | %s | %s | %s |' % (b.name, (b.comment or '').replace('|', '/'), ins, outs,
                                              ', '.join(sorted(reads)) or '—', nerr or '—'))
    w('')

    # ---------------- B. Switches ----------------
    w('## B. Switches')
    w('')
    w('| Switch | Index | Entradas | Sale hacia | Problema |')
    w('|---|---|---|---|---|')
    for s in sorted([o for o in every if o.OPType in ('switchTOP', 'switchCHOP')], key=lambda o: o.path):
        n = len(s.inputs)
        idx = _safe(lambda: int(s.par.index.eval()), 0)
        outs = ', '.join(o.name for o in s.outputs) or ''
        probs = []
        if n and idx >= n:
            probs.append('index %d fuera de rango' % idx)
        if not outs and not s.outputConnectors[0].connections:
            probs.append('sin salida')
        if n == 0:
            probs.append('sin entradas')
        w('| %s | %d | %d | %s | %s |' % (s.path, idx, n, outs or '—', ', '.join(probs) or 'ok'))
    w('')

    # ---------------- C. Pestanas custom ----------------
    w('## C. Pestanas custom con parametros que nadie usa')
    w('_Una pestana donde ningun parametro es leido por expresiones, binds o scripts probablemente es de una base que ya no existe._')
    w('')
    w('| COMP | Pestana | Parametros | Usados | Veredicto |')
    w('|---|---|---|---|---|')
    for c in [o for o in every if o.isCOMP]:
        for pg in _safe(lambda: c.customPages, []) or []:
            names = [p.name for p in pg.pars if not p.name.startswith('Escenaactiva')]
            if not names:
                continue
            used = [n for n in names if n in used_pars]
            verdict = '**muerta?**' if not used else ('parcial' if len(used) < len(names) else 'ok')
            if verdict != 'ok':
                w('| %s | %s | %d | %d | %s |' % (c.path, pg.name, len(names), len(used), verdict))
    w('')

    # ---------------- D. Referencias rotas ----------------
    w('## D. Referencias rotas (`op()` que no existe)')
    w('')
    if broken:
        w('| Operador | Parametro | Referencia |')
        w('|---|---|---|')
        for path, pname, text in broken[:200]:
            w('| %s | %s | `%s` |' % (path, pname, text.replace('|', '/')[:120]))
        if len(broken) > 200:
            w('| … | … | %d mas |' % (len(broken) - 200))
    else:
        w('Ninguna.')
    w('')

    # ---------------- E. Scripts con indices invalidos ----------------
    w('## E. Scripts que ponen un switch en una entrada que no existe')
    w('')
    rows = []
    for d in [o for o in every if _is_script(o)]:
        txt = _safe(lambda: d.text, '') or ''
        for path, idx in SETIDX.findall(txt):
            sw = _resolve(d, path)
            if sw is None:
                rows.append((d.path, path, idx, 'el switch no existe'))
            elif int(idx) >= len(sw.inputs):
                rows.append((d.path, path, idx, 'solo tiene %d entradas' % len(sw.inputs)))
    if rows:
        w('| Script | Switch | Index | Problema |')
        w('|---|---|---|---|')
        for r in rows:
            w('| %s | %s | %s | %s |' % r)
    else:
        w('Ninguno.')
    w('')

    # ---------------- F. Errores ----------------
    w('## F. Operadores con errores')
    w('')
    errs = []
    for o in every:
        e = (_safe(lambda: o.errors(recurse=False), '') or '').strip()
        if e:
            errs.append((o.path, e.splitlines()[0][:140]))
    if errs:
        w('| Operador | Error |')
        w('|---|---|')
        for path, e in errs[:150]:
            w('| %s | %s |' % (path, e.replace('|', '/')))
        if len(errs) > 150:
            w('| … | %d mas |' % (len(errs) - 150))
    else:
        w('Ninguno.')
    w('')

    # ---------------- G. Contrato td-vj-builder ----------------
    # visuales base1-16 -> pestana Visual; efectos base18-24/38-45 -> pestana Filter
    # cada uno: 5 sliders + Bypass + pestana Audio (Audioreact Low Mid High Audiotarget Audiomult)
    w('## G. Contrato de parametros (skill td-vj-builder)')
    w('')
    w('| Base | Tipo | Pestana | Sliders | Bypass | Audio | Pestanas custom |')
    w('|---|---|---|---|---|---|---|')
    audio_pars = ('Audioreact', 'Low', 'Mid', 'High', 'Audiotarget', 'Audiomult')
    for b in bases:
        num = int(b.name[4:])
        if 1 <= num <= 16:
            kind, page = 'visual', 'Visual'
        elif 18 <= num <= 24 or 38 <= num <= 45:
            kind, page = 'efecto', 'Filter'
        else:
            continue
        pages = {pg.name: pg for pg in (_safe(lambda: b.customPages, []) or [])}
        main = pages.get(page)
        sliders = len([p for p in main.pars if p.isFloat and p.name != 'Bypass']) if main else 0
        has_bypass = hasattr(b.par, 'Bypass')
        audio = pages.get('Audio')
        audio_ok = audio is not None and all(hasattr(b.par, n) for n in audio_pars)
        w('| %s | %s | %s | %s | %s | %s | %s |' % (
            b.name, kind, page if main else '**falta**', sliders if sliders == 5 else '**%d**' % sliders,
            'si' if has_bypass else '**no**', 'si' if audio_ok else '**no**', ', '.join(pages) or '—'))
    w('')

    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('[ok] auditoria lista: %d bases, %d referencias rotas, %d scripts con indice invalido, %d con errores'
          % (len(bases), len(broken), len(rows), len(errs)))
    print('     reporte ->', REPORT)


run()
