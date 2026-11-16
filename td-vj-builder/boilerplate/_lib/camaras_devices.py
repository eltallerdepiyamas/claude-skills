# -*- coding: utf-8 -*-
# ─────────────────────────────────────────────────────────────
# camaras_devices.py — fijado ESTABLE de la capturadora de cada camara.
#
# El problema: en Windows el string que guarda videodeviceinTOP.par.device es
#     V1|||<ruta del dispositivo>|||<indice>|||0|||<nombre>
# El <indice> y el <nombre> los pone el orden en que Windows enumero los devices al
# arrancar: tres capturadoras identicas salen como 'USB Video - 1 / - 2 / - 3' y ese
# numero CAMBIA en cada arranque o al reconectar un USB. Entonces el string guardado
# en el .toe deja de emparejar con la lista real y varias camaras caen en la misma
# capturadora (o en ninguna).
#
# La solucion: guardar por camara una CLAVE estable (la ruta fisica USB, que depende
# del puerto donde esta conectada, no del orden) y al abrir el proyecto volver a
# resolver esa clave contra la lista real de devices.
#
# Orden de emparejado (de mas a menos exacto):
#   1. misma ruta fisica  (mismo aparato en el mismo puerto)   -> exacto
#   2. mismo VID/PID libre (mismo modelo de capturadora)        -> se cambio de puerto
#   3. mismo nombre base libre                                   -> ultimo recurso
#   4. si quedo DUPLICADA con otra camara, se le da la primera capturadora fisica libre
#
# Nunca deja dos camaras en el mismo device.
#
# Uso: lo llaman builders/herramientas/setup_devices_camaras.py y el executeDAT
#      /project2/devices_fijos_sync (onStart). A mano, desde Textport:
#      import camaras_devices as cd; cd.fijar()
# ─────────────────────────────────────────────────────────────

import re

try:
    from td import *          # op(), project, etc. cuando se importa como modulo
except ImportError:
    pass

SCENE_PATH = '/project2/base17/escena_modular'
SHOW_PATH = '/project2/show'
N_CAMS = 6
STORE_KEY = 'cam_dev_claves'   # {'1': {'clave':..., 'senal':..., 'visto':...}, ...}

_RE_VIDPID = re.compile(r'(vid_[0-9a-f]{4}&pid_[0-9a-f]{4})', re.IGNORECASE)
_RE_SUFIJO = re.compile(r'\s*-\s*\d+\s*$')


# ---------------------------------------------------------------- piezas del string

def _partes(raw):
    return (raw or '').split('|||')


def ruta(raw):
    """La ruta fisica del dispositivo (segmento 1). Para devices virtuales (NVIDIA
    Broadcast, OBS Virtual Camera, NotchCam) ahi viene solo un numero: no sirve."""
    p = _partes(raw)
    return p[1] if len(p) > 2 else ''


def nombre(raw):
    p = _partes(raw)
    return p[-1] if p else (raw or '')


def nombre_base(raw):
    """'USB Video - 2' -> 'USB Video' (el numero lo pone el orden de enumeracion)."""
    return _RE_SUFIJO.sub('', nombre(raw)).strip()


def vidpid(raw):
    """'vid_534d&pid_2109' = modelo de la capturadora. '' si es virtual."""
    m = _RE_VIDPID.search(ruta(raw))
    return m.group(1).lower() if m else ''


def es_fisico(raw):
    """True si es un aparato USB real (no NVIDIA Broadcast / OBS / NotchCam)."""
    return bool(vidpid(raw))


def puerto_corto(raw):
    """Pedacito legible del instance id, para distinguir capturadoras identicas.
    '...#8&2740ad67&0&0000#...' -> '2740ad67'."""
    trozos = ruta(raw).split('#')
    if len(trozos) < 3:
        return ''
    inst = trozos[2]
    for t in inst.split('&'):
        if len(t) >= 6 and re.fullmatch(r'[0-9a-f]+', t, re.IGNORECASE):
            return t.lower()
    return inst[:10]


def clave(raw):
    """Identificador estable del device. Es lo que guardamos por camara."""
    if not raw:
        return ''
    r = ruta(raw)
    if es_fisico(raw):
        return 'ruta:' + r.strip().lower()
    return 'nombre:' + nombre_base(raw).lower()


def etiqueta(raw, todos=None):
    """Nombre legible para el menu del hub. Si hay varias capturadoras del mismo
    modelo, agrega el puerto para poder distinguirlas (y ese sufijo SI es estable)."""
    base = nombre_base(raw)
    if todos:
        iguales = [x for x in todos if nombre_base(x).lower() == base.lower()]
        if len(iguales) > 1:
            p = puerto_corto(raw)
            if p:
                return '%s · %s' % (base, p)
            return nombre(raw)
    return base or nombre(raw)


