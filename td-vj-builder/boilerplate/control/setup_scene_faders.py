# =============================================================
# setup_scene_faders.py
# Los faders 4-8 + MASTER del MIDImix controlan los parametros de la
# escena activa (Modoescena). Al cambiar de escena se reasignan solos.
#
# - Parametros: los Float de cada layout_xxx ligados a escena_modular
#   (sin colores, sin camcount/camfit, sin Escena activa), en orden.
# - Takeover: un fader no toma control hasta pasar por el valor actual,
#   asi nada salta al cambiar de escena.
# - scene_faders_map (Table DAT) muestra que mueve cada fader.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/setup_scene_faders.py').read())
# Se puede volver a correr: recrea solo sus propios operadores.
# =============================================================

SCENE_PATH = '/project2/base17/escena_modular'
MIDI_IN    = '/project1/midiin1'
FADERS     = ['ch1ctrl32', 'ch1ctrl50', 'ch1ctrl54', 'ch1ctrl58', 'ch1ctrl62', 'ch1ctrl63']
LABELS     = ['F4', 'F5', 'F6', 'F7', 'F8', 'MASTER']

LIB = r'''
import re

SCENE   = op(%(scene)r)
FADERS  = %(faders)r
LABELS  = %(labels)r
ALIASES = {'layout_fullscreen': 'layout_Fullscren'}
TAKEOVER_WINDOW = 0.03

state = {'scene': None, 'armed': set(), 'prev': {}}


def layout_for(name):
    name = ALIASES.get(name, name)
    lay = SCENE.op(name)
    if lay is None:
        low = name.lower()
        lay = next((c for c in SCENE.children if c.name.lower() == low), None)
    return lay


def scene_pars(name=None):
    """Parametros master (en escena_modular) que mueve cada fader."""
    lay = layout_for(name or SCENE.par.Modoescena.eval())
    if lay is None:
        return []
    out = []
    for p in lay.customPars:
        # algunos layouts ligan por expresion y otros por bind
        if p.mode == ParMode.EXPRESSION:
            expr = p.expr or ''
        elif p.mode == ParMode.BIND:
            expr = p.bindExpr or ''
        else:
            continue
        if not p.isFloat or p.style in ('RGB', 'RGBA'):
            continue
        if 'escena_modular' not in expr:
            continue
        names = re.findall(r'par\.(\w+)', expr)
        mp = getattr(SCENE.par, names[-1], None) if names else None
        if mp is not None:
            out.append(mp)
    return out[:len(FADERS)]


def refresh(*args):
    state['scene'] = SCENE.par.Modoescena.eval()
    state['armed'] = set()
    state['prev'] = {}
    t = op('scene_faders_map')
    if t is None:
        return
    pars = scene_pars()
    t.clear()
    t.appendRow(['fader', 'parametro', 'valor'])
    for i, lbl in enumerate(LABELS):
        p = pars[i] if i < len(pars) else None
        t.appendRow([lbl, p.label if p else '-', round(p.eval(), 3) if p else ''])


def on_fader(chname, val):
    if chname not in FADERS:
        return
    if state['scene'] != SCENE.par.Modoescena.eval():
        refresh()
    i = FADERS.index(chname)
    pars = scene_pars()
    if i >= len(pars):
        return
    p = pars[i]
    lo, hi = p.normMin, p.normMax
    if hi == lo:
        return
    v = min(max(val / 127.0, 0.0), 1.0)
    cur = (p.eval() - lo) / (hi - lo)

    # takeover: espera a que el fader cruce el valor actual
    if i not in state['armed']:
        prev = state['prev'].get(i)
        if abs(v - cur) < TAKEOVER_WINDOW or (prev is not None and (prev - cur) * (v - cur) <= 0):
            state['armed'].add(i)
        state['prev'][i] = v
        if i not in state['armed']:
            return

    p.val = lo + v * (hi - lo)
''' % {'scene': SCENE_PATH, 'faders': FADERS, 'labels': LABELS}

EXEC = '''def onValueChange(channel, sampleIndex, val, prev):
\top('scene_faders_lib').module.on_fader(channel.name, val)
\treturn
'''

PAREXEC = '''def onValueChange(par, prev):
\top('scene_faders_lib').module.refresh()
\treturn
'''


def _replace(parent, optype, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    o = parent.create(optype, name)
    o.nodeX, o.nodeY = x, y
    return o


def _check_conflicts():
    """Avisa si algo mas usa los CC de estos faders (expresiones o exports)."""
    hits = []
    for o in root.findChildren():
        if o.path.startswith(SCENE_PATH + '/scene_faders'):
            continue
        for p in o.pars():
            e = (p.expr or '') if p.mode == ParMode.EXPRESSION else ''
            if any(f in e for f in FADERS):
                hits.append(f'{o.path}.{p.name} = {e}')
        if o.family == 'CHOP' and getattr(o, 'export', False):
            used = [c.name for c in o.chans() if c.name in FADERS]
            if used:
                hits.append(f'{o.path} exporta {used}')
    return hits


def run():
    scene = op(SCENE_PATH)
    if scene is None or op(MIDI_IN) is None:
        print('[error] no encuentro', SCENE_PATH, 'o', MIDI_IN)
        return

    hits = _check_conflicts()
    if hits:
        print('[aviso] estos CC ya los usa algo mas:')
        for h in hits:
            print('   ', h)

    x, y = -1200, -900
    lib = _replace(scene, textDAT, 'scene_faders_lib', x, y)
    lib.text = LIB

    tbl = _replace(scene, tableDAT, 'scene_faders_map', x, y - 150)

    sel = _replace(scene, selectCHOP, 'scene_faders_in', x + 200, y)
    sel.par.chop = MIDI_IN
    sel.par.channames = ' '.join(FADERS)

    ex = _replace(scene, chopexecuteDAT, 'scene_faders_exec', x + 400, y)
    ex.text = EXEC
    ex.par.chop = sel.path
    for t in ('offtoon', 'whileon', 'ontooff', 'whileoff'):
        if hasattr(ex.par, t):
            setattr(ex.par, t, False)
    ex.par.valuechange = True

    pe = _replace(scene, parameterexecuteDAT, 'scene_faders_parexec', x + 400, y - 150)
    pe.text = PAREXEC
    pe.par.op = scene.path
    pe.par.pars = 'Modoescena'
    if hasattr(pe.par, 'onpulse'):
        pe.par.onpulse = False
    pe.par.valuechange = True

    mod = lib.module
    mod.refresh()

    print('[ok] faders listos. Lo que mueve cada fader por escena:')
    for name, label in zip(scene.par.Modoescena.menuNames, scene.par.Modoescena.menuLabels):
        pars = mod.scene_pars(name)
        desc = ', '.join(f'{LABELS[i]}={p.label}' for i, p in enumerate(pars)) or '(sin parametros)'
        print(f'   {label:18s} {desc}')


run()
