# piloto_lib.py — PILOTO AUTOMATICO + VIGIA DE VIDEO (+ registro de resistencia). Vive como texto en
# /project2/show/piloto/piloto_lib; lo llama piloto_exec cada cuadro (tick). Lo instala setup_piloto.py.
#
# PILOTO: rota los pads de BANCOS (CH9/CH10/CH11) con fundido real entre dos visuales vivos
#   (switch2 = lo que esta al aire, piloto_b = lo que entra, piloto_cross los mezcla antes de level1).
#   Ritmo: Duracion ± Variacion; adelanta en un DROP; espera el KICK para cambiar. Logo cada N cambios.
#   Si alguien toca un pad, se pausa "Retomar" segundos y sigue solo. Deriva: mueve lento los sliders del visual.
# VIGIA: mide la salida (64x36) cada ~0.25 s. Negro o saturado mas de "Tolerancia" s -> reinicia el feedback de esa
#   base; si sigue mal y el piloto esta prendido, la salta. Todo queda en control/piloto_log.txt.
# REGISTRO: cada "Registro (min)" anota FPS, memoria, visual y avisos en control/soak_log.csv.
import ast, json, math, os, random, re, time

R = op('/project2')
S = op('/project2/show')
P = me.parent()                     # /project2/show/piloto
LOG = project.folder + '/control/piloto_log.txt'
SOAK = project.folder + '/control/soak_log.csv'
NO_DERIVA = ('Tono', 'Tamano', 'Disuelve')


def st():
    d = P.fetch('pil', None, search=False)
    if d is None:
        d = {'bolsa': [], 'sig': None, 'prox': 0.0, 'ultimo': 0.0, 'pausa': 0.0, 'esperado': None,
             'trans': None, 'cambios': 0, 'desde_logo': 0, 'fast': 0.0, 'slow': 0.0, 'kick_prev': 0.0,
             'malo': None, 'malo_t': 0.0, 'resets': 0, 'deriva': None, 'vigia_n': 0, 'soak_t': 0.0,
             'saltos': 0, 'f0': absTime.frame, 't0': time.time(), 'espera_kick': 0.0}
        P.store('pil', d)
    return d


def par(n, defecto=None):
    p = getattr(S.par, n, None)
    return p.eval() if p is not None else defecto


def log(txt):
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S  ') + txt + '\n')
    except Exception:
        pass


def bancos():
    c = P.fetch('bancos_cache', None, search=False)
    if c is None:
        src = open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read()
        B = next(ast.literal_eval(n.value) for n in ast.parse(src).body
                 if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'BANCOS')
        G = next(ast.literal_eval(n.value) for n in ast.parse(src).body
                 if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'GRUPOS')
        c = [(canal, i + 1, p[0], p[1]) for canal, pads in sorted(B.items()) for i, p in enumerate(pads) if p]
        P.store('bancos_cache', c)
        P.store('logos_cache', [k for k, g in G.items() if 'LOGO' in g])
    return c


def nombre_de(entrada):
    return next((n for c, i, n, e in bancos() if e == entrada), '?')


def base_de(k):
    sw = R.op('switch2')
    o = sw.inputs[k] if 0 <= k < len(sw.inputs) else None
    for _ in range(4):
        if o is None:
            return None
        if o.parent() != R:
            return o.parent()
        if re.match(r'base\d+$', o.name):
            return o
        nul = next((i for i in o.inputs if i.OPType == 'nullTOP'), None) if o.OPType == 'switchTOP' else None
        o = nul if nul is not None else (o.inputs[0] if o.inputs else None)
    return None


# ------------------------------------------------------------------ eleccion
def candidatos(logo):
    excl = set(str(par('Pilotoexcluir', '')).replace(',', ' ').split())
    logos = P.fetch('logos_cache', [11], search=False)
    out = []
    for canal, pad, nombre, e in bancos():
        if not par('Pilotoch%d' % canal, True) or '%d-%d' % (canal, pad) in excl:
            continue
        if logo is not None and (canal in logos) != logo:
            continue
        out.append((canal, pad, nombre, e))
    return out


