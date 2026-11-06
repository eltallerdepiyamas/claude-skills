# =============================================================
# setup_demo.py  —  DEMO automatico de las escenas modulares + GRABACION (botones del Stream Deck)
#
# Pestaña "Demo" en escena_modular:
#   Demo              on/off: recorre todas las escenas (menu Modoescena), una cada "Segundos por escena".
#                     En cada escena mueve sus 5 parametros, UNO POR UNO (sube, baja y regresa a su valor,
#                     siempre suave), para que se vea lo que hace cada uno. Al cambiar de escena el Stream Deck
#                     salta solo a AJUSTES y muestra esos parametros moviendose.
#   Democada          segundos por escena (11 por default)
#   Demograbar        al prender el demo empieza a grabar; al terminar deja de grabar
#   Demounavez        da UNA vuelta a todas las escenas y para (si no, sigue en loop)
#   Demotexto         en la GRABACION (no en la salida en vivo) pone el nombre de la escena y del parametro
#                     que se esta moviendo, con su %
#   Rec               grabar ya (con o sin demo). Cada grabacion es un archivo nuevo en renders/
#   Recsel            FUENTE: Camaras + FX (fit2) / Visuales (fit1) / Escena sin FX / Otro TOP
#   Recfuente         el TOP que se graba con FUENTE = Otro TOP
#   Recaudio          on/off: grabar con pista de audio
#   Recaudiochop      el CHOP de audio que se graba (el script pone el primer Audio Device In del proyecto;
#                     cambialo si el bueno es otro). OJO: el audio en bruto, no el analisis low/mid/high (null4)
#   Recarchivo        (solo lectura) el ultimo archivo grabado
#
# Nodos: demo_exec (Execute DAT), demo_fuente (Select) -> demo_texto (Text) + demo_over (Over) -> demo_rec
# (Movie File Out). Todo dentro de escena_modular.
# Lo corre actualizar_companion.py. Solo, en el Textport:
#   exec(open(project.folder + '/control/setup_demo.py', encoding='utf-8').read())
# Se puede volver a correr: conserva los valores de la pestaña Demo.
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'
REC_DEFAULT = ['/project2/fit2', '/project2/switch23']
# FUENTE de la grabacion (boton FUENTE del Stream Deck las recorre). 'otro' = el TOP que pongas en Recfuente
REC_SOURCES = [('camarasfx', 'Camaras + FX', '/project2/fit2'),
               ('visuales', 'Visuales', '/project2/fit1'),
               ('escena', 'Escena sin FX', '/project2/base17/out1'),
               ('otro', 'Otro TOP', '')]

