# =============================================================
# midi_inventario.py  —  SOLO LECTURA (salvo el modo LEARN)
# Busca en todo el proyecto quien lee cada CC del MIDImix (canales chNctrlNN)
# y escribe control/knobs_mapa.md, agrupado por fila del MIDImix.
#
# Revisa expresiones, binds, parametros de texto (Select/Rename CHOP)
# y el texto de los DATs.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/midi_inventario.py', encoding='utf-8').read())
#       -> escribe knobs_mapa.md
#   LEARN = True;  exec(open(r'...\midi_inventario.py', encoding='utf-8').read())
#       -> crea /project1/knob_learn: gira un knob y el Textport imprime su canal
#   LEARN = 'off'; exec(open(r'...\midi_inventario.py', encoding='utf-8').read())
#       -> borra knob_learn
#   BOTONES = True; exec(...)  -> lo mismo pero para los botones (notas) -> botones_mapa.md
# =============================================================

import re

REPORT  = project.folder + '/control/knobs_mapa.md'
SKIP    = ('local', 'sys', 'ui', 'perform')
CC_RE   = re.compile(r'ch(\d+)ctrl(\d+)(?!\d)')
WILD_RE = re.compile(r'ch\d+ctrl[\[\*\?]')

# MIDImix (canal 1). Inferido del patron "3 knobs y luego el fader"
# (fader 4 = CC32). Confirmar con LEARN.
ROWS = {
    'fila 1': [17, 21, 25, 29, 47, 51, 55, 59],
    'fila 2': [18, 22, 26, 30, 48, 52, 56, 60],
    'fila 3': [19, 23, 27, 31, 49, 53, 57, 61],
    'faders': [20, 24, 28, 32, 50, 54, 58, 62, 63],
}

try:
    LEARN
except NameError:
    LEARN = False
try:
    BOTONES
except NameError:
    BOTONES = False
if BOTONES:   # botones del MIDImix (notas chNnNN) en vez de knobs -> botones_mapa.md
    CC_RE   = re.compile(r'ch(\d+)n(\d+)(?!\d)')
    WILD_RE = re.compile(r'ch\d+n[\[\*\?]')
    REPORT  = REPORT.replace('knobs_mapa.md', 'botones_mapa.md')
    ROWS    = {}

LEARN_LOG = REPORT.replace('knobs_mapa.md', 'learn_log').replace('botones_mapa.md', 'learn_log') + '.md'
LEARN_CB = '''
# Cada control nuevo que se mueve se anota una vez, en orden, en control/learn_log.md
LOG = %r

def onValueChange(channel, sampleIndex, val, prev):
    seen = me.fetch('seen', [], storeDefault=True)
    if channel.name in seen:
        return
    seen.append(channel.name)
    me.store('seen', seen)
    line = '| %%d | %%s | %%s |' %% (len(seen), channel.name, channel.owner.path)
    print('[knob_learn] #%%d %%s   (%%s)' %% (len(seen), channel.name, channel.owner.path))
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + chr(10))
''' % LEARN_LOG


def _ops():
    for top in op('/').children:
        if top.name in SKIP:
            continue
        yield top
        if top.isCOMP:
            for o in top.findChildren(depth=None):
                yield o


def scan():
    """[(cc_chan, cc, op, donde, texto)] y lista de patrones con comodin."""
    hits, wild = [], []
    for o in _ops():
        if o.name == 'knob_learn':
            continue
        for p in o.pars():
            if p.mode == ParMode.EXPRESSION:
                src, kind = p.expr or '', 'expr'
            elif p.mode == ParMode.BIND:
                src, kind = p.bindExpr or '', 'bind'
            elif p.isString:
                src, kind = p.val or '', 'valor'
            else:
                continue
            if WILD_RE.search(src):
                wild.append((o.path, p.name, src))
            for ch, cc in CC_RE.findall(src):
                hits.append((int(ch), int(cc), o, '%s (%s)' % (p.name, kind), src))
        if o.isDAT and o.name not in ('scene_faders_lib',):
            try:
                text = o.text
            except Exception:
                continue
            for line in text.splitlines():
                if WILD_RE.search(line):
                    wild.append((o.path, 'texto', line.strip()))
                for ch, cc in CC_RE.findall(line):
                    hits.append((int(ch), int(cc), o, 'texto DAT', line.strip()))
    return hits, wild


def where(cc):
    for row, ccs in ROWS.items():
        if cc in ccs:
            return '%s, col %d' % (row, ccs.index(cc) + 1)
    return '?'


def report():
    hits, wild = scan()
    midis = [o for o in _ops() if o.OPType in ('midiinCHOP', 'midiinmapCHOP')]
    L = ['# Mapa de knobs del MIDImix', '',
         '## MIDI In en el proyecto', '']
    L += ['- `%s` (%s)' % (m.path, m.OPType) for m in midis] or ['- ninguno']
    L += ['', '## Quien lee cada CC', '',
          '| CC | Posicion | Operador | Donde | Texto |', '|---|---|---|---|---|']
    for ch, cc, o, w, src in sorted(hits, key=lambda h: (h[0], h[1], h[2].path)):
        L.append('| ch%d cc%d | %s | `%s` | %s | `%s` |' % (ch, cc, where(cc), o.path, w,
                                                         src.replace('|', '\\|')[:90]))
    if wild:
        L += ['', '## Con comodin (revisar a mano)', '']
        L += ['- `%s` %s: `%s`' % w for w in wild]
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))
    print('[ok] %d referencias a CC, %d con comodin -> %s' % (len(hits), len(wild), REPORT))
    for row, ccs in ROWS.items():
        used = sorted({h[1] for h in hits if h[1] in ccs})
        print('   %-7s usados: %s' % (row, used or '-'))


def learn(on):
    host = op('/project1')
    old = host.op('knob_learn')
    if old is not None:
        old.destroy()
    if not on:
        print('[ok] knob_learn borrado')
        return
    midis = [o for o in _ops() if o.OPType == 'midiinCHOP']
    d = host.create(chopexecuteDAT, 'knob_learn')
    d.text = LEARN_CB
    d.par.chop = ' '.join(m.path for m in midis)
    d.par.valuechange = True
    d.par.offtoon = d.par.ontooff = d.par.whileon = d.par.whileoff = False
    d.nodeX, d.nodeY = -400, -600
    with open(LEARN_LOG, 'w', encoding='utf-8') as f:
        f.write('# Learn: controles en el orden en que se movieron\n\n| # | Canal | MIDI In |\n|---|---|---|\n')
    print('[ok] knob_learn escuchando %s.' % ', '.join(m.name for m in midis))
    print('     Mueve/presiona cada control UNA vez, en orden. Se anota en %s' % LEARN_LOG)
    print('     Para quitarlo: LEARN = "off"; exec(...)')


if LEARN == 'off':
    learn(False)
elif LEARN:
    learn(True)
else:
    report()
LEARN = False
BOTONES = False
