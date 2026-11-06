# =============================================================
# fase3_fila2.py  —  fila 2 del MIDImix (knobs 1-5) = FX de camara activo
#
# - FX activo = el baseNN que llega (directo o por null/select) a la entrada `index` de /project2/switch23.
# - Cada FX dice que mueven sus 5 knobs:
#     * si el base tiene un Table DAT `knobs` (un nombre de parametro por fila) -> esos
#     * si no, los 5 del contrato: Mezcla, Tiempo, Distorsion, Color, Firma
#   Asi un FX nuevo con otros parametros solo necesita su tabla `knobs`.
# - El knob va 0..1 sobre el rango del parametro (menus y toggles por pasos).
# - Takeover proporcional: al cambiar de FX el knob responde desde el primer movimiento sin
#   brincar; el parametro avanza hacia el lado que gira y se emparejan al llegar al extremo
#   (o antes, si se cruzan). Despues el knob manda directo.
# - Suavizado: lag corto en los knobs (LAG segundos).
# - /project2/fx_knobs_map (Table DAT) muestra que mueve cada knob ahora.
#
# Tambien prepara base25 (Prism): parametro Rotspeed (velocidad de giro, sin saltos).
# Prism ya usa el contrato (fase2_contrato.py), asi que se le quita la tabla `knobs` vieja.
#
# El mismo script arma la fila 1 (visual activo) con LINE = 'vis' (ver fase3_fila1.py):
# mismo contrato, mismo takeover, nodos vis_knobs_*.
#
# Se puede volver a correr: recrea solo sus propios operadores.
# Uso (Textport):
#   exec(open(project.folder + '/control/fase3_fila2.py', encoding='utf-8').read())
# =============================================================

LINES = {
    # fila 2 = FX de camara activo (switch23)
    'fx':  {'switch': '/project2/switch23', 'prefix': 'fx_knobs', 'fila': 'fila 2', 'que': 'FX',
            'knobs': ['ch1ctrl18', 'ch1ctrl22', 'ch1ctrl26', 'ch1ctrl30', 'ch1ctrl48'],
            'watch': 'switch23'},
    # fila 1 = visual activo (switch2 -> switch6..21 -> base1-16)
    'vis': {'switch': '/project2/switch2', 'prefix': 'vis_knobs', 'fila': 'fila 1', 'que': 'visual',
            'knobs': ['ch1ctrl17', 'ch1ctrl21', 'ch1ctrl25', 'ch1ctrl29', 'ch1ctrl47'],
            'watch': 'switch2'},
}
try:
    LINE
except NameError:
    LINE = 'fx'
CFG      = LINES[LINE]
P        = CFG['prefix']

ROOT     = '/project2'
SWITCH   = CFG['switch']
MIDI_IN  = '/project2/midi_midiin1'
KNOBS    = CFG['knobs']
LAG      = 0.08
CONTRACT = ['Mezcla', 'Tiempo', 'Distorsion', 'Color', 'Firma']
PRISM    = '/project2/base25'

