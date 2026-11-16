# ─────────────────────────────────────────────────────────────
# setup_devices_camaras.py — selector de device por camara en una pestana dedicada.
#
# En TD 2023 el videodeviceinTOP (Windows) usa DirectShow/MediaFoundation por default y
# los menus de `device` ya listan los dispositivos disponibles del sistema. Solo exponemos
# el selector en el hub para no andar entrando a cada cam vivo.
#
# En /project2/show, pestana Dispositivos:
#   Envivo       Toggle — "En vivo" global. Al cambiar MUEVE los 6 On{N} a ese valor
#                        (visual + funcional). Los On individuales pueden luego ajustarse.
#   Por cada cam N (1..6) un bloque:
#     Sepcam{N}  Header 'Cam N'
#     On{N}      Toggle — prende esa camara (su videodeviceinTOP se activa)
#     Dev{N}     Menu   — espeja camN_vivo.par.device       (labels = nombre legible)
#     Res{N}     Menu   — espeja camN_vivo.par.signalformat (labels = '640x480 @ 30p')
#   Devestado    Str    — solo lectura: 'n/6 camaras en su capturadora' o las duplicadas
#   Fijardevices Pulse  — guarda la asignacion de AHORA como la buena
#   Refrescar    Pulse  — re-escanea + vuelve a fijar cada camara en SU capturadora
#
# FIJADO ESTABLE (_lib/camaras_devices.py): Windows reordena los video devices en cada
# arranque (tres capturadoras identicas salen como 'USB Video - 1/2/3' y ese numero
# cambia), asi que el string guardado en el .toe deja de emparejar y varias camaras caen
# en la misma capturadora — lo que ademas hace que la imagen BRINQUE, porque dos
# videodeviceinTOP sobre el mismo aparato se pelean el driver. Guardamos por camara la
# ruta fisica USB (estable por puerto) y la re-resolvemos al abrir el .toe.
#
# Un parameterexecute (devices_watch):
#   - Envivo change -> copia el valor a On1..6
#   - Dev{N} change -> camaras_devices.elegir() (intercambia si otra cam ya lo tenia)
#   - Res{N} change -> copia a cam{N}_vivo.par.signalformat
#   - Fijardevices pulse -> guarda la asignacion actual como la buena
#   - Refrescar pulse -> re-escanea + fijar()
# Un executeDAT (/project2/devices_fijos_sync) repite el fijado al abrir el proyecto.
# La activacion del device la maneja la expr de camN_vivo.par.active:
#   On{N}  OR  (FuenteN == 'vivo')
#
# Idempotente: nodos/params con tag 'tdvj_dev_cam' se reusan.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_devices_camaras.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────

TAG = 'tdvj_dev_cam'
N_CAMS = 6
SCENE_PATH = '/project2/base17/escena_modular'

scene = op(SCENE_PATH)
show = op('/project2/show')
if scene is None:
    raise SystemExit('[err] No existe %s' % SCENE_PATH)
if show is None:
    raise SystemExit('[err] No existe /project2/show')


import re
import sys
import importlib

LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import camaras_devices as cd
importlib.reload(cd)


def _nombre_legible(valor, todos=None):
    """Nombre legible del device. Si hay varias capturadoras del mismo modelo agrega el
    puerto fisico, que SI es estable entre arranques (el '- 1 / - 2 / - 3' no lo es)."""
    if not valor:
        return valor
    return cd.etiqueta(valor, todos)


_RE_SIGNAL = re.compile(r'^f?(\d+)x(\d+)([pi])?-?([\d.]+)?(?:hz)?$', re.IGNORECASE)


def _signal_legible(valor, todos=None):
    """signalformat viene como 'f640x480p-30.00hz' → '640x480 @ 30p'. Si no matchea,
    devuelve el valor tal cual."""
    if not valor:
        return valor
    m = _RE_SIGNAL.match(valor)
    if not m:
        return valor
    w, h, scan, hz = m.groups()
    s = '%sx%s' % (w, h)
    if hz:
        hz_num = float(hz)
        hz_s = ('%d' % int(hz_num)) if hz_num == int(hz_num) else ('%.2f' % hz_num)
        s += ' @ %s' % hz_s
        if scan:
            s += scan.lower()
    elif scan:
        s += ' ' + scan.lower()
    return s