def elegir_siguiente():
    d = st()
    actual = int(R.op('switch2').par.index.eval())
    cada = int(par('Pilotologo', 4) or 0)
    bancos()
    logos = P.fetch('logos_cache', [11], search=False)
    quiere_logo = cada > 0 and any(par('Pilotoch%d' % k, True) for k in logos) and d['desde_logo'] >= cada - 1
    lista = candidatos(True if quiere_logo else (False if cada > 0 else None)) or candidatos(None)
    if not lista:
        return None
    if par('Pilotoorden', 'aleatorio') == 'secuencia':
        es = [x[3] for x in lista]
        pos = [i for i, x in enumerate(lista) if x[3] == actual]
        return lista[(pos[0] + 1) % len(lista)] if pos else lista[0]
    # aleatorio sin repetir: bolsa por grupo (logo / no logo), con peso por canal
    clave = 'L' if quiere_logo else 'V'
    bolsa = [x for x in d['bolsa'] if x[0] == clave and any(c[3] == x[1] for c in lista)]
    if not bolsa:
        bolsa = []
        for c in lista:
            peso = float(par('Pilotopeso%d' % c[0], 1.0) or 0)
            bolsa += [(clave, c[3])] * max(0, int(round(peso * 2)))
        random.shuffle(bolsa)
    d['bolsa'] = [x for x in d['bolsa'] if x[0] != clave] + bolsa
    while bolsa:
        x = bolsa.pop(0)
        d['bolsa'].remove(x)
        if x[1] != actual:
            return next(c for c in lista if c[3] == x[1])
    return next((c for c in lista if c[3] != actual), lista[0])


def programar(d, ahora):
    dur = max(3.0, float(par('Pilotoduracion', 30.0)))
    var = float(par('Pilotovariacion', 0.25))
    d['prox'] = ahora + dur * (1.0 + random.uniform(-var, var))


# ------------------------------------------------------------------ deriva de sliders
def deriva_empezar(entrada):
    d = st()
    deriva_parar()
    b = base_de(entrada)
    if b is None or not par('Pilotoderiva', False):
        return
    pg = next((g for g in b.customPages if g.name in ('Visual', 'Layout')), None)
    if pg is None:
        return
    ps = [p for p in pg.pars if p.isFloat and p.mode == ParMode.CONSTANT and p.style not in ('RGB', 'RGBA')
          and p.name not in NO_DERIVA][:5]
    d['deriva'] = {'base': b.path, 'orig': {p.name: p.eval() for p in ps},
                   'fase': {p.name: random.uniform(0, 100) for p in ps}}


def deriva_parar():
    d = st()
    dv = d.get('deriva')
    d['deriva'] = None
    if not dv:
        return
    b = op(dv['base'])
    if b is None:
        return
    for n, v in dv['orig'].items():
        p = getattr(b.par, n, None)
        if p is not None:
            p.val = v


def deriva_tick(ahora):
    dv = st().get('deriva')
    if not dv:
        return
    b = op(dv['base'])
    rango = float(par('Pilotoderivarango', 0.15))
    for n, v0 in dv['orig'].items():
        p = getattr(b.par, n, None) if b else None
        if p is None:
            continue
        lo, hi = (p.normMin, p.normMax) if p.normMax > p.normMin else (p.min, p.max)
        f = dv['fase'][n]
        ruido = 0.6 * math.sin(ahora * 0.11 + f) + 0.4 * math.sin(ahora * 0.047 + f * 1.7)
        p.val = min(max(v0 + ruido * rango * (hi - lo), lo), hi)


# ------------------------------------------------------------------ cambio con fundido
def cambiar(c, motivo):
    d = st()
    if c is None:
        return
    sw, b, cr = R.op('switch2'), R.op('piloto_b'), R.op('piloto_cross')
    dur = float(par('Pilototransdur', 1.5))
    if par('Pilototransicion', 'fundido') == 'corte' or b is None or cr is None or dur < 0.05:
        deriva_parar()
        sw.par.index = c[3]
        d['esperado'] = c[3]
        terminar_cambio(c, motivo)
        return
    b.par.index = c[3]
    d['trans'] = {'c': list(c), 't0': time.time(), 'dur': dur, 'motivo': motivo}