LIB = r'''
SWITCH   = op(%(switch)r)
KNOBS    = %(knobs)r
CONTRACT = %(contract)r
MAP      = %(map)r
TAKEOVER_WINDOW = 0.03

state = {'base': None, 'armed': set(), 'prev': {}, 'knob': {}, 'calls': 0, 'last': None}


def resolve(o):
    """Sigue la senal hacia atras hasta el baseNN que la alimenta: en un Switch TOP toma la
    entrada elegida (index recortado al rango, como TD), en un Select TOP su TOP, si no la entrada 0."""
    for _ in range(16):
        if o is None:
            return None
        if o.isCOMP and o.name.startswith('base'):
            return o
        if o.OPType == 'outTOP' and o.parent().name.startswith('base'):
            return o.parent()
        if o.OPType == 'selectTOP':
            o = o.par.top.eval()
            continue
        ins = o.inputs
        if not ins:
            return None
        k = min(max(int(o.par.index.eval()), 0), len(ins) - 1) if o.OPType == 'switchTOP' else 0
        o = ins[k]
    return None


def active_base():
    return resolve(SWITCH)


def knob_pars(base=None):
    """Los 5 parametros que mueve la fila 2 en este base (None donde no hay)."""
    base = base or active_base()
    if base is None:
        return [None] * len(KNOBS)
    t = base.op('knobs')
    names = [t[r, 0].val for r in range(t.numRows)] if t is not None and t.isDAT else CONTRACT
    if (t is None or not t.isDAT) and not all(getattr(base.par, n, None) is not None for n in CONTRACT):
        # bases de tdvj_core (Intensity, Speed...): los 5 primeros sliders de su pagina, en orden de rol
        pg = next((g for g in base.customPages if g.name in ('Visual', 'Filter', 'Layout')), None)
        if pg is not None:
            names = [p.name for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')]
    out = []
    for i in range(len(KNOBS)):
        p = getattr(base.par, names[i], None) if i < len(names) and names[i] else None
        out.append(p)
    return out


def _range(p):
    lo, hi = p.normMin, p.normMax
    if lo == hi:
        lo, hi = p.min, p.max
    return float(lo), float(hi)


def get_norm(p):
    if p.isMenu:
        names = list(p.menuNames)
        n = max(len(names), 1)
        return (names.index(p.eval()) + 0.5) / n if p.eval() in names else 0.0
    if p.isToggle:
        return 1.0 if p.eval() else 0.0
    lo, hi = _range(p)
    return 0.0 if hi == lo else (float(p.eval()) - lo) / (hi - lo)


def set_norm(p, v):
    if p.isMenu:
        names = list(p.menuNames)
        if names:
            p.val = names[min(len(names) - 1, int(v * len(names)))]
    elif p.isToggle:
        p.val = v >= 0.5
    else:
        lo, hi = _range(p)
        x = lo + v * (hi - lo)
        p.val = int(round(x)) if p.isInt else x


def real(base, p):
    """Valor real que mueve el slot (lectura <Slot>val de fase2_contrato), entero si es entero."""
    r = getattr(base.par, p.name + 'val', None) if base is not None and p is not None else None
    if r is None:
        return ''
    v = r.eval()
    return ('%%g' %% round(v, 3)) if isinstance(v, float) else str(v)


def refresh(*args):
    base = active_base()
    state['base'] = base.path if base is not None else None
    state['armed'] = set()
    state['prev'] = {}
    t = op(MAP)
    if t is None:
        return
    t.clear()
    t.appendRow(['knob', 'fx', 'parametro', 'valor', 'real'])
    for i, p in enumerate(knob_pars(base)):
        t.appendRow(['K%%d' %% (i + 1), base.name if base is not None else '-',
                     p.label if p is not None else '-',
                     '%%d%%%%' %% round(get_norm(p) * 100) if p is not None else '',
                     real(base, p)])


def on_knob(chname, val):
    state['calls'] += 1                 # diag_fila2.py los muestra
    state['last'] = (chname, val)
    if chname not in KNOBS:
        return
    i = KNOBS.index(chname)
    v = min(max(val / 127.0, 0.0), 1.0)
    last = state['knob'].get(i)          # posicion fisica anterior (no se borra al cambiar de FX)
    state['knob'][i] = v
    base = active_base()
    if (base.path if base is not None else None) != state['base']:
        refresh()
    p = knob_pars(base)[i]
    if p is None:
        return

    # takeover proporcional: avanza hacia el lado que gira, sin brincar
    if i not in state['armed']:
        cur = get_norm(p)
        if abs(v - cur) < TAKEOVER_WINDOW:
            state['armed'].add(i)
        elif last is None or last == v:
            return
        else:
            if v > last:
                new = cur + (v - last) * (1.0 - cur) / (1.0 - last) if last < 1.0 else cur
            else:
                new = cur - (last - v) * cur / last if last > 0.0 else cur
            if abs(v - new) < TAKEOVER_WINDOW or (cur - v) * (new - v) <= 0:
                state['armed'].add(i)
                new = v
            state['prev'][i] = new
            v = min(max(new, 0.0), 1.0)

    set_norm(p, v)
    t = op(MAP)
    if t is not None and t.numRows > i + 1:
        t[i + 1, 3] = '%%d%%%%' %% round(v * 100)
        t[i + 1, 4] = real(base, p)
''' % {'switch': SWITCH, 'knobs': KNOBS, 'contract': CONTRACT, 'map': P + '_map'}

EXEC = '''def onValueChange(channel, sampleIndex, val, prev):
\top(%r).module.on_knob(channel.name, val)
\treturn
''' % (P + '_lib')

# Nada mas "jala" <P>_lag: sin esto, al abrir el .toe no cocina y el CHOP Execute nunca dispara.
COOK = '''def onFrameStart(frame):
\top(%r).cook()
\treturn
''' % (P + '_lag')

PAREXEC = '''def onValueChange(par, prev):
\top(%r).module.refresh()
\treturn
''' % (P + '_lib')