# ---------- 1. pestana Dispositivos ----------
pg = next((g for g in show.customPages if g.name == 'Dispositivos'), None) or show.appendCustomPage('Dispositivos')

def _ensure(page, name, label, append, **kw):
    for p in page.pars:
        if p.name == name:
            p.label = label
            for k, v in kw.items():
                setattr(p, k, v)
            return p
    tup = append(name, label=label)
    p = tup[0] if isinstance(tup, (list, tuple)) else tup
    for k, v in kw.items():
        setattr(p, k, v)
    return p


_ensure(pg, 'Envivo', 'En vivo (prende las 6)', pg.appendToggle)
for i in range(1, N_CAMS + 1):
    _ensure(pg, 'Sepcam%d' % i, 'Cam %d' % i, pg.appendHeader)
    # 'Hay camara' OFF = esa camara no existe en este show: no se activa nunca, no entra
    # en el 'En vivo' global y no se le reserva capturadora.
    nueva = not any(p.name == 'Hay%d' % i for p in pg.pars)
    ph = _ensure(pg, 'Hay%d' % i, 'Hay camara', pg.appendToggle, default=True)
    if nueva:
        ph.val = True
    _ensure(pg, 'On%d' % i,  'En vivo',  pg.appendToggle)
    _ensure(pg, 'Dev%d' % i, 'Device',   pg.appendMenu)
    _ensure(pg, 'Res%d' % i, 'Senal',    pg.appendMenu)
    # On/Dev/Senal se ven apagados cuando no hay camara
    for nm in ('On%d' % i, 'Dev%d' % i, 'Res%d' % i):
        try:
            getattr(show.par, nm).enableExpr = "me.par.Hay%d.eval()" % i
        except Exception:
            pass
_ensure(pg, 'Seprefrescar', '—', pg.appendHeader)
_ensure(pg, 'Devestado', 'Estado', pg.appendStr, readOnly=True)
_ensure(pg, 'Fijardevices', 'Guardar esta asignacion', pg.appendPulse)
_ensure(pg, 'Aplicardevices', 'APLICAR (camaras cerradas)', pg.appendPulse)
_ensure(pg, 'Refrescar', 'Refrescar lista de devices', pg.appendPulse)

try:
    orden = ['Envivo']
    for i in range(1, N_CAMS + 1):
        orden += ['Sepcam%d' % i, 'Hay%d' % i, 'On%d' % i, 'Dev%d' % i, 'Res%d' % i]
    orden += ['Seprefrescar', 'Devestado', 'Fijardevices', 'Aplicardevices', 'Refrescar']
    pg.sort(*orden)
except Exception as e:
    print('[warn] no pude ordenar pestana Dispositivos:', e)


# ---------- 2. funcion de sync (se ejecuta ahora y al pulsar Refrescar) ----------
def _sync_menu(show_par, src_par, label_fn):
    """Copia menuNames/menuLabels del src al show_par y sincroniza valor. Si el src no
    tiene menu disponible, deja el menu vacio (sin placeholder)."""
    nombres = list(src_par.menuNames) if src_par.menuNames else []
    if not nombres:
        show_par.menuNames  = []
        show_par.menuLabels = []
        return False
    show_par.menuNames  = nombres
    show_par.menuLabels = [label_fn(n, nombres) for n in nombres]
    actual = src_par.eval()
    if actual in nombres and show_par.eval() != actual:
        show_par.val = actual
    return True


def refrescar():
    actualizados, sin_vivo = [], []
    for i in range(1, N_CAMS + 1):
        vivo = scene.op('cam%d_vivo' % i)
        sp_dev = getattr(show.par, 'Dev%d' % i, None)
        sp_res = getattr(show.par, 'Res%d' % i, None)
        if vivo is None or sp_dev is None:
            sin_vivo.append('cam%d' % i)
            continue
        # el menu Dev{N} lo arma camaras_devices._menu_hub con la CLAVE estable:
        # si aqui le metieramos el string crudo, al reenumerar Windows el valor se
        # desplaza y el parexec manda esa camara a otra capturadora.
        hay_dev = bool(vivo.par.device.menuNames)
        if sp_res is not None:
            _sync_menu(sp_res, vivo.par.signalformat, _signal_legible)
        if hay_dev:
            actualizados.append('cam%d:%s' % (i, _nombre_legible(vivo.par.device.eval())))
    print('[ok] devices refrescados:', ', '.join(actualizados) if actualizados else 'ninguno')
    if sin_vivo:
        print('     saltadas:', ', '.join(sin_vivo))