CODE = r'''# generado por control/setup_demo.py — demo automatico de escenas + grabacion
import math, os, time

S = op(%(scene)r)
CONTRACT = ['Mezcla', 'Tiempo', 'Distorsion', 'Color', 'Firma']
INTRO = 1.0          # segundos limpios al entrar a la escena (y al final)


def five(comp):
    """Los 5 parametros de la escena (los mismos que muestra AJUSTES), solo los que se pueden mover."""
    if comp is None:
        return []
    if all(getattr(comp.par, n, None) is not None for n in CONTRACT):
        ps = [getattr(comp.par, n, None) for n in CONTRACT]
    else:
        pg = next((g for g in comp.customPages if g.name in ('Layout', 'Visual', 'Filter')), None)
        ps = [p for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')][:5] if pg else []
    return [p for p in ps if p is not None and p.mode == type(p.mode).CONSTANT and not p.readOnly]


def rango(p):
    lo, hi = p.normMin, p.normMax
    if lo == hi:
        lo, hi = p.min, p.max
    return lo, hi


def pct(p):
    lo, hi = rango(p)
    return '' if hi == lo else '%%d%%%%' %% round(max(0.0, min(1.0, (float(p.eval()) - lo) / (hi - lo))) * 100)


def short(label):
    parts = label.split(' ', 1)
    return parts[1] if len(parts) == 2 and parts[0].isdigit() else label


def restore():
    comp = op(me.fetch('comp', '', storeDefault=False) or '/')
    for name, v in (me.fetch('orig', {}, storeDefault=False) or {}).items():
        p = getattr(comp.par, name, None) if comp is not None else None
        if p is not None and p.mode == type(p.mode).CONSTANT:
            p.val = v
    me.store('orig', {})


def begin(now):
    p = S.par.Modoescena
    comp = S.op(p.eval())
    me.store('t0', now)
    me.store('comp', comp.path if comp is not None else '')
    me.store('orig', {q.name: q.eval() for q in five(comp)})


def animate(t, cada):
    comp = op(me.fetch('comp', '', storeDefault=False) or '/')
    orig = me.fetch('orig', {}, storeDefault=False) or {}
    pars = [getattr(comp.par, n) for n in orig] if comp is not None else []
    activo = None
    if pars:
        w = max(0.5, (cada - 2 * INTRO) / len(pars))
        for i, p in enumerate(pars):
            u = (t - INTRO - i * w) / w
            if 0.0 <= u <= 1.0:
                # sube, baja y regresa: arranca y termina con velocidad 0 (sin brincos)
                off = math.sin(2 * math.pi * u) * math.sin(math.pi * u) * 1.3
                off = max(-1.0, min(1.0, off))
                lo, hi = rango(p)
                o = orig[p.name]
                v = o + off * ((hi - o) if off > 0 else (o - lo))
                p.val = int(round(v)) if p.isInt else v
                activo = p
            elif p.eval() != orig[p.name]:
                p.val = orig[p.name]
    lbl = S.par.Modoescena.menuLabels[S.par.Modoescena.menuIndex].upper()
    txt = lbl + ('\n' + short(activo.label).upper() + '  ' + pct(activo) if activo is not None else '')
    texto(txt)


def texto(txt):
    t = S.op('demo_texto')
    if t is not None:
        want = txt if S.par.Demotexto.eval() else ''
        if t.par.text.eval() != want:
            t.par.text = want


def audio_chop():
    """El CHOP de audio que se graba. Si es un Audio Device Out (la salida a bocinas), se graba lo que
    le ENTRA (la musica); un CHOP de analisis (low/mid/high a 60 fps) no sirve: no es sonido."""
    if not S.par.Recaudio.eval():
        return None
    c = S.par.Recaudiochop.eval()
    if c is not None and c.OPType == 'audiodeviceoutCHOP' and c.inputs:
        c = c.inputs[0]
    if c is not None and c.rate < 8000:
        debug('demo_rec: %%s corre a %%g por segundo: no es audio, grabo sin sonido' %% (c.path, c.rate))
        return None
    return c


def rec_sync():
    mo = S.op('demo_rec')
    if mo is None:
        return
    want = bool(S.par.Rec.eval())
    if want and not mo.par.record.eval():
        # el audio se conecta justo antes de grabar (asi siempre va el que diga la pestana Demo)
        ap = getattr(mo.par, 'audiochop', None)
        if ap is not None:
            ach = audio_chop()
            if ap.mode != type(ap.mode).CONSTANT:
                ap.mode = type(ap.mode).CONSTANT
            ap.val = ach.path if ach is not None else ''
        folder = project.folder + '/renders'
        os.makedirs(folder, exist_ok=True)
        f = folder + '/rec_' + time.strftime('%%Y%%m%%d_%%H%%M%%S') + '.mov'
        mo.par.file = f
        S.par.Recarchivo.val = f
        mo.par.record = True
    elif not want and mo.par.record.eval():
        mo.par.record = False


def onFrameStart(frame):
    p = S.par
    rec_sync()
    activo = me.fetch('activo', False, storeDefault=False)
    if not p.Demo.eval():
        if activo:
            restore()
            me.store('activo', False)
            if p.Demograbar.eval():
                p.Rec.val = False
            texto('')
        return
    now = absTime.seconds
    if not activo:
        me.store('activo', True)
        me.store('inicio', p.Modoescena.menuIndex)
        begin(now)
        if p.Demograbar.eval():
            p.Rec.val = True
        return
    t = now - me.fetch('t0', now, storeDefault=False)
    cada = max(3.0, float(p.Democada.eval()))
    if t >= cada:
        restore()
        n = len(p.Modoescena.menuNames)
        sig = (p.Modoescena.menuIndex + 1) %% max(n, 1)
        if p.Demounavez.eval() and sig == me.fetch('inicio', 0, storeDefault=False):
            p.Demo.val = False          # dio la vuelta: el siguiente frame apaga (y deja de grabar)
            return
        p.Modoescena.menuIndex = sig
        begin(now)
        return
    animate(t, cada)
    return
''' % {'scene': SCENE_PATH}


