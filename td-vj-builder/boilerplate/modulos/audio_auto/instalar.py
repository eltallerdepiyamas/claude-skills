# audio_auto — cambio automatico de la fuente de audio: MICRO (en vivo) <-> CANCION (archivo).
#   Con el modulo instalado el micro (/project2/audio/audio_vivo) escucha SIEMPRE, aunque la fuente sea el archivo.
#   - Fuente = CANCION y el micro pasa de "Pasa a MICRO arriba de" durante N s  -> fuente = EN VIVO.
#   - Fuente = MICRO y el micro se queda abajo de "Regresa a CANCION abajo de" durante N s -> fuente = ARCHIVO.
#   Dos umbrales (histeresis) y dos tiempos: no brinca de un lado a otro en un hueco de la rola.
#   Nivel del micro = pico de la entrada CRUDA (antes del Gain), con caida suave; la lectura sale en el hub y en el cel
#   para calibrar los umbrales en sitio. Elegir la fuente a mano (hub, UI o cel) apaga el automatico.
#   Pagina Audio de /project2/show, seccion CAMBIO AUTOMATICO. Log: control/audio_auto_log.txt.
# Modulo del boilerplate: modulos/audio_auto. Requiere la cadena de setup_show.py (audio_vivo / audio_fuente).

S = op('/project2/show')
A = op('/project2/audio')

