# =============================================================
# BOILERPLATE: BASE/INNER apuntan al Prism de Little Jesus. Sirve para cualquier COMP importado
#   cuyos parametros quieras ver en el COMP baseXX que lo contiene.
# exponer_parametros.py  —  los parametros de Prism se ven y se mueven desde base25
#
# Copia las pestañas de /project2/base25/prism (Custom, Patterns, Chroma) al COMP base25,
# con los mismos nombres, rangos y menus, y cada copia hace BIND al parametro de adentro:
# se mueve desde cualquiera de los dos.
# Los que el prism calcula solo (expresiones como Resx = ancho de entrada o
# Rotsinphase = tiempo) no se exponen: siguen funcionando adentro.
#
# Se puede volver a correr.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/exponer_parametros.py', encoding='utf-8').read())
#       -> solo revisa
#   APPLY = True; exec(open(r'...\exponer_parametros.py', encoding='utf-8').read())
#       -> aplica
# =============================================================

BASE  = '/project2/base25'
INNER = 'prism'

try:
    APPLY
except NameError:
    APPLY = False


def _page(comp, name):
    for pg in comp.customPages:
        if pg.name == name:
            return pg
    return comp.appendCustomPage(name)


def _clone(page, tup):
    """Crea en page el mismo parametro (tuplet) que tup: estilo, etiqueta, rangos y menu."""
    base = page.owner
    first = tup[0]
    name = first.tupletName
    old = getattr(base.par, first.name, None)
    if old is not None:
        old.destroy()
    new = getattr(page, 'append' + first.style)(name, label=first.label, size=len(tup))         if first.style in ('Float', 'Int') else getattr(page, 'append' + first.style)(name, label=first.label)
    for s, d in zip(tup, new):
        if s.isNumber:
            d.min, d.max = s.min, s.max
            d.normMin, d.normMax = s.normMin, s.normMax
            d.clampMin, d.clampMax = s.clampMin, s.clampMax
        if s.isMenu:
            # menu fijo con las opciones actuales (el original las lee de nodos internos)
            d.menuNames = list(s.menuNames)
            d.menuLabels = list(s.menuLabels)
        try:
            d.default = s.default
        except Exception:
            pass


def run():
    base = op(BASE)
    pr = base.op(INNER)
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    done, skipped = 0, []
    for src_page in pr.customPages:
        groups = []
        for p in src_page.pars:
            if p.tupletName in [g[0].tupletName for g in groups]:
                continue
            tup = list(p.tuplet)
            if any(s.mode == ParMode.EXPRESSION for s in tup):
                skipped.append('%s (%s)' % (p.tupletName, tup[0].expr))
                continue
            groups.append(tup)
        print('   pestaña %s: %s' % (src_page.name, ', '.join(g[0].tupletName for g in groups)))
        if not APPLY:
            continue
        dst_page = _page(base, src_page.name)
        for tup in groups:
            try:
                _clone(dst_page, tup)
            except Exception as e:
                print('   [!] %s no se pudo copiar: %s' % (tup[0].tupletName, e))
                continue
            # el de afuera se liga al de adentro (al reves rompe las secuencias tipo Pattern0/1)
            for s in tup:
                d = getattr(base.par, s.name)
                d.bindExpr = "op('./%s').par.%s" % (INNER, s.name)
                d.mode = ParMode.BIND
            done += 1
    if skipped:
        print('\n   se quedan adentro (los calcula el prism): %s' % ', '.join(skipped))
    if APPLY:
        print('\n[ok] %d parametros expuestos en %s' % (done, BASE))
    else:
        print('\n[revision] nada se cambio. Para aplicar: APPLY = True; exec(...)')


try:
    run()
finally:
    APPLY = False