def terminar_cambio(c, motivo):
    d = st()
    ahora = time.time()
    d['ultimo'] = ahora
    d['cambios'] += 1
    d['desde_logo'] = 0 if c[0] in P.fetch('logos_cache', [11], search=False) else d['desde_logo'] + 1
    d['malo'] = None
    programar(d, ahora)
    deriva_empezar(c[3])
    P.store('ahora_txt', '%d-%d %s' % (c[0], c[1], c[2]))
    if motivo != 'tiempo':
        log('cambio (%s) -> %d-%d %s' % (motivo, c[0], c[1], c[2]))


def trans_tick():
    d = st()
    t = d['trans']
    if not t:
        return
    sw, b, cr = R.op('switch2'), R.op('piloto_b'), R.op('piloto_cross')
    k = min(1.0, (time.time() - t['t0']) / t['dur'])
    cr.par.cross = k * k * (3 - 2 * k)
    if k >= 1.0:
        deriva_parar()
        c = t['c']
        sw.par.index = c[3]
        d['esperado'] = c[3]
        cr.par.cross = 0.0
        d['trans'] = None
        terminar_cambio(c, t['motivo'])


# ------------------------------------------------------------------ vigia de video
def medir():
    t = P.op('vigia_res')
    a = t.numpyArray(delayed=True)
    if a is None or a.size == 0:
        return None, None
    import numpy as np
    lum = a[:, :, :3].max(axis=2)
    return float(np.percentile(lum, 99.5)), float((lum > 0.97).mean())   # pico (no media): lineas finas en negro = ok


def reset_feedback(entrada):
    b = base_de(entrada)
    n = 0
    if b is not None:
        for f in b.findChildren(type=feedbackTOP):
            try:
                f.par.resetpulse.pulse()
                n += 1
            except Exception:
                pass
    return n


def vigia_tick(ahora, piloto_on):
    d = st()
    d['vigia_n'] += 1
    if not par('Vigia', True) or d['trans'] or float(S.par.Master.eval()) < 0.5:
        d['malo'] = None
        return
    lum, sat = medir()
    if lum is None:
        return
    P.store('vigia_txt', 'pico %.2f · saturado %.0f%%' % (lum, sat * 100))
    malo = 'NEGRO' if lum < float(par('Vigianegro', 0.05)) else ('SATURADO' if sat > float(par('Vigiasat', 0.6)) else None)
    if malo is None:
        d['malo'] = None
        return
    if d['malo'] != malo:
        d['malo'], d['malo_t'], d['malo_reset'] = malo, ahora, False
        return
    tol = float(par('Vigiatol', 4.0))
    e = int(R.op('switch2').par.index.eval())
    if ahora - d['malo_t'] > tol and not d.get('malo_reset'):
        n = reset_feedback(e)
        d['malo_reset'] = True
        d['resets'] += 1
        log('VIGIA %s en %s: reinicio %d feedback' % (malo, nombre_de(e), n))
    elif ahora - d['malo_t'] > 2 * tol and d.get('malo_reset'):
        if piloto_on:
            d['saltos'] += 1
            log('VIGIA %s sigue en %s: lo salto' % (malo, nombre_de(e)))
            cambiar(elegir_siguiente(), 'vigia')
        d['malo'] = None


# ------------------------------------------------------------------ registro de resistencia
def soak_tick(ahora):
    d = st()
    cada = float(par('Pilotoregistro', 5.0)) * 60.0
    if cada <= 0 or ahora - d['soak_t'] < cada:
        return
    frames = absTime.frame - d['f0']
    fps = frames / max(ahora - d['soak_t'], 0.001) if d['soak_t'] else 0.0
    d['soak_t'], d['f0'] = ahora, absTime.frame
    pf = P.op('piloto_perform')
    vals = {c.name: round(c.eval(), 2) for c in pf.chans()} if pf is not None else {}
    nuevo = not os.path.exists(SOAK)
    cols = sorted(vals)
    try:
        with open(SOAK, 'a', encoding='utf-8') as f:
            if nuevo:
                f.write('hora,fps_real,visual,cambios,resets_vigia,saltos_vigia,audio_low,' + ','.join(cols) + '\n')
            m = op('/project2/audio/master_audio')
            low = round(float(m['low'].eval()), 3) if m is not None and m['low'] is not None else ''
            f.write('%s,%.1f,%s,%d,%d,%d,%s,%s\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), fps,
                    nombre_de(int(R.op('switch2').par.index.eval())).replace(',', ' '), d['cambios'], d['resets'],
                    d['saltos'], low, ','.join(str(vals[c]) for c in cols)))
    except Exception:
        pass


