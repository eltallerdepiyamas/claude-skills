# inventario_project2.py — SOLO LEE. Lista los nodos de primer nivel de /project2 con:
# tipo, entradas, salidas, quien los referencia (expresiones / select / parametros OP) y estado
# (bypass, active, display, lock). Sirve para decidir que sobra antes de mover nada.
# Salida tambien en control/inventario_project2.json
import json, re

ROOT = op('/project2')
kids = [o for o in ROOT.children]
names = set(o.name for o in kids)

# referencias por nombre / ruta desde cualquier parametro de todo /project2 (y /project1)
refs = {o.path: set() for o in kids}
scan = list(ROOT.findChildren()) + list(op('/project1').findChildren() if op('/project1') else [])
pat_cache = {o.path: (o.path, o.name) for o in kids}
for s in scan:
    for p in s.pars():
        try:
            if p.mode == ParMode.EXPRESSION:
                txt = p.expr
            elif p.mode == ParMode.BIND:
                txt = p.bindExpr
            elif p.isOP or p.style in ('TOP', 'CHOP', 'DAT', 'COMP', 'SOP', 'MAT', 'Object', 'PanelCOMP', 'OP'):
                txt = str(p.val)
            else:
                continue
        except Exception:
            continue
        if not txt:
            continue
        for o in kids:
            if s == o or s.path.startswith(o.path + '/'):
                continue
            if o.path in txt or re.search(r"(?<![\w/])%s(?![\w])" % re.escape(o.name), txt):
                refs[o.path].add('%s.%s' % (s.path, p.name))
# texto de DATs (scripts) que nombran al nodo
dat_refs = {o.path: set() for o in kids}
for d in ROOT.findChildren(type=DAT):
    try:
        t = d.text
    except Exception:
        continue
    if not t or len(t) > 400000:
        continue
    for o in kids:
        if d == o or d.path.startswith(o.path + '/'):
            continue
        if o.path in t or re.search(r"['\"/]%s['\"/]" % re.escape(o.name), t):
            dat_refs[o.path].add(d.path)


def estado(o):
    e = []
    for n in ('bypass', 'lock', 'display', 'render', 'active', 'play', 'cooking'):
        v = getattr(o, n, None) if n in ('bypass', 'lock', 'display', 'render') else None
        if v is True:
            e.append(n)
    a = getattr(o.par, 'active', None)
    if a is not None and not a.eval():
        e.append('INACTIVO')
    if hasattr(o, 'allowCooking') and not o.allowCooking:
        e.append('NO-COOK')
    return e


out = []
for o in sorted(kids, key=lambda o: (o.nodeX, -o.nodeY)):
    ins = [i.name if i.parent() == ROOT else i.path for i in o.inputs]
    outs = sorted(set(c.owner.name if c.owner.parent() == ROOT else c.owner.path
                      for oc in o.outputConnectors for c in oc.connections))
    row = dict(name=o.name, tipo=o.OPType, x=o.nodeX, y=o.nodeY, ins=ins, outs=outs,
               refs=sorted(refs[o.path])[:6], nrefs=len(refs[o.path]),
               dats=sorted(dat_refs[o.path])[:4], ndats=len(dat_refs[o.path]),
               estado=estado(o), tags=sorted(o.tags), comment=o.comment[:60],
               hijos=len(o.children) if o.isCOMP else 0)
    out.append(row)
    flag = '' if (ins or outs or row['nrefs'] or row['ndats'] or o.isCOMP) else '  <<< SUELTO'
    print('%-26s %-20s in=%s out=%s refs=%d dats=%d %s%s' % (
        o.name, o.OPType, ins[:4], outs[:4], row['nrefs'], row['ndats'], ' '.join(row['estado']), flag))

with open(project.folder + '/control/inventario_project2.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('\n%d nodos · json en control/inventario_project2.json' % len(out))
