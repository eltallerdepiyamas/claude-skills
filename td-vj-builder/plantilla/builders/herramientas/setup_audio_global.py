# ─────────────────────────────────────────────────────────────
# setup_audio_global.py — control GLOBAL de la audio-reactividad (pestaña Audio del hub /project2/show).
# Lo que se toca EN VIVO, una vez para todo (escenas, visuales, FX), sin entrar base por base:
#   · Autonivel  cada banda (low / mid / high) se mide contra su propio pico de los últimos segundos:
#                un track suave y uno fuerte empujan igual, sin mover el Gain. OFF = nivel crudo (como antes).
#   · Reaccion   cuánto empuja el audio a TODO (0 = nada · 1 = normal · 2 = el doble).
#   · Suavizado  qué tan nervioso responde todo (0 = crudo · 1 = lento, sube rápido y baja despacio).
# La pestaña Audio de cada escena (target, bandas, Mult, Smooth) queda igual: es el ajuste fino por escena.
#
# Red (en /project2/audio, tag tdvj_audglob), insertada justo antes de master_audio:
#   <analisis> -> audio_crudo -> audglob_bandas -> [audglob_pico -> audglob_piso -> audglob_norm]
#   -> audglob_auto -> audglob_reac -> audglob_suave -> audglob_out (reemplaza low/mid/high) -> master_audio
# Los demás canales (kick, snare...) pasan intactos. Paleta Audio lee audio_crudo (sus golpes no cambian).
# No toca el contrato de Audio de las bases. Idempotente. Para quitarlo: QUITAR = True y volver a correr.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_audio_global.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────
QUITAR = False
TAG = 'tdvj_audglob'
REL = 8.0        # s que tarda en "olvidar" el pico (Autonivel)
PISO = 0.12      # pico minimo: por debajo de esto no se amplifica mas (silencio = silencio)
BANDAS = 'low mid high'

A = op('/project2/audio')
M = A.op('master_audio')
HUB = op('/project2/show')


def pone(o, **vals):
    for k, v in vals.items():
        p = getattr(o.par, k, None)
        if p is not None:
            p.val = v


def hub_pars():
    pg = next((g for g in HUB.customPages if g.name == 'Audio'), None) or HUB.appendCustomPage('Audio')
    if getattr(HUB.par, 'Sepreaccion', None) is None:
        pg.appendHeader('Sepreaccion', label='Reaccion global (en vivo)')
    if getattr(HUB.par, 'Autonivel', None) is None:
        p = pg.appendToggle('Autonivel', label='Autonivel')[0]
        p.val = False
    HUB.par.Autonivel.default = False
    for name, label, lo, hi, dflt in (('Reaccion', 'Reaccion', 0.0, 2.0, 1.0), ('Suavizado', 'Suavizado', 0.0, 1.0, 0.0)):
        p = getattr(HUB.par, name, None)
        if p is None:
            p = pg.appendFloat(name, label=label)[0]
            p.val = dflt
        p.min, p.max, p.normMin, p.normMax = lo, hi, lo, hi
        p.clampMin = p.clampMax = True
        p.default = dflt


def fuente():
    """Lo que alimentaba a master_audio antes del control global."""
    crudo = A.op('audio_crudo')
    if crudo is not None and crudo.inputs:
        return crudo.inputs[0]
    return M.inputs[0] if M.inputs else None


def run():
    if M is None or HUB is None:
        print('[falla] no existe /project2/audio/master_audio o /project2/show')
        return
    src = fuente()
    if src is None:
        print('[falla] master_audio no tiene entrada')
        return
    M.inputConnectors[0].connect(src)             # primero se puentea: nunca queda sin audio
    for c in list(A.children):
        if c.valid and TAG in c.tags:
            c.destroy()
    pal = op('/project2/base17/escena_modular/palaudio_sel')
    if QUITAR:
        if pal is not None:
            pal.par.chop = M.path
        print('[ok] control global de audio quitado (master_audio directo)')
        return
    hub_pars()
    x0, y0 = M.nodeX - 1500, M.nodeY - 260
    h = "op('/project2/show').par."

    def new(tipo, name, dx, dy, *ins):
        n = A.create(tipo, name)
        n.tags.add(TAG)
        n.nodeX, n.nodeY = x0 + dx, y0 + dy
        for i, s in enumerate(ins):
            n.inputConnectors[i].connect(s)
        return n

    crudo = new(nullCHOP, 'audio_crudo', 0, 0, src)
    crudo.comment = 'audio analizado ANTES del control global (lo lee Paleta Audio)'
    band = new(selectCHOP, 'audglob_bandas', 180, 0)
    band.par.chop = crudo.path
    band.par.channames = BANDAS
    pico = new(lagCHOP, 'audglob_pico', 360, -110, band)
    pone(pico, lagunit='seconds', lag1=0.0, lag2=REL)
    piso = new(limitCHOP, 'audglob_piso', 540, -110, pico)
    pone(piso, type='clamp', min=PISO, max=100.0)
    norm = new(mathCHOP, 'audglob_norm', 720, -110, band, piso)
    norm.par.chopop = 'div'
    auto = new(switchCHOP, 'audglob_auto', 900, 0, band, norm)
    auto.par.index.expr = 'int(%sAutonivel)' % h
    reac = new(mathCHOP, 'audglob_reac', 1080, 0, auto)
    reac.par.gain.expr = h + 'Reaccion'
    suave = new(lagCHOP, 'audglob_suave', 1260, 0, reac)
    pone(suave, lagunit='seconds')
    suave.par.lag1.expr = '0.12 * %sSuavizado' % h
    suave.par.lag2.expr = '0.60 * %sSuavizado' % h
    out = new(replaceCHOP, 'audglob_out', 1440, 0, crudo, suave)
    out.comment = 'low / mid / high con Autonivel · Reaccion · Suavizado del hub · setup_audio_global.py'
    faltan = [b for b in BANDAS.split() if out[b] is None] + [c.name for c in crudo.chans() if out[c.name] is None]
    if out.numChans != crudo.numChans or faltan:
        print('[falla] audglob_out no conserva los canales (%s): master_audio se queda directo' % faltan)
        return
    M.inputConnectors[0].connect(out)
    if pal is not None:
        pal.par.chop = crudo.path
    print('[ok] control global de audio: %d canales · Autonivel %s · Reaccion %.2f · Suavizado %.2f' % (
        M.numChans, 'ON' if HUB.par.Autonivel.eval() else 'OFF', HUB.par.Reaccion.eval(), HUB.par.Suavizado.eval()))

run()
