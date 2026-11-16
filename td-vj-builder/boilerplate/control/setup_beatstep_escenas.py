# =============================================================
# setup_beatstep_escenas.py  —  canal 9 del Beatstep Pro = Escena activa de escena_modular
#
# Igual que el canal 10 / 11 eligen visuales y FX, el canal 9 elige escena (layout):
#   pads de arriba  (notas 45-52)  -> escenas 1-8  del menu Escena activa
#   pads de abajo   (notas 37-44)  -> escenas 9-16
# En el orden del menu (multiview primero, luego single cam): reordenar con registrar_layouts.py
# reacomoda los pads solos. Un pad sin escena (menu con menos opciones) no hace nada.
# El Stream Deck se entera solo (feedback de Escena activa) y la pagina MIX enfoca el layout.
#
# En el Beatstep: un proyecto / pattern con los pads en el canal 9 (MIDI Control Center).
# Uso (Textport):
#   exec(open(project.folder + '/control/setup_beatstep_escenas.py', encoding='utf-8').read())
# Se puede volver a correr: recrea solo sus propios operadores.
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'
MIDI_IN    = '/project2/midi_midiin3'          # Beatstep Pro
CHANNEL    = 9
PADS = (['ch%dn%d' % (CHANNEL, n) for n in range(45, 53)]       # arriba: escenas 1-8
        + ['ch%dn%d' % (CHANNEL, n) for n in range(37, 45)])    # abajo:  escenas 9-16

EXEC = '''# generado por control/setup_beatstep_escenas.py — pad del canal 9 -> Escena activa
PADS = %r

def onOffToOn(channel, sampleIndex, val, prev):
\tif channel.name not in PADS:
\t\treturn
\tp = parent().par.Modoescena
\ti = PADS.index(channel.name)
\tif i < len(p.menuNames):
\t\tp.menuIndex = i
\treturn
''' % (PADS,)

# sin esto el Select CHOP no cocina al abrir el .toe y el CHOP Execute nunca dispara
COOK = '''def onFrameStart(frame):
\top('bs_escenas_in').cook()
\treturn
'''


def _replace(parent, optype, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    o = parent.create(optype, name)
    o.nodeX, o.nodeY = x, y
    return o


def run():
    scene = op(SCENE_PATH)
    midi = op(MIDI_IN)
    if scene is None or midi is None:
        print('[error] no encuentro', SCENE_PATH, 'o', MIDI_IN)
        return
    x, y = -1200, -1500
    sel = _replace(scene, selectCHOP, 'bs_escenas_in', x, y)
    sel.par.chop = midi.path
    sel.par.channames = ' '.join(PADS)
    ex = _replace(scene, chopexecuteDAT, 'bs_escenas_exec', x + 200, y)
    ex.text = EXEC
    ex.par.chop = sel.path
    for t in ('ontooff', 'whileon', 'whileoff', 'valuechange'):
        if hasattr(ex.par, t):
            setattr(ex.par, t, False)
    ex.par.offtoon = True
    ck = _replace(scene, executeDAT, 'bs_escenas_cook', x + 400, y)
    ck.text = COOK
    for t in ('start', 'create', 'exit', 'frameend', 'playstatechange', 'devicechange',
              'projectpresave', 'projectpostsave'):
        if hasattr(ck.par, t):
            setattr(ck.par, t, False)
    ck.par.framestart = True

    llegan = [c.name for c in midi.chans() if c.name in PADS]
    names = list(scene.par.Modoescena.menuLabels) if hasattr(scene.par, 'Modoescena') else []
    print('[ok] canal %d del Beatstep -> Escena activa' % CHANNEL)
    for i, pad in enumerate(PADS):
        fila = 'arriba' if i < 8 else 'abajo '
        print('   pad %s %d  %-9s -> %s' % (fila, i % 8 + 1, pad, names[i] if i < len(names) else '(sin escena)'))
    if not llegan:
        print('[aviso] todavia no llega nada del canal %d a %s: configura los pads del Beatstep en ese canal '
              'y toca uno (el canal aparece en cuanto llega la primera nota)' % (CHANNEL, MIDI_IN))


run()
