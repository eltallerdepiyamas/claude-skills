# auto_capa — ALTERNA SOLO los efectos de la segunda capa (chaser, barrido y los ledfx_* que vengan) encima del visual.
# Idempotente. Origen: Casa Bacardi x Corona Capital (2026-11-20). Apagado por default (Capaauto).
#
# Cada cuanto: cada N COMPASES con el BPM detectado (audio_tempo: el cambio cae justo en el 1 del compas) o cada N
# segundos (sin tempo, o si se elige). En segundos puede esperar al kick (maximo 1 s).
# Que pone: un efecto solo, combinaciones de dos o solo el visual; con led_slices a veces SOLO EFECTOS (sin visual) (cada opcion se prende / apaga en la pagina); nunca repite
# la anterior. Variar = cada vez que entra un efecto le cambia el patron (chaser) o la forma (barrido).
# Pagina Capa en el mismo COMP de los efectos (/project1/slices con led_slices; si no, /project1/led). Log: control/capa_log.txt
# Efectos que conoce: los TOP con tag 'ledfx' del COMP. Para uno nuevo: store('on_par', 'Xon') y opcional
# store('var_par', 'Xpatron') en su TOP (los de chaser / barrido ya vienen aqui en EFECTOS).
import json

EFECTOS = {'chaser_led': ('Chaseron', 'Chaserpatron', 'CHASER'), 'barrido_led': ('Barridoon', 'Barridoforma', 'BARRIDO'),
           'eq_led': ('Eqon', 'Eqmodo', 'EQ'), 'onda_led': ('Ondaon', 'Ondadesde', 'ONDA'),
           'cascada_led': ('Cascadaon', 'Cascadaorden', 'CASCADA'), 'giro_led': ('Giroon', 'Giromodo', 'GIRO'),
           'respira_led': ('Respiraon', 'Respiraforma', 'RESPIRA')}


def host():
    for p in ('/project1/slices', '/project1/led'):
        o = op(p)
        if o is not None and any(o.op(n) is not None for n in EFECTOS):
            return o
    return None


