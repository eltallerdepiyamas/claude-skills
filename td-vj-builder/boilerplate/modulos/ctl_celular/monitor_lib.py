# monitor_lib.py — ESTADO del show (para la pagina del celular) y AVISOS al celular por ntfy.
# Vive como texto en /project2/show/celular/monitor_lib; lo instala modulos/ctl_celular y lo llama monitor_exec (1 vez por s).
# Avisa solo cuando algo CAMBIA (y otra vez cuando se arregla):
#   SALIDA  la salida a Resolume deja de estar confirmada (pastilla ambar / roja) mas de 15 s
#   VIGIA   el vigia reinicio el feedback de un visual o lo salto
#   FPS     baja a menos del 60 % del cookRate mas de 10 s
#   AUDIO   no llega audio (low + mid + high en ~0) mas de Avisoaudioseg
#   ARRANQUE TD arranco (si no lo abriste tu: se cerro y alguien / algo lo reabrio)
#   RESUMEN cada Avisoresumen min un "todo bien" (0 = no)
# Los avisos van por HTTPS a ntfy.sh/<Avisostema> en un hilo aparte (no frena TD). Solo texto de estado, nada del proyecto.
# Todo queda tambien en control/avisos_log.txt.
import json, threading, time, urllib.request

S = op('/project2/show')
C = me.parent()                      # /project2/show/celular
LOG = project.folder + '/control/avisos_log.txt'
NTFY = 'https://ntfy.sh/'


def par(n, defecto=None):
    p = getattr(S.par, n, None)
    return p.eval() if p is not None else defecto


def st():
    d = C.fetch('mon', None, search=False)
    if d is None:
        d = {'t': 0.0, 'f0': absTime.frame, 't0': time.time(), 'fps': 0.0, 'cond': {}, 'resets': None,
             'saltos': None, 'avisos': [], 't_resumen': time.time(), 'audio_t': time.time()}
        C.store('mon', d)
    return d


def log(txt):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S  ') + txt + '\n')
    except Exception:
        pass


def _post(cuerpo):
    try:
        req = urllib.request.Request(NTFY, data=json.dumps(cuerpo).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=8).read()
    except Exception as e:
        log('ntfy no salio: ' + str(e)[:120])


def enviar(titulo, texto, prioridad=3, tags=None, forzar=False):
    """Guarda el aviso (lo ve la pagina del cel) y, si Avisos esta prendido, lo manda a ntfy."""
    d = st()
    d['avisos'] = ([{'t': time.strftime('%H:%M'), 'titulo': titulo, 'txt': texto, 'p': prioridad}] + d['avisos'])[:8]
    log('%s · %s' % (titulo, texto))
    tema = str(par('Avisostema', '') or '').strip()
    if not tema or not (forzar or par('Avisos', False)):
        return
    cuerpo = {'topic': tema, 'title': titulo, 'message': texto, 'priority': int(prioridad)}
    if tags:
        cuerpo['tags'] = list(tags)
    threading.Thread(target=_post, args=(cuerpo,), daemon=True).start()


def cond(nombre, malo, espera, titulo_malo, txt_malo, txt_ok, prio=4, activo=True):
    """Avisa cuando 'malo' dura mas de 'espera' s, y una vez cuando se arregla."""
    c = st()['cond'].setdefault(nombre, {'desde': None, 'avisado': False})
    ahora = time.time()
    if malo and activo:
        if c['desde'] is None:
            c['desde'] = ahora
        if not c['avisado'] and ahora - c['desde'] >= espera:
            c['avisado'] = True
            enviar(titulo_malo, txt_malo, prio, ['warning'])
        return
    if c['avisado']:
        enviar('Se arreglo: ' + nombre, txt_ok, 3, ['white_check_mark'])
    c['desde'], c['avisado'] = None, False



def _pil_fetch(clave, defecto, search=False):
    """Lo que guarda el piloto (si hay modulo auto_piloto); sin piloto, el defecto."""
    P = op('/project2/show/piloto')
    return P.fetch(clave, defecto, search=search) if P is not None else defecto

# ------------------------------------------------------------------ lecturas
def salida():
    lib = op('/project2/ui_perform/ui_lib')
    try:
        return lib.module.salida_estado() if lib is not None else ('sin UI', 1)
    except Exception as e:
        return ('error: ' + str(e)[:40], 2)


def audio():
    m = op('/project2/audio/master_audio')
    try:
        return sum(abs(float(m[c].eval())) for c in ('low', 'mid', 'high') if m[c] is not None)
    except Exception:
        return 0.0


def visual():
    try:
        pl = op('/project2/show/piloto/piloto_lib').module
        return pl.nombre_de(int(op('/project2/switch2').par.index.eval()))
    except Exception:
        return '?'


def ultima_linea_vigia():
    try:
        with open(project.folder + '/control/piloto_log.txt', 'rb') as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 4000))
            lineas = f.read().decode('utf-8', 'ignore').splitlines()
        v = [l for l in lineas if 'VIGIA' in l]
        return v[-1][21:] if v else 'el vigia actuo'
    except Exception:
        return 'el vigia actuo'


