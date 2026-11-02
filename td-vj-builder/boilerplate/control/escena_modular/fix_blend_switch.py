# =============================================================
# fix_blend_switch.py
# Alinea master_switch y blend_switch con el menu Modoescena:
# la opcion i del menu queda conectada a su layout en la entrada i.
# No borra ni recrea nada; solo reconecta lo que no coincide.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/fix_blend_switch.py').read())
#       -> solo revisa e imprime, NO cambia nada
#   APPLY = True; exec(open(project.folder + '/control/fix_blend_switch.py').read())
#       -> reconecta lo que no coincida
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'

try:
    APPLY
except NameError:
    APPLY = False


# nombres del menu cuyo operador se llama distinto
ALIASES = {'layout_fullscreen': 'layout_Fullscren'}


def _find_layout(scene, name):
    name = ALIASES.get(name, name)
    lay = scene.op(name)
    if lay is not None:
        return lay
    low = name.lower()
    for c in scene.children:
        if c.name.lower() == low:
            return c
    return None


def _owner(conn):
    return conn.connections[0].owner if conn is not None and conn.connections else None


def _report(i, name, via, cur, target):
    ok = cur is not None and target is not None and cur == target
    tag = 'ok' if ok else '<<< NO COINCIDE'
    if target is None:
        tag = '<<< NO EXISTE EL LAYOUT'
    print(f'{i:2d} | menu: {name:28s} | {via:10s} | conectado: {(cur.name if cur else "NADA"):28s} {tag}')
    return ok


def fix_master_switch(m, names):
    sw = m.op('master_switch')
    if sw is None:
        print('--- master_switch no existe, se omite')
        return
    print('\n=== master_switch')
    bad = fixed = 0
    for i, name in enumerate(names):
        target = _find_layout(m, name)
        out1 = target.op('out1') if target is not None else None
        conn = sw.inputConnectors[i] if i < len(sw.inputConnectors) else None
        cur = _owner(conn)
        cur_layout = cur.parent() if cur is not None and cur.name == 'out1' else cur
        if not _report(i, name, f'input {i}', cur_layout, target):
            bad += 1
            if APPLY and out1 is not None:
                sw.inputConnectors[i].connect(out1)
                fixed += 1
    expr = f"op('{m.path}').par.Modoescena.menuIndex"
    if APPLY and sw.par.index.expr != expr:
        sw.par.index.expr = expr
        print('    index ->', expr)
    print(f'--- master_switch: {bad} sin coincidir' + (f', {fixed} reconectados' if APPLY else ''))


def fix_blend_switch(m, names):
    b = m.op('blend_switch')
    if b is None:
        print('--- blend_switch no existe, se omite')
        return
    sw = b.op('switch2')
    s1 = b.op('switch1')
    print('\n=== blend_switch')
    print('    switch2.index:', sw.par.index.expr or sw.par.index.eval())
    if s1 is not None:
        print('    switch1 usa las mismas entradas que switch2:',
              [x.name for x in s1.inputs] == [x.name for x in sw.inputs])

    conn_by_in = {c.inOP: c for c in b.inputConnectors if c.inOP is not None}
    bad = fixed = 0
    for i, name in enumerate(names):
        target = _find_layout(m, name)
        if i >= len(sw.inputs):
            print(f'{i:2d} | menu: {name:28s} | switch2 NO tiene entrada {i}')
            bad += 1
            continue
        inop = sw.inputs[i]
        conn = conn_by_in.get(inop)
        if not _report(i, name, f'via {inop.name}', _owner(conn), target):
            bad += 1
            if APPLY and conn is not None and target is not None:
                conn.connect(target.outputConnectors[0])
                fixed += 1
    print(f'--- blend_switch: {bad} sin coincidir' + (f', {fixed} reconectados' if APPLY else ''))


def run():
    m = op(SCENE_PATH)
    names = list(m.par.Modoescena.menuNames)
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    fix_master_switch(m, names)
    fix_blend_switch(m, names)


run()
APPLY = False
