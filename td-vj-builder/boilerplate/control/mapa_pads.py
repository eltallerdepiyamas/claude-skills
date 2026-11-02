# =============================================================
# mapa_pads.py  —  SOLO LECTURA
# Sigue la cadena de cada pad del Beatstep en /project2:
#   table1 (nota MIDI) -> constantN -> logicN -> chopexecN -> que switch cambia
# y escribe control/mapa_pads.md
#
# Uso (Textport):
#   exec(open(project.folder + '/control/mapa_pads.py', encoding='utf-8').read())
# =============================================================

import re

ROOT_PATH = '/project2'
REPORT    = project.folder + '/control/mapa_pads.md'
ROW_RE    = re.compile(r"table1'\)\[\s*(\d+)\s*,\s*0\s*\]")
SETIDX    = re.compile(r"""op\(\s*'(\w+)'\s*\)\.par\.index\s*=\s*(\d+)""")


def run():
    root = op(ROOT_PATH)
    table = root.op('table1')
    consts = [o for o in root.children if o.OPType == 'constantCHOP']
    logics = [o for o in root.children if o.OPType == 'logicCHOP']
    execs  = [o for o in root.children if o.OPType == 'chopexecuteDAT']

    by_row = {}
    for c in consts:
        m = ROW_RE.search(c.par.const0value.expr or '')
        if m:
            by_row.setdefault(int(m.group(1)), []).append(c)

    lines = ['# Mapa de pads del Beatstep (/project2)', '',
             '| Fila table1 | Nota | Constant | Logic | Script | Accion |',
             '|---|---|---|---|---|---|']
    for r in range(table.numRows):
        note = table[r, 0].val
        if not note:
            continue
        cs = by_row.get(r, [])
        if not cs:
            lines.append('| %d | %s | **nadie la lee** | | | |' % (r, note))
            continue
        for c in cs:
            ls = [l for l in logics if c in l.inputs]
            if not ls:
                lines.append('| %d | %s | %s | **sin logic** | | |' % (r, note, c.name))
                continue
            for l in ls:
                xs = [x for x in execs if l in (x.par.chop.evalOPs() if hasattr(x.par.chop, 'evalOPs') else [x.par.chop.eval()])]
                if not xs:
                    lines.append('| %d | %s | %s | %s | **sin script** | |' % (r, note, c.name, l.name))
                for x in xs:
                    acts = ', '.join('%s=%s' % a for a in SETIDX.findall(x.text)) or '(nada)'
                    lines.append('| %d | %s | %s | %s | %s | %s |' % (r, note, c.name, l.name, x.name, acts))

    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('[ok] mapa de pads ->', REPORT)


run()