# ------------------------------------------------------------------ cada segundo
def tick():
    d = st()
    ahora = time.time()
    if ahora - d['t'] < 1.0:
        return
    dt = ahora - d['t0']
    if dt >= 2.0:
        d['fps'] = (absTime.frame - d['f0']) / dt
        d['f0'], d['t0'] = absTime.frame, ahora
    d['t'] = ahora

    txt, nivel = salida()
    cond('SALIDA', nivel >= 1, 15, 'Salida a Resolume', 'La salida no esta confirmada: ' + txt,
         'Salida otra vez bien: ' + txt, 5 if nivel == 2 else 4, par('Avisosalida', True))

    cr = float(project.cookRate)
    fps = d['fps']
    cond('FPS', fps > 0 and fps < 0.6 * cr, 10, 'FPS bajos', 'TD va a %d FPS (de %d) en %s' % (fps, cr, visual()),
         'FPS otra vez en %d' % fps, 4, par('Avisofps', True))

    a = audio()
    cond('AUDIO', a < 0.005, float(par('Avisoaudioseg', 30.0)), 'Sin audio',
         'No llega audio a los visuales hace %d s' % par('Avisoaudioseg', 30.0), 'El audio regreso', 4, par('Avisoaudio', True))

    pil = _pil_fetch('pil', {}, search=False)
    r, s = pil.get('resets', 0), pil.get('saltos', 0)
    if d['resets'] is not None and (r > d['resets'] or s > d['saltos']) and par('Avisovigia', True):
        enviar('Vigia', ultima_linea_vigia(), 4, ['eyes'])
    d['resets'], d['saltos'] = r, s

    # patron de prueba: se apaga solo despues de Patronmin minutos (por si se queda prendido)
    if par('Patronprueba', False):
        d.setdefault('patron_t', ahora)
        lim = float(par('Patronmin', 15) or 0) * 60.0
        if lim > 0 and ahora - d['patron_t'] >= lim:
            S.par.Patronprueba = False
            d.pop('patron_t', None)
            enviar('Patron apagado', 'El patron de prueba llevaba %d min: lo apague, ya sale el visual.' % (lim / 60), 4,
                   ['warning'])
    else:
        d.pop('patron_t', None)

    cada = float(par('Avisoresumen', 0) or 0) * 60.0
    if cada > 0 and ahora - d['t_resumen'] >= cada:
        d['t_resumen'] = ahora
        enviar('Todo corriendo', '%s · %d FPS · %s' % (visual(), fps, txt), 2, ['white_check_mark'])


def arranque():
    C.unstore('mon')
    st()
    enviar('TD arranco', 'TouchDesigner se abrio. Si no fuiste tu, se cerro y se reabrio: revisa la salida.', 5,
           ['rotating_light'])


def prueba():
    enviar('Prueba', 'Los avisos del show llegan a este celular.', 3, ['bell'], forzar=True)


# ------------------------------------------------------------------ para la pagina del cel
def estado():
    d = st()
    txt, nivel = salida()
    pil = _pil_fetch('pil', {}, search=False)
    vig_on = bool(par('Vigia', False))
    vig_txt = _pil_fetch('vigia_txt', '', search=False) or ''
    if not vig_on:
        vig = ('apagado', 1)
    elif pil.get('malo'):
        vig = (pil['malo'].lower() + ' · revisando', 1)
    else:
        vig = ('vigilando · %d reinicios' % pil.get('resets', 0), 0)
    cr = float(project.cookRate)
    fps = d['fps']
    a = audio()
    negro = float(par('Master', 1.0)) < 0.5
    filas = [
        {'k': 'SALIDA', 'v': txt, 'n': nivel},
        {'k': 'VIGIA', 'v': vig[0], 'n': vig[1]},
        {'k': 'FPS', 'v': '%d de %d' % (fps, cr), 'n': 0 if fps >= 0.85 * cr else (1 if fps >= 0.6 * cr else 2)},
        {'k': 'AUDIO', 'v': 'llegando' if a >= 0.005 else 'en cero', 'n': 0 if a >= 0.005 else 2},
    ]
    if negro:
        filas.insert(0, {'k': 'PANTALLA', 'v': 'BLACKOUT puesto', 'n': 2})
    if par('Patronprueba', False):
        resta = ''
        if d.get('patron_t') and float(par('Patronmin', 15) or 0) > 0:
            resta = ' · se apaga en %d min' % max(0, (float(par('Patronmin', 15)) * 60 - (time.time() - d['patron_t'])) // 60 + 1)
        filas.insert(0, {'k': 'RESOLUME', 'v': 'PATRON DE PRUEBA' + resta, 'n': 1})
    tema = str(par('Avisostema', '') or '')
    return {'filas': filas, 'avisos': d['avisos'][:5], 'avisos_on': bool(par('Avisos', False)), 'tema': tema}
