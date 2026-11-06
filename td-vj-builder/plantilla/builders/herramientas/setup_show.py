# ─────────────────────────────────────────────────────────────
# setup_show.py — HUB MAESTRO /project2/show (resolucion · audio · color final). Idempotente.
# Es la pieza fija del boilerplate: todo lo del show lee de aqui.
#
#  Resolucion  W / H        -> escena_modular.W/H lo siguen (y de ahi layouts, visuales, FX, /project1).
#  Audio       Fuente       Archivo (prueba) / En vivo (Audio Device In: elegir el dispositivo en
#                           /project2/audio/audio_vivo) · Archivo · Gain · Monitor (sacar el audio por bocinas).
#              /project1: audio_fuente (switch) -> audio_gain -> switch6 -> audioAnalysis -> null4
#              (= AUDIO_SOURCE de rig.py: lo que mueve el audio de layouts / visuales / FX).
#              REC graba audio_gain (pestana Demo de escena_modular).
#  Color       Bypass · Brillo · Contraste · Negros · Saturacion · Temperatura · Master
#              -> /project1/color_final (GLSL, donde estaba lumalevel1: despues de los FX y del
#              proceso de /project1, antes de overlays / strobe / NDI).
#              MIDImix (knobs que estaban libres): CC51 Saturacion · CC55 Contraste · CC59 Brillo ·
#              CC60 Negros (el mismo knob que movia el blacklevel del luma) · fader CC57 Master.
#              Temperatura: solo en la UI / pestana (no hay knob libre). 'Color MIDI' apaga los knobs.
#  Lo que sale (lumalevel1, math30 = suma de los 2 archivos, audiofilein1 = mp3 de ejemplo de TD)
#  va a /project2/_respaldo/project1_hub (no se borra).
# ─────────────────────────────────────────────────────────────
R2, R1 = op('/project2'), op('/project1')
AUD = op('/project2/audio') or R1          # el audio vive en /project2/audio (limpiar_project1.py)
ESC = op('/project2/base17/escena_modular')
SHADER = project.folder + '/shaders/master/color_final.frag'
MIDI_IN = '/project2/midi_midiin1'
COLOR_CC = {           # cc -> (parametro, min, max)
    51: ('Brillo', 0.0, 2.0),
    55: ('Contraste', 0.5, 1.5),
    59: ('Negros', 0.0, 0.3),
    52: ('Saturacion', 0.0, 2.0),
    63: ('Master', 0.0, 1.0),
    16: ('Audiogain', 0.0, 2.0),
}
S = "op('/project2/show')"


def page(c, name):
    return next((p for p in c.customPages if p.name == name), None) or c.appendCustomPage(name)


def fpar(pg, c, name, label, mn, mx, d):
    if not hasattr(c.par, name):
        p = pg.appendFloat(name, label=label)[0]
        p.val = d
    p = getattr(c.par, name)
    p.label = label
    p.normMin, p.normMax, p.default = mn, mx, d
    return p


def respaldo(ops, dest='project1_hub'):
    ops = [o for o in ops if o is not None]
    if not ops:
        return []
    r = R2.op('_respaldo')
    d = r.op(dest) or r.create(baseCOMP, dest)
    d.copyOPs(ops)
    d.allowCooking = False
    names = [o.path for o in ops]
    for o in ops:
        o.destroy()
    return names