# ---------------------------------------------------------------- acceso a los nodos

def _scene():
    return op(SCENE_PATH)


def _show():
    return op(SHOW_PATH)


def cam(i):
    s = _scene()
    return s.op('cam%d_vivo' % i) if s is not None else None


def hay(i):
    """False si el toggle 'Hay camara' de esa cam esta apagado: no existe en este show,
    no se le asigna capturadora y no entra en el 'En vivo' global."""
    sh = _show()
    if sh is None:
        return True
    p = getattr(sh.par, 'Hay%d' % i, None)
    return True if p is None else bool(p.eval())


def cams():
    """Los numeros de camara que SI existen en este show."""
    return [i for i in range(1, N_CAMS + 1) if hay(i)]


def lista_devices():
    """Los devices que ve TD ahora mismo (lista de strings crudos)."""
    for i in range(1, N_CAMS + 1):
        v = cam(i)
        if v is None:
            continue
        nm = list(v.par.device.menuNames or [])
        if nm:
            return nm
    return []


# ---------------------------------------------------------------- claves guardadas

def _leer_store():
    sh = _show()
    if sh is None:
        return {}
    d = sh.fetch(STORE_KEY, {}, storeDefault=True)
    return dict(d) if isinstance(d, dict) else {}


def _escribir_store(d):
    sh = _show()
    if sh is not None:
        sh.store(STORE_KEY, d)


def guardar_claves(verbose=True):
    """Toma la asignacion que hay AHORA en cam1..6_vivo y la fija como la buena."""
    d = _leer_store()
    hechas = []
    for i in range(1, N_CAMS + 1):
        v = cam(i)
        if v is None:
            continue
        if not hay(i):
            d.pop(str(i), None)      # esa camara no existe en este show
            continue
        raw = v.par.device.eval()
        k = clave(raw)
        if not k:
            continue
        d[str(i)] = {
            'clave': k,
            'senal': v.par.signalformat.eval(),
            'visto': nombre(raw),
        }
        hechas.append('cam%d=%s' % (i, etiqueta(raw, lista_devices())))
    _escribir_store(d)
    if verbose:
        print('[devices] asignacion guardada:', ', '.join(hechas) if hechas else 'nada')
    return d


def guardar_una(i, verbose=False):
    """Fija solo la camara i con lo que tenga puesto (se llama cuando el usuario la cambia)."""
    v = cam(i)
    if v is None or not hay(i):
        return
    raw = v.par.device.eval()
    k = clave(raw)
    if not k:
        return
    d = _leer_store()
    d[str(i)] = {'clave': k, 'senal': v.par.signalformat.eval(), 'visto': nombre(raw)}
    _escribir_store(d)
    if verbose:
        print('[devices] cam%d fijada a %s' % (i, nombre(raw)))


# ---------------------------------------------------------------- resolver y aplicar

def resolver(devices=None, claves=None):
    """Devuelve {cam: raw} sin repetir device, y la lista de camaras que no se pudieron
    resolver. No toca nada: solo calcula."""
    devices = devices if devices is not None else lista_devices()
    claves = claves if claves is not None else _leer_store()
    asignado, usados, pendientes = {}, set(), []

    por_clave = {}
    for raw in devices:
        por_clave.setdefault(clave(raw), raw)

    # 1. ruta exacta (mismo aparato, mismo puerto)
    for i in cams():
        info = claves.get(str(i))
        if not info:
            pendientes.append(i)
            continue
        raw = por_clave.get(info.get('clave', ''))
        if raw is not None and raw not in usados:
            asignado[i] = raw
            usados.add(raw)
        else:
            pendientes.append(i)

    # 2. mismo modelo (VID/PID) libre — la capturadora se cambio de puerto
    todavia = []
    for i in pendientes:
        info = claves.get(str(i)) or {}
        k = info.get('clave', '')
        if not k.startswith('ruta:'):
            todavia.append(i)
            continue
        m = _RE_VIDPID.search(k)
        modelo = m.group(1).lower() if m else ''
        libre = next((r for r in devices if r not in usados and modelo and vidpid(r) == modelo), None)
        if libre is not None:
            asignado[i] = libre
            usados.add(libre)
        else:
            todavia.append(i)

    # 3. mismo nombre base libre
    pendientes, todavia = todavia, []
    for i in pendientes:
        info = claves.get(str(i)) or {}
        visto = _RE_SUFIJO.sub('', info.get('visto', '')).strip().lower()
        libre = next((r for r in devices if r not in usados and visto
                      and nombre_base(r).lower() == visto), None)
        if libre is not None:
            asignado[i] = libre
            usados.add(libre)
        else:
            todavia.append(i)

    # 4. anti-duplicado: lo que tenga puesto la camara, si esta libre; si no, la primera
    #    capturadora fisica libre (mejor eso que dos camaras en el mismo aparato)
    pendientes, sin_resolver = todavia, []
    for i in pendientes:
        v = cam(i)
        actual = v.par.device.eval() if v is not None else ''
        if actual in devices and actual not in usados:
            asignado[i] = actual
            usados.add(actual)
            continue
        libre = next((r for r in devices if r not in usados and es_fisico(r)), None)
        if libre is None:
            libre = next((r for r in devices if r not in usados), None)
        if libre is not None:
            asignado[i] = libre
            usados.add(libre)
            sin_resolver.append(i)
        else:
            sin_resolver.append(i)

    return asignado, sin_resolver