LIB = r'''# auto_lib — cambio automatico micro <-> cancion (lo escribe modulos/audio_auto; no editar aqui)
import math, time


def _S():
    return op('/project2/show')


def log(txt):
    try:
        with open(project.folder + '/control/audio_auto_log.txt', 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S') + '  ' + txt + '\n')
    except Exception:
        pass


def poner(fuente, motivo):
    S = _S()
    u = parent()
    u.store('yo', True)                       # el cambio lo hizo el automatico (no lo apaga)
    S.par.Audiofuente = fuente
    u.store('yo', False)
    u.store('t_cambio', absTime.seconds)
    log(('MICRO' if fuente == 'vivo' else 'CANCION') + ' · ' + motivo)
    m = op('/project2/show/celular/monitor_lib')
    try:
        if m is not None:                      # sale en AVISOS del cel (y por ntfy si Avisos esta prendido)
            m.module.enviar('Audio: ' + ('MICRO' if fuente == 'vivo' else 'CANCION'), motivo, prioridad=2)
    except Exception:
        pass


def nivel():
    v = op('/project2/audio/audio_vivo')
    if v is None or not v.numChans or not v.par.active.eval():
        return 0.0
    try:
        import numpy as np
        return float(np.abs(v.numpyArray()).max())
    except Exception:
        return 0.0


def tick():
    S = _S()
    u = parent()
    ahora = absTime.seconds
    dt = min(max(ahora - u.fetch('t', ahora, search=False), 0.0), 0.25)
    u.store('t', ahora)
    p = nivel()
    env = u.fetch('env', 0.0, search=False)
    env = p if p > env else env * math.exp(-dt / 0.35)          # sube al instante, cae suave
    u.store('env', env)
    calibrando(u, env, ahora)
    registro(u, env, ahora)
    on = S.par.Audioauto.eval()
    fuente = S.par.Audiofuente.eval()
    sube, baja = S.par.Audioautosube.eval(), S.par.Audioautobaja.eval()
    baja = min(baja, sube * 0.9)                                 # histeresis siempre
    arriba = u.fetch('arriba', 0.0, search=False)
    abajo = u.fetch('abajo', 0.0, search=False)
    arriba = arriba + dt if env > sube else 0.0
    abajo = abajo + dt if env < baja else 0.0
    u.store('arriba', arriba)
    u.store('abajo', abajo)
    cal = u.fetch('cal', None, search=False)
    if cal is not None:
        txt = 'CALIBRANDO · %.0f s' % max(0.0, CAL_SEG - (ahora - cal['t0']))
    elif not on:
        txt = 'apagado'
    elif fuente == 'archivo':
        if arriba >= S.par.Audioautosubeseg.eval():
            poner('vivo', 'micro arriba de %.3f por %.1f s' % (sube, arriba))
            u.store('arriba', 0.0)
            txt = 'MICRO · recien cambiado'
        else:
            txt = 'CANCION · ' + ('micro arriba hace %.1f s' % arriba if arriba > 0 else 'esperando micro')
    else:
        if abajo >= S.par.Audioautobajaseg.eval():
            poner('archivo', 'micro abajo de %.3f por %.0f s' % (baja, abajo))
            u.store('abajo', 0.0)
            txt = 'CANCION · recien cambiado'
        else:
            txt = 'MICRO · ' + ('micro bajo hace %.0f s' % abajo if abajo > 0 else 'micro con nivel')
    # lecturas al hub cada ~0.25 s (no cada cuadro)
    if ahora - u.fetch('t_lect', 0.0, search=False) > 0.25:
        u.store('t_lect', ahora)
        S.par.Audioautonivel = round(env, 4)
        if S.par.Audioautoestado.eval() != txt:
            S.par.Audioautoestado = txt


# ---- CALIBRAR CON EL AMBIENTE: mide CAL_SEG s lo que suena "cuando NO es el escenario" y pone los limites arriba
CAL_SEG = 10.0
CAL_BAJA = 1.15        # regresa a CANCION abajo de: un poco arriba del ambiente (p90)
CAL_SUBE = 1.6         # pasa a MICRO arriba de: bastante arriba del ambiente


def calibrar():
    u = parent()
    u.store('cal', {'t0': absTime.seconds, 'v': []})
    log('CALIBRAR · midiendo ambiente %.0f s' % CAL_SEG)


def _pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * (len(v) - 1)))] if v else 0.0


def calibrando(u, env, ahora):
    cal = u.fetch('cal', None, search=False)
    if cal is None:
        return
    cal['v'].append(env)
    if ahora - cal['t0'] < CAL_SEG:
        return
    u.unstore('cal')
    S = _S()
    amb = _pct(cal['v'], 0.9)
    baja = round(max(0.005, amb * CAL_BAJA), 3)
    sube = round(max(baja * 1.3, amb * CAL_SUBE), 3)
    for n, x in (('Audioautobaja', baja), ('Audioautosube', sube)):
        pp = getattr(S.par, n)
        if x > pp.normMax:
            pp.normMax = round(x * 1.5, 2)
        pp.val = x
    log('CALIBRADO · ambiente p90 %.3f (mediana %.3f) -> CANCION abajo de %.3f · MICRO arriba de %.3f' % (
        amb, _pct(cal['v'], 0.5), baja, sube))
    m = op('/project2/show/celular/monitor_lib')
    try:
        if m is not None:
            m.module.enviar('Audio calibrado', 'ambiente %.3f · canción < %.3f · micro > %.3f' % (amb, baja, sube), prioridad=2)
    except Exception:
        pass


def registro(u, env, ahora):
    """Cada minuto anota en el log como anduvo el micro (para afinar los limites despues del show)."""
    h = u.fetch('hist', None, search=False)
    if h is None or not isinstance(h, dict):
        h = {'t0': ahora, 'v': []}
    h['v'].append(env)
    if ahora - h['t0'] >= 60.0 and h['v']:
        S = _S()
        log('minuto · micro min %.3f mediana %.3f p90 %.3f · fuente %s · auto %s' % (
            _pct(h['v'], 0.0), _pct(h['v'], 0.5), _pct(h['v'], 0.9), S.par.Audiofuente.eval(),
            'on' if S.par.Audioauto.eval() else 'off'))
        h = {'t0': ahora, 'v': []}
    u.store('hist', h)


def fuente_cambio():
    """Alguien eligio la fuente a mano (hub, UI, cel): el automatico se apaga para no pelearle."""
    S = _S()
    u = parent()
    if u.fetch('yo', False, search=False) or not S.par.Audioauto.eval():
        return
    if absTime.seconds - u.fetch('t_cambio', -99.0, search=False) < 0.5:
        return
    S.par.Audioauto = False
    log('APAGADO · fuente elegida a mano: ' + S.par.Audiofuente.eval())
'''

EXEC = r'''# auto_exec — cada cuadro mide el micro (modulos/audio_auto)
def onFrameEnd(frame):
    try:
        op('auto_lib').module.tick()
    except Exception as e:
        debug('audio_auto', e)
    return
'''

PEXEC = r'''# auto_fuente — fuente elegida a mano = apaga el automatico; pulso Calibrar (modulos/audio_auto)
def onValueChange(par, prev):
    if par.name == 'Audiofuente':
        op('auto_lib').module.fuente_cambio()
    return


def onPulse(par):
    if par.name == 'Audioautocalibrar':
        op('auto_lib').module.calibrar()
    return
'''


