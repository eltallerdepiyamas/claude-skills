# ─────────────────────────────────────────────────────────────
# limpiar_layouts_escena.py — deja escena_modular solo con los layouts de ESTE show (layout_rs_*).
#
# Haz esto SIEMPRE sobre una COPIA del rig (File → Save As con el nombre del show), nunca en el original.
#
# Qué hace:
#   - Lista los layout_* de escena_modular y separa los que se quedan (prefijo KEEP_PREFIXES) de los viejos.
#   - APPLY = False (default): solo REVISA e imprime. No cambia nada.
#   - APPLY = True: MUEVE los viejos a /project2/_respaldo/escena_modular (copia con cables + quita;
#     igual que limpiar_bases.py). No borra definitivamente: lo que haga falta se copia de vuelta.
#   - Con APPLY y REGISTRAR = True: además pone el menú Modoescena = ORDEN (los layouts nuevos) y conecta
#     cada layout a su entrada de master_switch (entrada i = opción i del menú).
#
# No toca: CAM_*, switch1, master_switch, blend_switch, parámetros, ni nada que no se llame layout_*.
#
# AVISO: cambiar el menú Modoescena cambia qué número corresponde a cada layout. Lo que esté mapeado por
# número (Stream Deck / Companion, MIDI) apuntará a otro layout hasta que lo vuelvas a mapear.
# blend_switch: aquí solo se REPORTA; sus entradas no se crean ni cambian (revísalo con fix_blend_switch.py).
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/limpiar_layouts_escena.py').read())          ← revisa
#   APPLY = True; exec(open(project.folder + '/builders/herramientas/limpiar_layouts_escena.py').read())
#   APPLY = True; REGISTRAR = True; exec(...)                                                        ← y registra menú
# (No probado en TouchDesigner.)
# ─────────────────────────────────────────────────────────────
SCENE_PATH = '/project2/base17/escena_modular'      # ajusta si tu escena_modular vive en otro lado
RESPALDO   = '/project2/_respaldo'
KEEP_PREFIXES = ('layout_rs_',)                     # los layouts de este show
ORDEN = ['layout_rs_playeras', 'layout_rs_columnas', 'layout_rs_luna',
         'layout_rs_late_show', 'layout_rs_riff', 'layout_rs_corriente']   # orden del menú Modoescena

try:
    APPLY
except NameError:
    APPLY = False
try:
    REGISTRAR
except NameError:
    REGISTRAR = False


def _kept(o):
    return o.name.startswith(KEEP_PREFIXES)


def _backup_parent():
    parent, name = RESPALDO.rsplit('/', 1)          # '/project2', '_respaldo' (create no acepta rutas)
    root = op(RESPALDO) or op(parent).create(baseCOMP, name)
    b = root.op('escena_modular')
    if b is None:
        b = root.create(baseCOMP, 'escena_modular')
    return b


def run():
    m = op(SCENE_PATH)
    if m is None:
        print('[limpiar_layouts] no existe', SCENE_PATH, '— ajusta SCENE_PATH')
        return
    layouts = [c for c in m.children if c.name.lower().startswith('layout_') and c.isCOMP]
    keep = [c for c in layouts if _kept(c)]
    old = [c for c in layouts if not _kept(c)]
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    print('se quedan (%d): %s' % (len(keep), [c.name for c in keep]))
    print('se van al respaldo (%d): %s' % (len(old), [c.name for c in old]))

    if APPLY and old:
        try:
            _backup_parent().copyOPs(old)
        except Exception as e:
            print('[WARN] no pude respaldar (%s) — NO se borró nada' % e)
            return
        for c in old:
            if c.valid:
                c.destroy()
        print('[limpiar_layouts] %d layouts movidos a %s/escena_modular' % (len(old), RESPALDO))

    if REGISTRAR and APPLY:
        names = [n for n in ORDEN if m.op(n) is not None]
        faltan = [n for n in ORDEN if m.op(n) is None]
        if faltan:
            print('[WARN] faltan por construir (corre sus setup_layout_*.py primero):', faltan)
        try:
            m.par.Modoescena.menuNames = names
            m.par.Modoescena.menuLabels = names
            print('[limpiar_layouts] menú Modoescena =', names)
        except Exception as e:
            print('[WARN] no pude poner el menú Modoescena (%s) — hazlo a mano' % e)
        sw = m.op('master_switch')
        if sw is not None:
            for i, n in enumerate(names):
                out1 = m.op(n).op('out1')
                try:
                    sw.inputConnectors[min(i, len(sw.inputConnectors) - 1)].connect(out1)
                except Exception as e:
                    print('[WARN] master_switch entrada %d ← %s: %s' % (i, n, e))
            try:
                sw.par.index.expr = "op('%s').par.Modoescena.menuIndex" % m.path
            except Exception as e:
                print('[WARN] master_switch.index:', e)
            print('[limpiar_layouts] master_switch conectado a %d layouts' % len(names))
        else:
            print('[WARN] no hay master_switch en', m.path)
        b = m.op('blend_switch')
        if b is not None:
            print('[AVISO] blend_switch NO se modificó. Revísalo con control/escena_modular/fix_blend_switch.py '
                  '(solo reconecta; si le faltan entradas hay que añadirlas a mano).')
    elif REGISTRAR:
        print('(REGISTRAR necesita APPLY = True)')

run()
APPLY = False
REGISTRAR = False