def por_clave(k, devices=None):
    """Del identificador estable al string crudo que entiende el videodeviceinTOP."""
    if not k:
        return None
    devices = devices if devices is not None else lista_devices()
    return next((r for r in devices if clave(r) == k), None)


def _menu_hub(devices):
    """Rehace el menu Dev1..6 del hub.

    OJO: los menuNames son las CLAVES, no el string crudo del device. El crudo trae el
    indice y el nombre que pone Windows al enumerar, asi que cambia entre arranques: si
    lo usabamos de menuName, al rehacer el menu el valor guardado dejaba de existir, TD
    lo pegaba al primero de la lista y el parexec movia esa camara a OTRA capturadora
    (asi cam2 acabo en GoStream el 2026-11-14). La clave no cambia."""
    sh = _show()
    if sh is None or not devices:
        return
    nombres = [clave(r) for r in devices]
    labels = [etiqueta(r, devices) for r in devices]
    for i in range(1, N_CAMS + 1):
        p = getattr(sh.par, 'Dev%d' % i, None)
        if p is None:
            continue
        if list(p.menuNames or []) == nombres:
            continue                      # sin cambios: no lo toques (evita eventos falsos)
        antes = p.eval()
        p.menuNames = nombres
        p.menuLabels = labels
        if antes in nombres and p.eval() != antes:
            p.val = antes                 # conserva la seleccion


def fijar(verbose=True, guardar_si_vacio=True, aplicar=False):
    """Revisa que cada camara este en SU capturadora.

    SEGURIDAD (2026-11-14): `aplicar=False` por default — solo CALCULA e informa en
    `show.Devestado`, no toca `par.device`. Cambiarle el device a un videodeviceinTOP
    que esta capturando TIRA TouchDesigner con los dongles MS2109 ('USB Video'): paso
    dos veces el 2026-11-14, la segunda cerro el .toe sin guardar. Reasignar solo a
    mano y con las camaras cerradas: pulso `Aplicardevices` en la pestana Dispositivos.
    """
    sh = _show()
    if sh is None or _scene() is None:
        return False

    devices = lista_devices()
    if not devices:
        if verbose:
            print('[devices] TD todavia no lista ningun video device; reintento mas tarde')
        return False

    claves = _leer_store()
    if not claves and guardar_si_vacio:
        claves = guardar_claves(verbose=verbose)

    asignado, dudosas = resolver(devices, claves)
    cambios, avisos = [], []

    for i in cams():
        v = cam(i)
        raw = asignado.get(i)
        if v is None or raw is None:
            avisos.append('cam%d sin device' % i)
            continue
        if v.par.device.eval() != raw:
            if aplicar:
                v.par.device = raw
                cambios.append('cam%d→%s' % (i, etiqueta(raw, devices)))
            else:
                avisos.append('cam%d deberia estar en %s' % (i, etiqueta(raw, devices)))
        # senal guardada, si ya aparece en la lista de esa camara
        info = claves.get(str(i)) or {}
        sen = info.get('senal')
        if (aplicar and sen and sen in (v.par.signalformat.menuNames or [])
                and v.par.signalformat.eval() != sen):
            v.par.signalformat = sen
        if i in dudosas:
            avisos.append('cam%d: no encontre la suya, le puse %s' % (i, etiqueta(raw, devices)))

    _menu_hub(devices)
    espejar_hub()

    activas = cams()
    ok = len([i for i in activas if i in asignado]) - len(dudosas)
    txt = '%d/%d camaras en su capturadora' % (ok, len(activas))
    if len(activas) < N_CAMS:
        txt += ' (apagadas: %s)' % ', '.join('cam%d' % i for i in range(1, N_CAMS + 1)
                                             if i not in activas)
    if avisos:
        txt += ' · ' + ' · '.join(avisos)
    pe = getattr(sh.par, 'Devestado', None)
    if pe is not None:
        pe.val = txt
    if verbose:
        print('[devices]', txt)
        if cambios:
            print('[devices] reacomodadas:', ', '.join(cambios))
    return not avisos