def hub():
    c = R2.op('show') or R2.create(baseCOMP, 'show')
    c.comment = 'HUB MAESTRO: resolucion · audio · color final (builders/herramientas/setup_show.py)'
    c.color = (0.08, 0.72, 0.72)
    # --- Resolucion
    pg = page(c, 'Resolucion')
    if not hasattr(c.par, 'W'):
        w = pg.appendInt('W', label='Ancho')[0]
        h = pg.appendInt('H', label='Alto')[0]
        w.val = int(ESC.par.W.eval()) if ESC is not None and hasattr(ESC.par, 'W') else 1920
        h.val = int(ESC.par.H.eval()) if ESC is not None and hasattr(ESC.par, 'H') else 1080
    c.par.W.normMin, c.par.W.normMax = 640, 3840
    c.par.H.normMin, c.par.H.normMax = 360, 2160
    # --- Audio
    pg = page(c, 'Audio')
    if not hasattr(c.par, 'Audiofuente'):
        m = pg.appendMenu('Audiofuente', label='Fuente de audio')[0]
        m.menuNames, m.menuLabels = ['archivo', 'vivo'], ['Archivo (prueba)', 'En vivo (entrada)']
        m.val = 'archivo'
        f = pg.appendFile('Audioarchivo', label='Archivo')[0]
        lm = AUD.op('Little_Jesus___La_Magia')
        f.val = lm.par.file.eval() if lm is not None else ''
        fpar(pg, c, 'Audiogain', 'Gain', 0.0, 4.0, 1.0)
        pg.appendToggle('Audiomonitor', label='Monitor (bocinas)')
    # --- Correccion de color
    for g_ in c.customPages:
        if g_.name == 'Color':
            g_.name = 'Correccion de color'
    if hasattr(c.par, 'Temperatura'):
        c.par.Temperatura.destroy()
    pg = page(c, 'Correccion de color')
    if not hasattr(c.par, 'Colorbypass'):
        pg.appendToggle('Colorbypass', label='Bypass color')
    fpar(pg, c, 'Brillo', 'Brillo', 0.0, 2.0, 1.0)
    fpar(pg, c, 'Contraste', 'Contraste', 0.5, 1.5, 1.0)
    fpar(pg, c, 'Negros', 'Negros', 0.0, 0.3, 0.0)
    fpar(pg, c, 'Saturacion', 'Saturacion', 0.0, 2.0, 1.0)
    fpar(pg, c, 'Master', 'Master (a negro)', 0.0, 1.0, 1.0)
    if hasattr(c.par, 'Colormidi'):
        c.par.Colormidi.destroy()            # los knobs quedan siempre activos
    return c