def nuevo(comp, tipo, nombre, x, y):
    o = comp.op(nombre)
    if o is None:
        o = comp.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def pagina(comp, nombre):
    for p in comp.customPages:
        if p.name == nombre:
            return p
    return comp.appendCustomPage(nombre)


V = A.op('audio_vivo') if A is not None else None
if S is None or V is None or not hasattr(S.par, 'Audiofuente'):
    print('[fallo] falta /project2/show (Audiofuente) o /project2/audio/audio_vivo (setup_show.py)')
else:
    pg = pagina(S, 'Audio')
    specs = (('Toggle', 'Audioauto', 'Cambio automatico', False, None),
             ('Float', 'Audioautonivel', 'Nivel del micro (lectura)', 0.0, (0.0, 1.0)),
             ('Str', 'Audioautoestado', 'Estado (lectura)', 'apagado', None),
             ('Float', 'Audioautosube', 'Pasa a MICRO arriba de', 0.05, (0.0, 0.8)),
             ('Float', 'Audioautosubeseg', 'durante (s)', 1.5, (0.2, 10.0)),
             ('Float', 'Audioautobaja', 'Regresa a CANCION abajo de', 0.015, (0.0, 0.6)),
             ('Float', 'Audioautobajaseg', 'durante (s) ', 10.0, (1.0, 60.0)))
    for tipo, n, lab, dfl, rng in specs:
        if not hasattr(S.par, n):
            p = getattr(pg, 'append' + tipo)(n, label=lab)[0]
            p.default = dfl
            p.val = dfl
            if rng:
                p.normMin, p.normMax = rng
                p.clampMin = True
                p.min = 0.0
        getattr(S.par, n).label = lab
        if rng:
            getattr(S.par, n).normMax = max(getattr(S.par, n).normMax, rng[1])
    if not hasattr(S.par, 'Audioautocalibrar'):
        pg.appendPulse('Audioautocalibrar', label='Calibrar con el ambiente (10 s)')
    S.par.Audioautonivel.readOnly = True
    S.par.Audioautoestado.readOnly = True
    for n in ('Audioautosube', 'Audioautosubeseg', 'Audioautobaja', 'Audioautobajaseg'):
        getattr(S.par, n).enableExpr = "me.par.Audioauto"
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    # conserva las secciones que ya tiene la pagina Audio (Sep*) y agrega la nueva al final
    if not hasattr(S.par, 'Sepauto'):
        pg.appendHeader('Sepauto', label='CAMBIO AUTOMATICO MICRO / CANCION')
    S.par.Sepauto.label = 'CAMBIO AUTOMATICO MICRO / CANCION'
    nombres = [p.name for p in pg.pars]
    nuevos = ['Sepauto', 'Audioauto', 'Audioautoestado', 'Audioautonivel', 'Audioautosube', 'Audioautosubeseg',
              'Audioautobaja', 'Audioautobajaseg', 'Audioautocalibrar']
    pg.sort(*([n for n in nombres if n not in nuevos] + nuevos))

    # el micro escucha siempre con el automatico prendido
    V.par.active.expr = ''
    V.par.active.mode = ParMode.CONSTANT
    V.par.active = True                      # siempre: asi se lee el nivel para calibrar aunque el automatico este apagado
    for n in ('Audiodriver', 'Audiodevice'):
        p = getattr(S.par, n, None)
        if p is not None:
            p.enableExpr = ''
            p.enable = True

    U = A.op('audio_auto') or A.create(baseCOMP, 'audio_auto')
    U.nodeX, U.nodeY = V.nodeX, V.nodeY - 260
    U.color = (0.35, 0.55, 0.45)
    U.comment = 'audio_auto: micro <-> cancion solo (pagina Audio de show)'
    lib = nuevo(U, textDAT, 'auto_lib', 0, 0)
    lib.text = LIB
    ex = nuevo(U, executeDAT, 'auto_exec', 200, 0)
    ex.text = EXEC
    ex.par.framestart = False
    ex.par.frameend = True
    ex.par.active = True
    px = nuevo(U, parameterexecuteDAT, 'auto_fuente', 200, -150)
    px.text = PEXEC
    px.par.op = S.path
    px.par.pars = 'Audiofuente Audioautocalibrar'
    px.par.valuechange = True
    px.par.onpulse = True
    px.par.active = True
    U.store('t', absTime.seconds)
    print('[ok] audio_auto en %s · %s · micro siempre escuchando con Audioauto (ahora %s)' % (
        U.path, 'pagina Audio de show', 'PRENDIDO' if S.par.Audioauto.eval() else 'apagado'))
