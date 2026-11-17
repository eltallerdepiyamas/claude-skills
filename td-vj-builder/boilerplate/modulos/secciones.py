# secciones.py — regla de legibilidad de la UI para los modulos (y cualquier pagina de parametros):
# cada pagina se parte en SECCIONES con titulo en MAYUSCULAS (Header = separador con nombre), en orden de uso:
# primero lo que se toca en show, luego ajustes, al final lecturas. Lo que no este en una seccion queda al final.
# Uso dentro de un instalar.py:
#   exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
#   secciones(comp, 'Chaser', [('Hchaser', 'CHASER', ['Chaseron', 'Chaserpatron']), ...])


def secciones(comp, pagina, lista):
    pg = next((p for p in comp.customPages if p.name == pagina), None)
    if pg is None:
        return
    orden = []
    for hn, titulo, pars in lista:
        h = getattr(comp.par, hn, None)
        if h is not None and h.page.name != pg.name:
            h.destroy()
        if not hasattr(comp.par, hn):
            pg.appendHeader(hn, label=titulo.upper())
        getattr(comp.par, hn).label = titulo.upper()
        orden += [hn] + [n for n in pars if hasattr(comp.par, n)]
    resto = [p.name for p in pg.pars if p.name not in orden]
    pg.sort(*(orden + resto))


def orden_paginas(comp, nombres):
    """Paginas en el orden dado (las que existan); las demas despues."""
    tiene = [p.name for p in comp.customPages]
    comp.sortCustomPages(*([n for n in nombres if n in tiene] + [n for n in tiene if n not in nombres]))