def color_midi(c):
    sel = c.op('color_midi') or c.create(selectCHOP, 'color_midi')
    sel.par.chops = MIDI_IN
    sel.par.channames = ' '.join('ch1ctrl%d' % k for k in COLOR_CC)
    sel.nodeX, sel.nodeY = 0, 0
    ex = c.op('color_midi_exec') or c.create(chopexecuteDAT, 'color_midi_exec')
    ex.par.chops = sel
    ex.par.valuechange = True
    ex.par.offtoon = ex.par.ontooff = ex.par.whileon = ex.par.whileoff = False
    ex.nodeX, ex.nodeY = 200, 0
    pg = page(c, 'Correccion de color')
    if not hasattr(c.par, 'Ultimomidi'):
        pg.appendStr('Ultimomidi', label='Ultimo MIDI movido')
    u = c.op('midi_ultimo') or c.create(chopexecuteDAT, 'midi_ultimo')
    u.par.valuechange = True
    u.par.offtoon = u.par.ontooff = u.par.whileon = u.par.whileoff = False
    u.nodeX, u.nodeY = 200, -160
    pg = page(c, 'Correccion de color')
    if not hasattr(c.par, 'Resetcolor'):
        pg.appendPulse('Resetcolor', label='Reset correccion')
    rx = c.op('color_reset') or c.create(parameterexecuteDAT, 'color_reset')
    rx.par.op = c
    rx.par.pars = 'Resetcolor'
    rx.par.onpulse = True
    rx.par.valuechange = False
    rx.nodeX, rx.nodeY = 200, -480
    rx.text = chr(10).join(['def onPulse(par):',
                            "    for n in ('Brillo', 'Contraste', 'Negros', 'Saturacion', 'Master'):",
                            '        p = getattr(parent().par, n)', '        p.val = p.default',
                            '    return', ''])
    # pad ch1n27: RESET de la escena activa (sliders + reloj + feedback; no toca los videos)
    ps = c.op('pad_reset_in') or c.create(selectCHOP, 'pad_reset_in')
    ps.par.chops = '/project2/control_p1/midiin1'
    ps.par.channames = 'ch1n27'
    ps.nodeX, ps.nodeY = 0, -320
    pe = c.op('pad_reset_exec') or c.create(chopexecuteDAT, 'pad_reset_exec')
    pe.par.chops = ps
    pe.par.offtoon = True
    pe.par.valuechange = pe.par.ontooff = pe.par.whileon = pe.par.whileoff = False
    pe.nodeX, pe.nodeY = 200, -320
    pe.text = chr(10).join(['def onOffToOn(channel, sampleIndex, val, prev):',
                            "    op('/project2/base17/escena_modular/oscin1_callbacks').module.resetActivo(escena=True, videos=False)",
                            '    return', ''])
    mapa = ', '.join("%d: ('%s', %g, %g)" % (k, n, a, b) for k, (n, a, b) in COLOR_CC.items())
    ex.text = (
        "# MIDImix -> pestana Color del hub (lo escribe setup_show.py; no editar aqui)\n"
        "MAPA = {%s}\n\n"
        "def onValueChange(channel, sampleIndex, val, prev):\n"
        "\tc = parent()\n"
        "\ttry:\n"
        "\t\tcc = int(channel.name.replace('ch1ctrl', ''))\n"
        "\texcept ValueError:\n"
        "\t\treturn\n"
        "\tif cc not in MAPA:\n"
        "\t\treturn\n"
        "\tname, lo, hi = MAPA[cc]\n"
        "\tv = val / 127.0 if val > 1.0001 or prev > 1.0001 else val\n"
        "\tgetattr(c.par, name).val = lo + min(max(v, 0.0), 1.0) * (hi - lo)\n"
        "\treturn\n" % mapa)


def resolucion(c):
    if ESC is not None and hasattr(ESC.par, 'W'):
        ESC.par.W.expr = S + '.par.W'
        ESC.par.H.expr = S + '.par.H'
    k = R1.op('constant3')            # color del strobe en /project1 (tenia 1920x1080 a mano)
    if k is not None:
        k.par.outputresolution = 'custom'
        k.par.resolutionw.expr = S + '.par.W'
        k.par.resolutionh.expr = S + '.par.H'