# ------------------------------------------------------------------ cada cuadro
def tick():
    d = st()
    ahora = time.time()
    on = bool(par('Pilotoauto', False))
    m = op('/project2/audio/master_audio')
    e = sum(float(m[c].eval()) for c in ('low', 'kick') if m is not None and m[c] is not None)
    kick = float(m['kick'].eval()) if m is not None and m['kick'] is not None else 0.0
    d['fast'] += (e - d['fast']) * 0.08
    d['slow'] += (e - d['slow']) * 0.002
    golpe = kick > 0.5 and d['kick_prev'] <= 0.5
    d['kick_prev'] = kick
    trans_tick()
    if absTime.frame % 15 == 0:
        vigia_tick(ahora, on)
    soak_tick(ahora)
    sw = R.op('switch2')
    idx = int(sw.par.index.eval())
    if d['esperado'] is None:
        d['esperado'] = idx
    if idx != d['esperado'] and not d['trans']:
        # alguien toco un pad: se respeta y se pausa
        d['esperado'] = idx
        deriva_parar()
        b = R.op('piloto_b')
        if b is not None:
            b.par.index = idx                       # que no se quede cocinando el visual anterior
        if on:
            d['pausa'] = ahora + float(par('Pilotoretomar', 20.0))
            programar(d, d['pausa'])
            log('manual -> %s · piloto en pausa %ds' % (nombre_de(idx), par('Pilotoretomar', 20.0)))
        P.store('ahora_txt', nombre_de(idx))
    if not on:
        if d.get('deriva'):
            deriva_parar()
        d['prox'] = 0.0
        return
    if absTime.frame % 3 == 0:
        deriva_tick(ahora)
    if d['trans'] or par('Pilotoquedarse', False) or ahora < d['pausa']:
        if par('Pilotoquedarse', False):
            d['prox'] = max(d['prox'], ahora + 1.0)
        return
    if d['prox'] <= 0:
        programar(d, ahora)
        deriva_empezar(idx)
        return
    minimo = float(par('Pilotominimo', 8.0))
    drop = (par('Pilotodrop', True) and ahora - d['ultimo'] > minimo and d['fast'] > 0.15 and
            d['fast'] > d['slow'] * (1.4 + 1.6 * (1.0 - float(par('Pilotodropsens', 0.5)))))
    if not (drop or ahora >= d['prox']):
        d['espera_kick'] = 0.0
        return
    if par('Pilotoenkick', True) and not golpe:
        if not d['espera_kick']:
            d['espera_kick'] = ahora
        if ahora - d['espera_kick'] < 2.0:        # sin kick en 2 s, cambia igual
            return
    d['espera_kick'] = 0.0
    cambiar(elegir_siguiente(), 'drop' if drop else 'tiempo')
    if drop:
        d['slow'] = d['fast']                       # que un mismo drop no dispare dos veces


def siguiente():
    if not st()['trans']:
        cambiar(elegir_siguiente(), 'boton')


def estado_txt():
    d = st()
    if not par('Pilotoauto', False):
        return 'AUTO'
    if par('Pilotoquedarse', False):
        return 'AUTO · AQUI'
    ahora = time.time()
    if ahora < d['pausa']:
        return 'AUTO · PAUSA %d' % (d['pausa'] - ahora)
    falta = max(0, int(d['prox'] - ahora))
    return 'AUTO %d:%02d' % (falta // 60, falta % 60)


def chip_rgb(k):
    """color del chip: gris apagado · verde corriendo · rojo si el vigia actuo hace poco · ambar en pausa."""
    d = st()
    if not par('Pilotoauto', False):
        return (0.25, 0.25, 0.27)[k]
    if d.get('malo'):
        return (0.85, 0.12, 0.10)[k]
    if time.time() < d['pausa'] or par('Pilotoquedarse', False):
        return (0.75, 0.50, 0.08)[k]
    return (0.10, 0.50, 0.25)[k]