refrescar()

# ---------- 2a. fijado estable: cada camara a SU capturadora ----------
# Si nunca se ha guardado una asignacion, tomamos la de ahora como la buena.
# OJO: solo informan. Reasignar el device de una camara que esta capturando TIRA TD
# con los dongles MS2109 (paso dos veces el 2026-11-14). Para aplicar de verdad:
# pulso 'APLICAR (camaras cerradas)' en la pestana Dispositivos.
cd.sin_duplicados()
cd.fijar()


# ---------- 2b. Vivoprendido (en escena_modular) bidireccional con Envivo ----------
# Lo hacemos editable (quitamos expr) y agregamos un watch que al cambiarlo copie el
# valor a show.Envivo (que a su vez propaga a On1..6 por el devices_watch del hub).
vp = getattr(scene.par, 'Vivoprendido', None)
if vp is not None:
    try: vp.expr = ''
    except Exception: pass
    vp.mode = ParMode.CONSTANT
    # sync inicial desde el Envivo del hub (por si traía valor distinto)
    envivo_val = bool(show.par.Envivo.eval())
    if bool(vp.eval()) != envivo_val:
        vp.val = envivo_val
else:
    print('[warn] escena_modular no tiene Vivoprendido; ignorado')

# parexec en escena_modular: Vivoprendido change -> show.Envivo = Vivoprendido
vp_watch = scene.op('vivoprendido_watch')
if vp_watch is None:
    vp_watch = scene.create(parameterexecuteDAT, 'vivoprendido_watch')
    vp_watch.tags.add(TAG)
    ref = scene.op('CAM_1')
    vp_watch.nodeX = (ref.nodeX - 400) if ref is not None else -800
    vp_watch.nodeY = (ref.nodeY + 200) if ref is not None else 200
vp_watch.par.ops = scene.path
vp_watch.par.pars = 'Vivoprendido'
vp_watch.par.valuechange = True
vp_watch.par.onpulse = False
vp_watch.text = '''# Vivoprendido (escena_modular) -> show.Envivo
def onValueChange(par, prev):
    env = op('/project2/show').par.Envivo
    nuevo = bool(par.eval())
    if bool(env.eval()) != nuevo:
        env.val = nuevo  # dispara el devices_watch del hub -> sincroniza On1..6
'''


# ---------- 2d. /button.par.value0 bidireccional con show.Envivo ----------
# El boton suelto en raiz actua como atajo rapido al "En vivo".
btn = op('/button')
if btn is not None and hasattr(btn.par, 'value0'):
    # ambos lados en CONSTANT (sin expr de bind)
    btn.par.value0.mode = ParMode.CONSTANT
    try: btn.par.value0.bindExpr = ''
    except Exception: pass
    # sync inicial desde Envivo
    if bool(btn.par.value0.eval()) != bool(show.par.Envivo.eval()):
        btn.par.value0.val = bool(show.par.Envivo.eval())
    # parexec en /button
    bw = btn.op('envivo_watch') if hasattr(btn, 'op') else None
    if bw is None:
        bw = btn.create(parameterexecuteDAT, 'envivo_watch')
        bw.tags.add(TAG)
    bw.par.ops = '/button'
    bw.par.pars = 'Value0'  # el param interno se llama value0 pero el matcher usa Pascal
    # corregimos: parexec matchea por nombre exacto
    bw.par.pars = 'value0'
    bw.par.valuechange = True
    bw.par.onpulse = False
    bw.text = '''# /button.value0 -> show.Envivo
def onValueChange(par, prev):
    env = op('/project2/show').par.Envivo
    nuevo = bool(par.eval())
    if bool(env.eval()) != nuevo:
        env.val = nuevo
'''
else:
    print('[warn] /button no existe o sin par value0; skipping binding')