def audio(c):
    lm = AUD.op('Little_Jesus___La_Magia')
    sw6 = AUD.op('switch6')
    if lm is None or sw6 is None:
        print('[aviso] no encontre Little_Jesus___La_Magia o switch6 en /project1: audio sin tocar')
        return
    lm.par.file.expr = S + '.par.Audioarchivo'
    viv = AUD.op('audio_vivo') or AUD.create(audiodeviceinCHOP, 'audio_vivo')
    viv.par.active.expr = S + ".par.Audiofuente == 'vivo'"
    fu = AUD.op('audio_fuente') or AUD.create(switchCHOP, 'audio_fuente')
    for cn in reversed(list(fu.inputConnectors)):
        cn.disconnect()
    fu.inputConnectors[0].connect(lm)
    fu.inputConnectors[1].connect(viv)
    fu.par.index.expr = "['archivo', 'vivo'].index(%s.par.Audiofuente.eval())" % S
    g = AUD.op('audio_gain') or AUD.create(mathCHOP, 'audio_gain')
    g.inputConnectors[0].connect(fu)
    g.par.gain.expr = S + '.par.Audiogain'
    prom = [v for v in g.par.chanop.menuNames if 'av' in v.lower()]    # SIEMPRE mono: promedia los canales
    g.par.chanop = prom[0]
    for cn in reversed(list(sw6.inputConnectors)):
        cn.disconnect()
    sw6.inputConnectors[0].connect(g)
    sw6.par.index = 0
    mon = AUD.op('audiodevout1')
    if mon is not None:
        mon.inputConnectors[0].connect(g)
        mon.par.active.expr = S + '.par.Audiomonitor'
    x, y = sw6.nodeX, sw6.nodeY
    for o, dx, dy in ((lm, -800, 80), (viv, -800, -80), (fu, -600, 0), (g, -400, 0)):
        o.nodeX, o.nodeY = x + dx, y + dy
    if ESC is not None and hasattr(ESC.par, 'Recaudiochop'):
        ESC.par.Recaudiochop = g.path
    # En vivo: driver y dispositivo en la pestana Audio del hub (solo se ven activos con Fuente = En vivo)
    pg = page(c, 'Audio')
    for name, label, src in (('Audiodriver', 'Driver (en vivo)', 'driver'), ('Audiodevice', 'Dispositivo (en vivo)', 'device')):
        if not hasattr(c.par, name):
            pg.appendStrMenu(name, label=label)
        p = getattr(c.par, name)
        p.menuSource = "op('%s').par.%s" % (viv.path, src)
        if not p.eval():
            p.val = getattr(viv.par, src).eval()
        p.enableExpr = "me.par.Audiofuente == 'vivo'"
        getattr(viv.par, src).bindExpr = "op('/project2/show').par.%s" % name
        getattr(viv.par, src).mode = ParMode.BIND
    fuera = respaldo([AUD.op('math30'), AUD.op('audiofilein1')])
    if fuera:
        print('[ok] audio: al respaldo', fuera)


def color(c):
    lv = R1.op('lumalevel1')
    g = R1.op('color_final')
    if g is None:
        g = R1.create(glslTOP, 'color_final')
        if lv is not None:
            g.nodeX, g.nodeY = lv.nodeX, lv.nodeY - 160
    d = R1.op('color_final_frag') or R1.create(textDAT, 'color_final_frag')
    d.par.file = 'shaders/master/color_final.frag'
    d.par.syncfile = False
    d.text = open(SHADER, encoding='utf-8').read()
    d.nodeX, d.nodeY = g.nodeX, g.nodeY - 140
    g.par.pixeldat = d
    g.par.outputresolution = 'useinput'
    g.par.format = 'rgba16float'
    for k in range(1, 7):                  # color_final = solo Master; la correccion va en camN_cc
        getattr(g.par, 'uniname%d' % k).val = ''
        getattr(g.par, 'value%dx' % k).expr = ''
        getattr(g.par, 'value%dx' % k).mode = type(g.par.value0x.mode).CONSTANT
    g.par.uniname0.val = 'uMaster'
    g.par.value0x.expr = S + '.par.Master'
    g.bypass = False
    g.comment = 'COLOR FINAL · /project2/show -> pestana Color · shaders/master/color_final.frag'
    if lv is not None:
        src = lv.inputs[0] if lv.inputs else None
        dests = [(cn.owner, cn.index) for oc in lv.outputConnectors for cn in oc.connections]
        if src is not None:
            g.inputConnectors[0].connect(src)
        for owner, idx in dests:
            owner.inputConnectors[idx].connect(g)
        # el knob que movia el blacklevel del luma (CC60) ahora mueve Negros del hub
        print('[ok] color_final en lugar de lumalevel1 (%s -> color_final -> %s)' % (
            src.name if src else '-', ', '.join(o.name for o, _ in dests)))
        respaldo([lv])


c = hub()
color_midi(c)
resolucion(c)
audio(c)
color(c)
exec(open(project.folder + '/builders/herramientas/ordenar_hub.py', encoding='utf-8').read())
print('[ok] hub /project2/show listo · %dx%d · audio=%s · color bypass=%s' % (
    c.par.W.eval(), c.par.H.eval(), c.par.Audiofuente.eval(), c.par.Colorbypass.eval()))