LIB = r'''# capa_lib — alterna los efectos de la segunda capa (lo escribe modulos/auto_capa/instalar.py; no editar aqui)
import math, random, time
H = me.parent()
EFECTOS = __EFECTOS__
LOG = project.folder + '/control/capa_log.txt'


def log(txt):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S  ') + txt + chr(10))
    except Exception:
        pass


def efectos():
    """[(nombre corto, Par on, Par variar o None)] de los ledfx que hay en este COMP."""
    out = []
    for o in sorted([o for o in H.children if o.isTOP and 'ledfx' in o.tags], key=lambda o: o.fetch('orden', 50, search=False)):
        on, var, nom = EFECTOS.get(o.name, (o.fetch('on_par', None, search=False), o.fetch('var_par', None, search=False),
                                            o.name.replace('_led', '').upper()))
        pon = getattr(H.par, on, None) if on else None
        if pon is None:
            continue
        incluir = getattr(H.par, 'Capa' + nom.lower(), None)
        if incluir is not None and not incluir.eval():
            continue
        out.append((nom, pon, getattr(H.par, var, None) if var else None))
    return out


def opciones():
    fx = efectos()
    ops = [[f] for f in fx]
    if H.par.Capaambos.eval():                    # combinaciones de dos (todos a la vez seria demasiado)
        ops += [[a, b] for k, a in enumerate(fx) for b in fx[k + 1:]]
    if H.par.Capanada.eval():
        ops.append([])
    return ops


def tempo():
    t = op('/project2/audio/tempo/tempo_lib')
    return t.module if t is not None else None


def st():
    d = H.fetch('capa', None, search=False)
    if d is None:
        d = {'actual': None, 'prox': 0.0, 'bloque': None, 'espera': 0.0}
        H.store('capa', d)
    return d


def cambiar(motivo):
    d = st()
    ops = opciones()
    if not ops:
        return
    nombres = lambda o: '+'.join(f[0] for f in o) or 'SOLO VISUAL'
    candidatos = [o for o in ops if nombres(o) != d['actual']] or ops
    elegido = random.choice(candidatos)
    prender = {f[0] for f in elegido}
    for nom, pon, pvar in efectos():
        on = nom in prender
        if on and not pon.eval() and H.par.Capavariar.eval() and pvar is not None and pvar.isMenu:
            otros = [n for n in pvar.menuNames if n != pvar.eval()]
            if otros:
                pvar.val = random.choice(otros)
        pon.val = on
    d['actual'] = nombres(elegido)
    sm = getattr(H.par, 'Salemezcla', None)          # QUE SALE de led_slices: a veces solo efectos (sobre color)
    if sm is not None and getattr(H.par, 'Capasoloefectos', None) is not None:
        solo = (H.par.Capasoloefectos.eval() and prender and not (prender & {'CASCADA', 'GIRO'})
                and random.random() < H.par.Capasoloprob.eval())
        sm.val = 'efectos' if solo else 'visual'
        if solo:
            d['actual'] += ' · SOLO EFECTOS'
    H.par.Capaestado = d['actual']
    log('%s -> %s' % (motivo, d['actual']))


def kick():
    m = op('/project2/audio/master_audio')
    try:
        return float(m['kick'].eval()) > 0.5
    except Exception:
        return False


def tick():
    d = st()
    if not H.par.Capaauto.eval():
        d['bloque'] = None
        return
    t = tempo()
    if H.par.Capamodo.eval() == 'compases' and t is not None:
        beats = 4.0 * max(1, int(H.par.Capacompases.eval()))
        b = math.floor(t.fase() / beats)
        if d['bloque'] is None:
            d['bloque'] = b
            if d['actual'] is None:
                cambiar('arranque')
        elif b < d['bloque']:
            d['bloque'] = b                  # el tempo corrigio la fase hacia atras: no es un compas nuevo
        elif b > d['bloque']:
            d['bloque'] = b
            minimo = 0.5 * beats * 60.0 / max(1.0, t.bpm())     # una correccion de fase no dispara dos cambios seguidos
            if time.time() - d.get('t_ult', 0.0) >= minimo:
                d['t_ult'] = time.time()
                cambiar('compas')
        faltan = (beats - (t.fase() % beats)) * 60.0 / max(1.0, t.bpm())
    else:
        ahora = time.time()
        if d['prox'] <= 0 or d['actual'] is None:
            d['prox'] = ahora + float(H.par.Capacada.eval())
            if d['actual'] is None:
                cambiar('arranque')
        if ahora >= d['prox']:
            if H.par.Capakick.eval() and not kick():
                d['espera'] = d['espera'] or ahora
                if ahora - d['espera'] < 1.0:
                    return
            d['espera'] = 0.0
            d['prox'] = ahora + float(H.par.Capacada.eval())
            cambiar('tiempo')
        faltan = max(0.0, d['prox'] - ahora)
    H.store('capa_faltan', faltan)


def siguiente():
    d = st()
    d['prox'] = time.time() + float(H.par.Capacada.eval())
    cambiar('boton')


def estado_txt():
    if not H.par.Capaauto.eval():
        return 'apagada'
    f = H.fetch('capa_faltan', 0.0, search=False)
    return '%s · cambia en %d:%02d' % (st()['actual'] or '-', f // 60, f % 60)
'''

H = host()
if H is None:
    print('[fallo] auto_capa: no hay efectos de segunda capa: instala antes ledfx_chaser / ledfx_barrido (en led_slices)')