def _page(scene):
    pg = next((g for g in scene.customPages if g.name == 'Demo'), None)
    return pg if pg is not None else scene.appendCustomPage('Demo')


def _toggle(pg, name, label, default):
    p = getattr(pg.owner.par, name, None)
    if p is None:
        p = pg.appendToggle(name, label=label)[0]
        p.val = default
    p.label = label
    return p


def _node(scene, optype, name, x, y):
    o = scene.op(name)
    if o is None:
        o = scene.create(optype, name)
    o.nodeX, o.nodeY = x, y
    return o


def _try(o, name, value):
    p = getattr(o.par, name, None)
    if p is None:
        return False
    try:
        p.val = value
        return True
    except Exception:
        return False


def run():
    scene = op(SCENE_PATH)
    if scene is None:
        print('[error] no encuentro', SCENE_PATH)
        return
    pg = _page(scene)
    _toggle(pg, 'Demo', 'Demo automatico', False)
    p = getattr(scene.par, 'Democada', None)
    if p is None:
        p = pg.appendFloat('Democada', label='Segundos por escena')[0]
        p.val = 11.0
    p.label = 'Segundos por escena'
    p.min, p.max, p.normMin, p.normMax = 3.0, 30.0, 3.0, 30.0
    p.clampMin = p.clampMax = True
    p.default = 11.0
    _toggle(pg, 'Demograbar', 'Grabar el demo', True)
    _toggle(pg, 'Demounavez', 'Una vuelta y para', True)
    _toggle(pg, 'Demotexto', 'Nombres en la grabacion', True)
    _toggle(pg, 'Rec', 'Grabar', False)
    f = getattr(scene.par, 'Recfuente', None)
    if f is None:
        f = pg.appendTOP('Recfuente', label='Que se graba')[0]
        f.val = next((s for s in REC_DEFAULT if op(s) is not None), '')
    f.label = 'Que se graba'
    fuentes = [s for s in REC_SOURCES if s[0] == 'otro' or op(s[2]) is not None]
    m = getattr(scene.par, 'Recsel', None)
    if m is None:
        m = pg.appendMenu('Recsel', label='Fuente')[0]
    m.label = 'Fuente'
    keep = m.eval()
    m.menuNames = [s[0] for s in fuentes]
    m.menuLabels = [s[1] for s in fuentes]
    if keep in m.menuNames:
        m.val = keep
    _toggle(pg, 'Recaudio', 'Grabar con audio', True)
    ac = getattr(scene.par, 'Recaudiochop', None)
    if ac is None:
        ac = pg.appendCHOP('Recaudiochop', label='Audio que se graba')[0]
    ac.label = 'Audio que se graba'
    if ac.eval() is None:
        cands = []
        for t in ('audiodeviceinCHOP', 'audiofileinCHOP', 'audiostreaminCHOP', 'audiondiCHOP'):
            cls = globals().get(t) or getattr(td, t, None)
            if cls is not None:
                cands += [o for o in op('/').findChildren(type=cls) if not o.path.startswith('/local')]
        if cands:
            ac.val = cands[0].path
    a = getattr(scene.par, 'Recarchivo', None)
    if a is None:
        a = pg.appendStr('Recarchivo', label='Ultimo archivo')[0]
    a.label = 'Ultimo archivo'
    a.readOnly = True
    scene.par.Rec.val = False          # nunca arranca grabando
    scene.par.Demo.val = False

    x, y = -1400, -1500
    sel = _node(scene, selectTOP, 'demo_fuente', x, y)
    rutas = {k: r for k, _l, r in fuentes if k != 'otro'}
    sel.par.top.expr = ("parent().par.Recfuente.eval() if parent().par.Recsel.eval() == 'otro' "
                        "else %r.get(parent().par.Recsel.eval(), '')" % rutas)
    txt = _node(scene, textTOP, 'demo_texto', x, y - 150)
    txt.par.text = ''
    _try(txt, 'outputresolution', 'custom')
    for n, e in (('resolutionw', "op('demo_fuente').width"), ('resolutionh', "op('demo_fuente').height")):
        if hasattr(txt.par, n):
            getattr(txt.par, n).expr = e
    _try(txt, 'alignx', 'left')
    _try(txt, 'aligny', 'bottom')
    _try(txt, 'fontsizex', 48)
    _try(txt, 'positionx', 60)
    _try(txt, 'positiony', 60)
    _try(txt, 'bgalpha', 0)
    over = _node(scene, overTOP, 'demo_over', x + 200, y - 75)
    over.inputConnectors[0].connect(txt)
    over.inputConnectors[1].connect(sel)
    rec = _node(scene, moviefileoutTOP, 'demo_rec', x + 400, y - 75)
    rec.inputConnectors[0].connect(over)
    rec.par.record = False
    # pista de audio (Movie File Out -> Audio CHOP); el nombre del parametro cambia entre versiones de TD
    apar = next((getattr(rec.par, n) for n in ('audiochop', 'audio') if hasattr(rec.par, n)), None)
    if apar is not None:
        apar.mode = type(apar.mode).CONSTANT   # lo pone demo_exec al empezar cada grabacion
    else:
        print('[aviso] demo_rec: no encontre el parametro Audio CHOP del Movie File Out; ponlo a mano')
    acodec = getattr(rec.par, 'audiocodec', None)
    if acodec is not None:
        pick = next((c for pref in ('pcm16', 'alac', 'pcm') for c in acodec.menuNames if pref in c.lower()), None)   # .mov: PCM sin perdida (mp3 en .mov da problemas)
        if pick:
            acodec.val = pick
    _try(rec, 'type', 'movie')
    codec = getattr(rec.par, 'videocodec', None)
    if codec is not None:
        pick = next((c for pref in ('h264', 'hevc', 'hap', 'prores') for c in codec.menuNames if pref in c.lower()), None)
        if pick:
            codec.val = pick
    ex = scene.op('demo_exec')
    if ex is not None:
        ex.destroy()
    ex = scene.create(executeDAT, 'demo_exec')
    ex.nodeX, ex.nodeY = x, y + 150
    ex.text = CODE
    for t in ('start', 'create', 'exit', 'frameend', 'playstatechange', 'devicechange',
              'projectpresave', 'projectpostsave'):
        if hasattr(ex.par, t):
            setattr(ex.par, t, False)
    ex.par.framestart = True
    print('[ok] demo + grabacion: pestaña Demo en escena_modular. Graba', m.menuLabels[m.menuIndex],
          '->', project.folder + '/renders/', '(codec %s)' % (codec.eval() if codec is not None else '?'))
    if ac.eval() is not None:
        print('     audio:', ac.eval().path, '(si no es el bueno, cambia "Audio que se graba" en la pestaña Demo)')
    else:
        print('[aviso] no encontre un Audio Device In: pon el CHOP de audio en "Audio que se graba" (pestaña Demo)')


run()