def _replace(parent, optype, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    o = parent.create(optype, name)
    o.nodeX, o.nodeY = x, y
    return o


def _prism():
    """base25: Rotspeed (giro que acelera/frena sin brincar). Sin tabla knobs: manda el contrato."""
    base = op(PRISM)
    pr = base.op('prism') if base else None
    if pr is None:
        print('[aviso] no encuentro %s/prism: se salta' % PRISM)
        return
    page = next((pg for pg in base.customPages if pg.name == 'Custom'), None) or base.appendCustomPage('Custom')
    p = getattr(base.par, 'Rotspeed', None)
    if p is None:
        p = page.appendFloat('Rotspeed', label='Rot Speed')[0]
        p.val = 0.25                    # 0.25 * 0.4 = 0.1, la velocidad que tenia
    p.min, p.max, p.normMin, p.normMax = 0.0, 1.0, 0.0, 1.0
    p.clampMin = p.clampMax = True
    p.default = 0.25
    k =_replace(base, constantCHOP, 'rot_speed', -200, -250)
    k.par.name0 = 'speed'
    k.par.value0.expr = 'parent().par.Rotspeed * 0.4'
    s = _replace(base, speedCHOP, 'rot_phase', 0, -250)
    s.inputConnectors[0].connect(k)
    pr.par.Rotsinphase.expr = "op('%s/rot_phase')[0]" % PRISM
    old = base.op('knobs')
    if old is not None:
        old.destroy()                   # la tabla ganaria sobre el contrato
    print('[ok] base25: Rotspeed listo; los knobs siguen el contrato')


def run():
    root, sw = op(ROOT), op(SWITCH)
    if sw is None or op(MIDI_IN) is None:
        print('[error] no encuentro', SWITCH, 'o', MIDI_IN)
        return
    if LINE == 'fx':
        _prism()

    x, y = sw.nodeX, sw.nodeY - 400
    lib = _replace(root, textDAT, P + '_lib', x, y)
    lib.text = LIB
    _replace(root, tableDAT, P + '_map', x, y - 150)

    sel = _replace(root, selectCHOP, P + '_in', x + 200, y)
    sel.par.chop = MIDI_IN
    sel.par.channames = ' '.join(KNOBS)
    lag = _replace(root, lagCHOP, P + '_lag', x + 350, y)
    lag.inputConnectors[0].connect(sel)
    lag.par.lag1 = lag.par.lag2 = LAG

    ex = _replace(root, chopexecuteDAT, P + '_exec', x + 500, y)
    ex.text = EXEC
    ex.par.chop = lag.path
    for t in ('offtoon', 'whileon', 'ontooff', 'whileoff'):
        if hasattr(ex.par, t):
            setattr(ex.par, t, False)
    ex.par.valuechange = True

    ck = _replace(root, executeDAT, P + '_cook', x + 650, y)
    ck.text = COOK
    for t in ('start', 'create', 'exit', 'frameend', 'playstatechange', 'devicechange',
              'projectpresave', 'projectpostsave'):
        if hasattr(ck.par, t):
            setattr(ck.par, t, False)
    ck.par.framestart = True

    pe = _replace(root, parameterexecuteDAT, P + '_parexec', x + 500, y - 150)
    pe.text = PAREXEC
    pe.par.op = CFG['watch']
    pe.par.pars = 'index'
    if hasattr(pe.par, 'onpulse'):
        pe.par.onpulse = False
    pe.par.valuechange = True

    mod = lib.module
    mod.refresh()
    act = mod.active_base()
    print('[ok] %s sigue al %s activo (ahora: %s). Lo que mueve en cada %s:'
          % (CFG['fila'], CFG['que'], act.name if act is not None else 'ninguno', CFG['que']))
    if LINE == 'fx':
        srcs = [(i, ic.connections[0].owner) for i, ic in enumerate(sw.inputConnectors) if ic.connections]
    else:
        srcs = [(n, op('%s/base%d' % (ROOT, n))) for n in range(1, 17)]
    for i, o in srcs:
        b = mod.resolve(o)
        if b is None:
            print('   %2d %-8s (no llega de ningun baseNN)' % (i, o.name if o is not None else '-'))
            continue
        pars = mod.knob_pars(b)
        desc = ', '.join('K%d=%s' % (k + 1, p.label) for k, p in enumerate(pars) if p is not None) or '(nada)'
        print('   %2d %-8s %s' % (i, b.name, desc))


try:
    run()
finally:   # la siguiente corrida vuelve a la fila 2 si no se pide otra cosa
    LINE = 'fx'