# ---------- 2c. expr de camN_vivo.par.active: On{N} OR (Fuente == 'vivo') ----------
for i in range(1, N_CAMS + 1):
    vivo = scene.op('cam%d_vivo' % i)
    if vivo is None:
        continue
    act = getattr(vivo.par, 'active', None)
    if act is None:
        continue
    # Hay{N} manda: si esa camara no existe en el show, su videodeviceinTOP no se
    # activa nunca (ni por On{N} ni porque la escena pida 'vivo').
    act.expr = (
        "op('/project2/show').par.Hay%d.eval() and ("
        "op('/project2/show').par.On%d.eval() "
        "or (parent().par.Fuente%d.eval() if parent().par.Fuente%d.eval() != 'global' "
        "    else parent().par.Fuente.eval()) == 'vivo')"
    ) % (i, i, i, i)


# ---------- 3. parameterexecute: show.Dev{N} -> cam{N}_vivo.par.device ----------
watch = show.op('devices_watch')
if watch is None:
    watch = show.create(parameterexecuteDAT, 'devices_watch')
    watch.tags.add(TAG)
    ref = show.op('lut_camaras_watch') or show.op('test_pantallas') or show
    watch.nodeX = (ref.nodeX + 300) if ref is not show else 0
    watch.nodeY = (ref.nodeY - 200) if ref is not show else -400
watch.par.ops = '/project2/show'
watch.par.pars = ' '.join(['Envivo']
                          + ['Hay%d' % i for i in range(1, N_CAMS + 1)]
                          + ['Dev%d' % i for i in range(1, N_CAMS + 1)]
                          + ['Res%d' % i for i in range(1, N_CAMS + 1)]
                          + ['Fijardevices', 'Aplicardevices', 'Refrescar'])
watch.par.valuechange = True
watch.par.onpulse = True
watch.text = '''# Devices camaras:
#   Envivo change -> copia a On1..6
#   DevN change  -> camaras_devices.elegir() (intercambia si otra cam ya tenia ese device)
#   ResN change  -> cam{N}_vivo.par.signalformat
#   Fijardevices pulse -> guarda la asignacion actual como la buena
#   Refrescar pulse -> vuelve a escanear, sincroniza y re-fija
SCENE = '/project2/base17/escena_modular'

def _cd():
    import sys
    lib = project.folder + '/_lib'
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import camaras_devices
    return camaras_devices

def _refrescar():
    # pasamos un dict de globals explicito para que las funciones definidas dentro del
    # script vean las variables del script (evita NameError en _ensure, refrescar, etc.)
    g = dict(globals())
    g['__name__'] = '__setup_devices_exec__'
    exec(open(project.folder + '/builders/herramientas/setup_devices_camaras.py', encoding='utf-8').read(), g)

def _copiar(par, dst_par_name):
    try: i = int(par.name[3:])
    except ValueError: return
    vivo = op(SCENE + '/cam%d_vivo' % i)
    if vivo is None: return
    dst = getattr(vivo.par, dst_par_name, None)
    if dst is None: return
    nuevo = par.eval()
    if nuevo and nuevo in (dst.menuNames or []) and dst.eval() != nuevo:
        dst.val = nuevo

def onValueChange(par, prev):
    if par.name == 'Envivo':
        nuevo = par.eval()
        show = op('/project2/show')
        for i in range(1, 7):
            p = getattr(show.par, 'On%d' % i, None)
            hay = getattr(show.par, 'Hay%d' % i, None)
            if hay is not None and not hay.eval():
                if p is not None and p.eval():
                    p.val = 0          # esa camara no existe: nunca se prende
                continue
            if p is not None and p.eval() != nuevo:
                p.val = nuevo
        # mantener Vivoprendido (escena_modular) en sync con Envivo
        vp = op(SCENE).par.Vivoprendido if op(SCENE) is not None else None
        if vp is not None and bool(vp.eval()) != bool(nuevo):
            vp.val = bool(nuevo)
        # mantener /button.value0 en sync con Envivo
        btn = op('/button')
        if btn is not None and hasattr(btn.par, 'value0'):
            if bool(btn.par.value0.eval()) != bool(nuevo):
                btn.par.value0.val = bool(nuevo)
    elif par.name.startswith('Hay'):
        try: i = int(par.name[3:])
        except ValueError: return
        show = op('/project2/show')
        p = getattr(show.par, 'On%d' % i, None)
        if not par.eval() and p is not None and p.eval():
            p.val = 0                      # se apaga al quitar la camara
        cd = _cd()
        cd.guardar_claves(verbose=False)   # libera / reserva su capturadora
        cd.fijar(verbose=False, guardar_si_vacio=False)
    elif par.name.startswith('Dev') and par.name != 'Devestado':
        try: i = int(par.name[3:])
        except ValueError: return
        nuevo = par.eval()
        if nuevo:
            # el menu guarda la CLAVE estable, no el string crudo. elegir_por_clave la
            # resuelve e intercambia si otra camara ya tenia esa capturadora: dos
            # videodeviceinTOP sobre el mismo aparato hacen que la imagen brinque.
            _cd().elegir_por_clave(i, nuevo)
    elif par.name.startswith('Res'):
        _copiar(par, 'signalformat')

def onPulse(par):
    if par.name == 'Refrescar':
        _refrescar()
    elif par.name == 'Fijardevices':
        cd = _cd()
        cd.guardar_claves()
    elif par.name == 'Aplicardevices':
        cd = _cd()
        vivas = [i for i in cd.cams()
                 if cd.cam(i) is not None and cd.cam(i).par.active.eval()]
        if vivas:
            print('[devices] OJO: camaras capturando (%s). Reasignar el device en caliente'
                  % ', '.join('cam%d' % i for i in vivas))
            print('          tira TD con los dongles MS2109. Pon sus Fuente en solido/stock')
            print('          (o Hay{N} en 0) y vuelve a pulsar APLICAR.')
        else:
            cd.sin_duplicados(aplicar=True)
            cd.fijar(aplicar=True, guardar_si_vacio=False)
'''

