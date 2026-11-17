# audio_tempo — detector de BPM del audio en vivo (a partir del canal kick de master_audio).
#   /project2/audio/tempo: guarda los kicks de los ultimos 12 s, vota el BPM con todos los intervalos
#   (y sus multiplos) dentro del rango Tempomin..Tempomax, y lleva una FASE de tiempos que sigue
#   corriendo aunque se vayan los kicks (breaks) y se corrige suave con cada kick (PLL).
#   Pagina Tempo de /project2/show: Tempoauto (usar el detectado) · Tempobpm (lectura) · Tempoconf (lectura)
#   · Tempomanual · Tempomin · Tempomax.
#   Para otros: op('/project2/audio/tempo/tempo_lib').module.bpm() / .fase() (en tiempos, continua).
# Modulo del boilerplate: modulos/audio_tempo. Usa el canal kick de /project2/audio/master_audio.

S = op('/project2/show')
A = op('/project2/audio')

LIB = r'''# tempo_lib — BPM y fase desde los kicks (lo escribe modulos/audio_tempo; no editar aqui)
import math
VENTANA = 12.0      # segundos de kicks que se usan para votar


def _S():
    return op('/project2/show')


def bpm():
    S = _S()
    return float(S.par.Tempobpm.eval()) if S.par.Tempoauto.eval() else float(S.par.Tempomanual.eval())


def fase():
    """Tiempos (beats) transcurridos, continuos; la parte entera sube en cada tiempo."""
    return parent().fetch('fase', 0.0, search=False)


def frame():
    u = parent()
    ahora = absTime.seconds
    t = u.fetch('t_frame', ahora, search=False)
    dt = min(max(ahora - t, 0.0), 0.25)
    u.store('t_frame', ahora)
    u.store('fase', fase() + dt * bpm() / 60.0)
    # sin kicks un rato: la confianza baja poco a poco (el tempo sigue corriendo)
    ks = u.fetch('kicks', [], search=False)
    if not ks or ahora - ks[-1] > 4.0:
        S = _S()
        S.par.Tempoconf = max(0.0, S.par.Tempoconf.eval() - dt * 0.05)


def kick(val, prev):
    if not (prev < 0.5 <= val):
        return
    u = parent()
    ahora = absTime.seconds
    ks = [t for t in u.fetch('kicks', [], search=False) if ahora - t < VENTANA]
    if ks and ahora - ks[-1] < 0.18:
        return                                   # rebote del mismo golpe
    ks.append(ahora)
    u.store('kicks', ks)
    estimar(ks)
    corregir_fase()


def estimar(ks):
    S = _S()
    lo, hi = S.par.Tempomin.eval(), S.par.Tempomax.eval()
    if len(ks) < 4:
        return
    votos, crudos = {}, []
    for i in range(len(ks)):
        for j in range(i + 1, min(len(ks), i + 9)):
            d = ks[j] - ks[i]
            for n in range(1, 9):
                b = 60.0 * n / d
                if lo <= b <= hi:
                    crudos.append(b)
                    k = round(b * 2.0) / 2.0
                    for kk, w in ((k, 1.0), (k - 0.5, 0.5), (k + 0.5, 0.5)):
                        votos[kk] = votos.get(kk, 0.0) + w
    if not votos:
        return
    mejor = max(votos, key=votos.get)
    cerca = [b for b in crudos if abs(b - mejor) <= 1.0]
    nuevo = sum(cerca) / len(cerca)
    # confianza: que tantos intervalos seguidos caen en multiplos (o medios) del periodo
    P = 60.0 / nuevo
    ok = 0
    for a, b in zip(ks, ks[1:]):
        d = b - a
        if min(abs(d / (n * P) - 1.0) for n in (0.5, 1, 1.5, 2, 3, 4)) < 0.06:     # medios tiempos cuentan
            ok += 1
    conf = ok / float(len(ks) - 1)
    u = parent()
    viejo = S.par.Tempobpm.eval()
    if conf >= 0.4:
        if abs(nuevo - viejo) < 4.0:
            S.par.Tempobpm = round(viejo + (nuevo - viejo) * 0.3, 2)
            u.store('pendiente', None)
        else:
            p = u.fetch('pendiente', None, search=False)
            if p is not None and abs(p - nuevo) < 2.0:      # dos veces seguidas: cambio de rola
                S.par.Tempobpm = round(nuevo, 2)
                u.store('pendiente', None)
            else:
                u.store('pendiente', nuevo)
    S.par.Tempoconf = round(0.7 * S.par.Tempoconf.eval() + 0.3 * conf, 3)


def corregir_fase():
    u = parent()
    f = fase()
    err = round(f) - f
    if abs(err) < 0.3:
        u.store('fase', f + err * 0.4)
        u.store('fallos', 0)
    else:
        n = u.fetch('fallos', 0, search=False) + 1
        u.store('fallos', n)
        if n >= 4:                                # 4 kicks fuera de la reja: re-engancha la fase al kick
            u.store('fase', float(round(f)))
            u.store('fallos', 0)
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


if S is None or A is None or A.op('master_audio') is None:
    print('[fallo] falta /project2/show o /project2/audio/master_audio')
else:
    pg = pagina(S, 'Tempo')
    specs = (('Toggle', 'Tempoauto', 'Usar BPM detectado', True, None),
             ('Float', 'Tempobpm', 'BPM detectado', 124.0, (85.0, 175.0)),
             ('Float', 'Tempoconf', 'Confianza', 0.0, (0.0, 1.0)),
             ('Float', 'Tempomanual', 'BPM manual', 124.0, (60.0, 200.0)),
             ('Float', 'Tempomin', 'BPM minimo', 85.0, (60.0, 140.0)),
             ('Float', 'Tempomax', 'BPM maximo', 175.0, (100.0, 220.0)))
    for kind, n, label, d, rango in specs:
        if not hasattr(S.par, n):
            getattr(pg, 'append' + kind)(n, label=label)
            getattr(S.par, n).default = d
            getattr(S.par, n).val = d
        if rango:
            getattr(S.par, n).normMin, getattr(S.par, n).normMax = rango
    S.par.Tempobpm.readOnly = True
    S.par.Tempoconf.readOnly = True
    pg.sort('Tempoauto', 'Tempobpm', 'Tempoconf', 'Tempomanual', 'Tempomin', 'Tempomax')

    T = A.op('tempo') or A.create(baseCOMP, 'tempo')
    T.comment = 'BPM y fase desde el kick de master_audio · modulos/audio_tempo'
    lib = nuevo(T, textDAT, 'tempo_lib', 0, 200)
    lib.text = LIB
    k = nuevo(T, selectCHOP, 'kick', 0, 0)
    k.par.chops = A.op('master_audio').path
    k.par.channames = 'kick'
    kx = nuevo(T, chopexecuteDAT, 'kick_exec', 200, 0)
    kx.par.chop = k.name
    for pn in ('channels', 'channel'):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = 'kick'
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False), ('whileon', False), ('whileoff', False)):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = v
    kx.text = ("def onValueChange(channel, sampleIndex, val, prev):\n"
               "    mod('tempo_lib').kick(val, prev)\n"
               "    return\n")
    fx = nuevo(T, executeDAT, 'fase_exec', 200, -150)
    fx.par.framestart = True
    fx.text = ("def onFrameStart(frame):\n"
               "    mod('tempo_lib').frame()\n"
               "    return\n")
    print('[ok] /project2/audio/tempo | BPM %.1f (conf %.2f) | auto=%s' % (
        S.par.Tempobpm.eval(), S.par.Tempoconf.eval(), S.par.Tempoauto.eval()))