def elegir(i, raw, verbose=True):
    """Pone la camara i en el device `raw`. Si otra camara ya lo tenia, se INTERCAMBIAN
    (esa otra se queda con el que tenia la i). Nunca deja dos camaras en el mismo
    aparato: dos videodeviceinTOP sobre la misma capturadora se pelean el driver y la
    imagen brinca / pierde cuadros."""
    v = cam(i)
    if v is None or not raw:
        return
    anterior = v.par.device.eval()
    if anterior == raw:
        return
    otra = next((j for j in range(1, N_CAMS + 1)
                 if j != i and cam(j) is not None and cam(j).par.device.eval() == raw), None)
    v.par.device = raw
    guardar_una(i)
    if otra is not None:
        oj = cam(otra)
        if anterior and anterior in (oj.par.device.menuNames or []):
            oj.par.device = anterior
            guardar_una(otra)
            if verbose:
                print('[devices] cam%d ↔ cam%d intercambiadas (no pueden compartir capturadora)'
                      % (i, otra))
        else:
            if verbose:
                print('[devices] ojo: cam%d se quedo sin device propio' % otra)
    espejar_hub()
    _actualizar_estado()


def sin_duplicados(verbose=True, aplicar=False):
    """Red de seguridad: si dos camaras quedaron en el mismo device, mueve la de numero
    mas alto a una capturadora libre. Devuelve True si todo estaba bien."""
    devices = lista_devices()
    if not devices:
        return True
    usados, movidas = {}, []
    for i in cams():
        v = cam(i)
        if v is None:
            continue
        raw = v.par.device.eval()
        if raw in usados:
            libre = next((r for r in devices
                          if r not in usados and r not in
                          [cam(j).par.device.eval() for j in cams() if cam(j)]
                          and es_fisico(r)), None)
            if libre is None:
                libre = next((r for r in devices if r not in usados and es_fisico(r)), None)
            if libre is not None:
                if aplicar:
                    v.par.device = libre
                    usados[libre] = i
                movidas.append('cam%d comparte capturadora con cam%d%s'
                               % (i, usados[raw],
                                  (' → movida a %s' % etiqueta(libre, devices)) if aplicar
                                  else ' (libre: %s)' % etiqueta(libre, devices)))
                continue
            movidas.append('cam%d duplicada con cam%d y NO hay capturadora libre'
                           % (i, usados[raw]))
        else:
            usados[raw] = i
    if movidas and verbose:
        print('[devices] duplicadas:', ' · '.join(movidas))
    return not movidas


def espejar_hub():
    """El menu Dev1..6 del hub muestra lo que realmente tiene cada camara (por clave)."""
    sh = _show()
    if sh is None:
        return
    for i in cams():
        v, p = cam(i), getattr(sh.par, 'Dev%d' % i, None)
        if v is None or p is None:
            continue
        k = clave(v.par.device.eval())
        if k in (p.menuNames or []) and p.eval() != k:
            p.val = k


def elegir_por_clave(i, k, verbose=True):
    """Lo que llama el parexec cuando tocas Dev{N} en el hub: la clave a device real."""
    raw = por_clave(k)
    if raw is None:
        if verbose:
            print('[devices] cam%d: esa capturadora ya no esta conectada' % i)
        return
    elegir(i, raw, verbose=verbose)


def _actualizar_estado():
    sh = _show()
    if sh is None:
        return
    pe = getattr(sh.par, 'Devestado', None)
    if pe is None:
        return
    devices = lista_devices()
    usados = {}
    dup = []
    for i in cams():
        v = cam(i)
        if v is None:
            continue
        raw = v.par.device.eval()
        if raw in usados:
            dup.append('cam%d=cam%d' % (i, usados[raw]))
        else:
            usados[raw] = i
    pe.val = ('DUPLICADAS: ' + ', '.join(dup)) if dup else ('%d/%d camaras en su capturadora'
                                                            % (len(usados), len(cams())))


def estado():
    """Imprime que tiene cada camara y que device ve TD. Solo lectura."""
    devices = lista_devices()
    claves = _leer_store()
    print('[devices] TD ve %d:' % len(devices))
    for r in devices:
        print('   ', etiqueta(r, devices), '|', clave(r))
    for i in range(1, N_CAMS + 1):
        v = cam(i)
        if v is None:
            print('   cam%d: NO EXISTE' % i)
            continue
        if not hay(i):
            print('   cam%d: APAGADA (no hay camara en este show)' % i)
            continue
        raw = v.par.device.eval()
        k = (claves.get(str(i)) or {}).get('clave', '—')
        marca = 'ok' if clave(raw) == k else 'DISTINTA A LA FIJADA'
        print('   cam%d: %s  [%s]' % (i, etiqueta(raw, devices), marca))