# ---------- 4. executeDAT: re-fijar los devices al abrir el .toe ----------
# Windows puede tardar en enumerar las capturadoras USB, asi que reintentamos.
p2 = op('/project2')
sync = p2.op('devices_fijos_sync') or p2.create(executeDAT, 'devices_fijos_sync')
sync.tags.add(TAG)
mref = p2.op('midi_devices_sync')
sync.nodeX, sync.nodeY = (mref.nodeX, mref.nodeY - 150) if mref is not None else (-1200, 250)
sync.par.start = True          # al abrir el proyecto
sync.par.devicechange = True   # al conectar/desconectar un USB
sync.par.create = False
sync.par.exit = False
sync.par.framestart = False
sync.par.frameend = False
sync.par.playstatechange = False
sync.par.projectpresave = False
sync.par.projectpostsave = False
sync.text = '''# auto-generado por builders/herramientas/setup_devices_camaras.py
# Vuelve a poner cada camara en SU capturadora al abrir el .toe.
# Windows reordena los video devices en cada arranque: el string guardado deja de
# emparejar y dos camaras acaban en el mismo aparato (imagen que brinca). Aqui
# re-resolvemos por la ruta fisica USB, que no depende del orden.
# OJO: necesita la linea de tiempo corriendo para los reintentos (delayFrames).

INTENTOS = [0, 60, 180, 600]   # cuadros: ya, 2s, 6s, 20s

def _cd():
    import sys
    lib = project.folder + '/_lib'
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import camaras_devices
    return camaras_devices

def fijar(_=None):
    try:
        cd = _cd()
        cd.sin_duplicados(verbose=False)            # solo informa
        cd.fijar(verbose=False, guardar_si_vacio=False)  # idem: no toca par.device
    except Exception as e:
        print('[devices] fallo el fijado:', e)

def _run():
    for f in INTENTOS:
        if f == 0:
            fijar()
        else:
            run('args[0]()', fijar, delayFrames=f, fromOP=me)

def onStart():
    _run()

def onDeviceChange():
    _run()

def onCreate(): return
def onExit(): return
def onFrameStart(frame): return
def onFrameEnd(frame): return
def onPlayStateChange(state): return
def onProjectPreSave(): return
def onProjectPostSave(): return
'''

print('[ok] pestana Dispositivos lista: Envivo + Cam N (On, Device, Senal) x6 + '
      'Estado / Guardar asignacion / Refrescar')
print('[ok] devices_fijos_sync instalado en /project2: re-fija las capturadoras al abrir el .toe')