else:
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    pg = next((g for g in H.customPages if g.name == 'Capa'), None) or H.appendCustomPage('Capa')

    def tog(n, label, v):
        if not hasattr(H.par, n):
            p = pg.appendToggle(n, label=label)[0]
            p.default = v
            p.val = v
        return getattr(H.par, n)

    def num(n, label, v, lo, hi):
        if not hasattr(H.par, n):
            p = pg.appendInt(n, label=label)[0]
            p.default = v
            p.val = v
        p = getattr(H.par, n)
        p.normMin, p.normMax, p.clampMin, p.min = lo, hi, True, lo
        return p

    tog('Capaauto', 'Alternar efectos solo', False)
    if not hasattr(H.par, 'Capasiguiente'):
        pg.appendPulse('Capasiguiente', label='Siguiente ya')
    if not hasattr(H.par, 'Capamodo'):
        p = pg.appendMenu('Capamodo', label='Cambia cada')[0]
        p.menuNames = ['compases', 'segundos']
        p.menuLabels = ['N compases (BPM detectado)', 'N segundos']
    num('Capacompases', 'Compases (4 tiempos)', 8, 1, 64)
    num('Capacada', 'Segundos', 30, 5, 600)
    tog('Capakick', 'En segundos: esperar el kick', True)
    NOMBRES = {'CHASER': 'Chaser', 'BARRIDO': 'Barrido', 'EQ': 'EQ de bocinas', 'ONDA': 'Onda de kick',
               'CASCADA': 'Cascada de tiempo', 'GIRO': 'Giro por bocina', 'RESPIRA': 'Respiracion'}
    hay = [v[2] for n, v in EFECTOS.items() if H.op(n) is not None]
    for nom in hay:
        tog('Capa' + nom.lower(), 'Incluir ' + NOMBRES.get(nom, nom.capitalize()), True)
    tog('Capaambos', 'Incluir combinaciones de dos', True)
    H.par.Capaambos.label = 'Incluir combinaciones de dos'
    tog('Capanada', 'Incluir solo el visual (sin efecto)', False)
    tog('Capavariar', 'Variar patron / forma al entrar', True)
    extra_que = []
    if hasattr(H.par, 'Salemezcla'):                 # led_slices con QUE SALE
        tog('Capasoloefectos', 'Incluir solo efectos (sin visual, sobre color)', True)
        if not hasattr(H.par, 'Capasoloprob'):
            p = pg.appendFloat('Capasoloprob', label='Solo efectos: que tan seguido (0-1)')[0]
            p.default, p.val = 0.3, 0.3
        H.par.Capasoloprob.normMin, H.par.Capasoloprob.normMax = 0.0, 1.0
        extra_que = ['Capasoloefectos', 'Capasoloprob']
    if not hasattr(H.par, 'Capaestado'):
        pg.appendStr('Capaestado', label='Ahora')
    H.par.Capaestado.readOnly = True
    secciones(H, 'Capa', [
        ('Hcapa', 'ALTERNAR EFECTOS (SEGUNDA CAPA)', ['Capaauto', 'Capasiguiente']),
        ('Hcaritmo', 'RITMO', ['Capamodo', 'Capacompases', 'Capacada', 'Capakick']),
        ('Hcaque', 'QUE ALTERNA', ['Capa' + n.lower() for n in hay]
                                  + ['Capaambos', 'Capanada', 'Capavariar'] + extra_que),
        ('Hcalectura', 'LECTURA', ['Capaestado']),
    ])
    orden_paginas(H, ['Salida', 'Efectos', 'Capa', 'Chaser', 'Barrido', 'EQ', 'Onda', 'Cascada', 'Giro', 'Respira', 'Slices', 'LED', 'Banner'])

    lib = H.op('capa_lib') or H.create(textDAT, 'capa_lib')
    lib.text = LIB.replace('__EFECTOS__', repr(EFECTOS))
    lib.nodeX, lib.nodeY = 1200, 350
    H.unstore('capa')
    ex = H.op('capa_exec') or H.create(executeDAT, 'capa_exec')
    ex.nodeX, ex.nodeY = 1400, 350
    ex.par.framestart = True
    ex.par.active = True
    ex.text = '\n'.join(['# alterna los efectos de la segunda capa (capa_lib)', 'def onFrameStart(frame):',
                         '    if frame % 6 == 0:', "        op('capa_lib').module.tick()", '    return', ''])
    pp = H.op('capa_pulso') or H.create(parameterexecuteDAT, 'capa_pulso')
    pp.nodeX, pp.nodeY = 1600, 350
    pp.par.op = H.path
    pp.par.pars = 'Capasiguiente'
    pp.par.onpulse = True
    pp.text = '\n'.join(['def onPulse(par):', "    op('capa_lib').module.siguiente()", '    return', ''])
    print('[ok] auto_capa en %s · efectos: %s · %s' % (H.path, [e[0] for e in lib.module.efectos()],
                                                      'PRENDIDA' if H.par.Capaauto.eval() else 'apagada (Capaauto)'))
