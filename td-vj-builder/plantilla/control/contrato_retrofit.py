# =============================================================
# BOILERPLATE: CONTRACT de abajo es el de Little Jesus (ejemplo). En cada show se reescribe
#   con el inventario_bases.md del proyecto. Pone el contrato a FX hechos a mano sin rehacerlos.
# contrato_retrofit.py  —  contrato de 5 en los FX de cámara (base18-24; base25 = Prism sin contrato)
#   Ver control/contrato_propuesta.md.
#
# En cada base:
#   - Pagina "Contrato": Mezcla, Tiempo, Distorsion, Color, Firma (0..1) + Bypass.
#     Mismos nombres en todas las bases -> la fila 2 del MIDImix y el Stream Deck
#     leen siempre par.Mezcla ... par.Firma.
#   - Cada slot mueve por expresion el parametro real del efecto (escalado a su rango).
#     Arranca en el valor actual, asi que al aplicar nada cambia de look.
#   - Piezas universales al final de la cadena (nodos con tag tdvj):
#       Estela -> Tono -> Mezcla (vs. entrada limpia) -> Bypass -> out1
#   - Pagina "Audio": Audioreact, Low/Mid/High, Audiotarget (a que slot suma), Audiomult,
#     Smooth, Audiochop, Energy.
#
# Se puede volver a correr: rearma solo lo suyo.
# Antes de aplicar guarda los valores/expresiones originales en control/fase2_backup.json.
#
# Uso (Textport):
#   exec(open(project.folder + '/control/contrato_retrofit.py', encoding='utf-8').read())
#       -> solo revisa e imprime (incluye lo que hay adentro de base22 y base23)
#   BASES = [18]; APPLY = True; exec(open(r'...\contrato_retrofit.py', encoding='utf-8').read())
#       -> aplica solo a base18 (para probar)
#   APPLY = True; exec(open(r'...\contrato_retrofit.py', encoding='utf-8').read())
#       -> aplica a todas
#   RESTORE = True; exec(open(r'...\contrato_retrofit.py', encoding='utf-8').read())
#       -> deshace con el respaldo (acepta BASES = [...] tambien)
# =============================================================

import colorsys, json, os

ROOT    = '/project2'
BACKUP  = project.folder + '/control/fase2_backup.json'
TAG     = 'tdvj'
AUDIO   = None   # None = busca en /project1 un CHOP con canales low/mid/high
SLOTS   = ('Mezcla', 'Tiempo', 'Distorsion', 'Color', 'Firma')
INSPECT = ()      # bases a listar por dentro en la revision, p. ej. (22, 23)

# Spec por slot:
#   ('par', rel, nombre)        lineal al rango del parametro
#   ('par', rel, nombre, mn, mx) lineal a un rango propio
#   ('steps', rel, nombre)      menu / toggle / int por zonas del knob
#   ('hue', rel, nombre)        gira el tono de un parametro RGB(A)
#   ('expr', [(rel, nombre, plantilla)], inicial)  macro; {Slot} = valor del slot
#   'mezcla' | 'tono' | 'estela'  pieza universal
#   'todo'                       pendiente (el slot existe pero no mueve nada)
KALEI = 'GLSL_Kaleidoscope1'
CONTRACT = {
    18: ['mezcla', ('par', '.', 'Cachesize'), ('par', '.', 'Threshold'), 'tono', ('par', '.', 'Threshold2')],
    19: [('par', 'pixelateUV_random/pixelate', 'Drywet'), ('par', '.', 'Int'), ('par', '.', 'Blackoffset'),
         'tono', ('steps', '.', 'Menu')],
    20: [('par', '.', 'Opacity'),
         ('expr', [('rgbaDelay', 'Reddelay', "-int(round({Tiempo} * 30))"),
                   ('rgbaDelay', 'Bluedelay', "-int(round({Tiempo} * 15))")], 0.05),
         ('par', '.', 'Size'), 'tono', ('par', '.', 'Preshrink')],
    21: ['mezcla', ('par', '.', 'Float'), ('par', '.', 'Displaceweight1'), 'tono', ('par', '.', 'Displaceweight2')],
    22: ['mezcla', ('par', '.', 'Feedbackscale2'), ('par', '.', 'Feedbackscale'), 'tono',
         ('par', 'liquid_feedback/displace1', 'displaceweighty', 0.0, 0.04)],
    23: ['mezcla', ('par', 'pixel_sort', 'Feedbackopacity'),
         ('par', 'pixel_sort/displace1', 'displaceweighty', 0.0, 0.05), 'tono',
         ('par', 'pixel_sort/thresh1', 'threshold', 0.0, 1.0)],
    24: [('par', '.', 'Mastercontrast'), 'estela', ('par', '.', 'Mastercellsize'), ('hue', '.', 'Mastercolor'),
         ('steps', '.', 'Asciiactivefilter2')],
}
# base25 = Prism (sin contrato, ver fase2c_prism.py); base26-32 libres para FX nuevos

try:
    APPLY
except NameError:
    APPLY = False
try:
    RESTORE
except NameError:
    RESTORE = False
try:
    BASES
except NameError:
    BASES = None


# ─────────────────────────────────────────────────────────────── utilidades
def _bases():
    return [n for n in CONTRACT if BASES is None or n in BASES]


def _target(comp, rel):
    return comp if rel == '.' else comp.op(rel)


def _range(p):
    mn, mx = p.normMin, p.normMax
    if mn == mx:
        mn, mx = p.min, p.max
    return float(mn), float(mx)


def _audio_source():
    if AUDIO:
        return op(AUDIO)
    for o in op('/project1').findChildren(type=CHOP, depth=1):
        names = {c.name for c in o.chans()}
        if {'low', 'mid', 'high'} <= names:
            return o
    return None


def _page(comp, name):
    for pg in comp.customPages:
        if pg.name == name:
            return pg
    return comp.appendCustomPage(name)


def _upsert(page, style, name, label):
    p = getattr(page.owner.par, name, None)
    if p is not None and (p.style != style or p.page.name != page.name):
        p.destroy()
        p = None
    created = p is None
    if created:
        getattr(page, 'append' + style)(name, label=label)
        p = getattr(page.owner.par, name)
    p.label = label
    return p, created


def _float(page, name, label, mn, mx, default, val=None):
    p, created = _upsert(page, 'Float', name, label)
    p.min, p.max = mn, mx
    p.normMin, p.normMax = mn, mx
    p.clampMin = p.clampMax = True
    p.default = default
    if created or val is not None:
        p.val = default if val is None else val
    return p


def _toggle(page, name, label, default):
    p, created = _upsert(page, 'Toggle', name, label)
    p.default = default
    if created:
        p.val = default
    return p


# ─────────────────────────────────────────────────────────────── plan por slot
def _slot_eff(B, slot):
    """Valor efectivo del slot: knob + audio si Audiotarget apunta a este slot."""
    return ("min(1.0, max(0.0, {B}.par.{s}.eval() + ({B}.par.Energy.eval() "
            "if {B}.par.Audiotarget.eval() == '{s}' else 0.0)))").format(B=B, s=slot)


def plan_slot(comp, slot, spec):
    """-> (label, inicial, [(op, parname, expr)], problema)"""
    B = "op('%s')" % comp.path
    v = _slot_eff(B, slot)
    if spec in ('mezcla', 'tono', 'estela'):
        return ({'mezcla': 'Mezcla ✱', 'tono': 'Tono ✱', 'estela': 'Estela ✱'}[spec],
                {'mezcla': 1.0, 'tono': 0.0, 'estela': 0.0}[spec], [], None)
    if spec == 'todo':
        return ('— pendiente', 0.0, [], None)
    kind = spec[0]
    if kind == 'expr':
        targets = []
        for rel, name, tpl in spec[1]:
            o = _target(comp, rel)
            if o is None or getattr(o.par, name, None) is None:
                return (None, 0, [], 'no existe %s/%s.%s' % (comp.path, rel, name))
            subs = {s: _slot_eff(B, s) for s in SLOTS}
            targets.append((o, name, tpl.format(**subs)))
        label = '+'.join(sorted({t[1] for t in targets})) or 'macro'
        return (label, spec[2], targets, None)

    rel, name = spec[1], spec[2]
    o = _target(comp, rel)
    if o is None:
        return (None, 0, [], 'no existe %s/%s' % (comp.path, rel))

    if kind == 'hue':
        comps = [getattr(o.par, name + c, None) for c in 'rgb']
        if None in comps:
            return (None, 0, [], 'no existe el color %s.%s' % (o.path, name))
        h, s, val = colorsys.rgb_to_hsv(*[c.eval() for c in comps])
        targets = [(o, name + c, "__import__('colorsys').hsv_to_rgb(%s, %r, %r)[%d]" % (v, s, val, i))
                   for i, c in enumerate('rgb')]
        return (name + ' (tono)', h, targets, None)

    p = getattr(o.par, name, None)
    if p is None:
        return (None, 0, [], 'no existe %s.%s' % (o.path, name))

    if kind == 'steps':
        if p.isMenu:
            names = list(p.menuNames)
            n = len(names)
            idx = names.index(p.eval()) if p.eval() in names else 0
            expr = "%r[min(%d, int(%s * %d))]" % (names, n - 1, v, n)
            return (name + ' (pasos)', (idx + 0.5) / n, [(o, name, expr)], None)
        if p.isToggle:
            return (name + ' (on/off)', 0.75 if p.eval() else 0.25, [(o, name, '%s >= 0.5' % v)], None)
        mn, mx = int(p.min), int(p.max)
        n = mx - mn + 1
        expr = 'min(%d, %d + int(%s * %d))' % (mx, mn, v, n)
        return (name + ' (pasos)', (int(p.eval()) - mn + 0.5) / n, [(o, name, expr)], None)

    mn, mx = (float(spec[3]), float(spec[4])) if len(spec) == 5 else _range(p)
    cur = float(p.eval())
    init = 0.0 if mx == mn else min(1.0, max(0.0, (cur - mn) / (mx - mn)))
    lin = '%r + (%r) * %s' % (mn, mx - mn, v)
    expr = 'int(round(%s))' % lin if p.isInt else lin
    return (name, init, [(o, name, expr)], None)


# ─────────────────────────────────────────────────────────────── nodos universales
def _io(comp):
    ins = [c for c in comp.children if c.OPType == 'inTOP']
    out = comp.op('out1') or next((c for c in comp.children if c.OPType == 'outTOP'), None)
    return (ins[0] if ins else None), out


def _up(o):
    """Nodos conectados a las entradas de o (sirve igual para TOPs y COMPs)."""
    return [cn.owner for ic in o.inputConnectors for cn in ic.connections]


def _down(o):
    return [cn.owner for oc in o.outputConnectors for cn in oc.connections]


def _clean_source(comp, src):
    """Sube desde la salida del efecto hasta el nodo que trae la camara
    (el primero sin entradas: Select TOP, In TOP, Video Device In...). Solo nodos de esta
    misma base: un in1 de adentro de otro COMP (p. ej. optical_flow/in1) no sirve."""
    seen, queue = set(), [src]
    while queue:
        o = queue.pop(0)
        if o.path in seen or TAG in o.tags or o.parent().path != comp.path:
            continue
        seen.add(o.path)
        ups = _up(o)
        if not ups:
            if (o.OPType in ('inTOP', 'selectTOP', 'videodeviceinTOP', 'ndiinTOP', 'syphonspoutinTOP')
                    and not o.errors()):
                return o
            continue
        queue.extend(ups)
    return None


def _original_src(comp, out):
    """El efecto original: se camina hacia atras desde out1 saltando los nodos tdvj
    (en tdvj_mezcla el efecto es la entrada 1; en los demas, la 0)."""
    o = (_up(out) or [None])[0]
    while o is not None and TAG in o.tags:
        ins = o.inputConnectors
        k = 1 if o.name == 'tdvj_mezcla' else 0
        conns = ins[k].connections if len(ins) > k else []
        o = conns[0].owner if conns else None
    return o


def _connect(dst, src):
    try:
        dst.inputConnectors[0].connect(src)
    except Exception:
        dst.inputConnectors[0].connect(src.outputConnectors[0])


def _clear(comp):
    out = _io(comp)[1]
    srcop = _original_src(comp, out) if out is not None else None
    for c in list(comp.children):
        if c.valid and TAG in c.tags:
            c.destroy()
    comp.unstore('tdvj_src')
    if out is not None and srcop is not None and srcop.valid:
        try:
            _connect(out, srcop)
        except Exception as e:
            print('   [!] no pude reconectar out1 <- %s (%s): %s' % (srcop.path, srcop.OPType, e))
        return srcop
    return None


def _new(comp, optype, name, x, y):
    o = comp.create(optype, name)
    o.tags.add(TAG)
    o.nodeX, o.nodeY = x, y
    return o


def build_chain(comp, specs, src=None):
    inp, out = _io(comp)
    if src is None and out is not None and _up(out):
        src = _up(out)[0]
    if src is None and out is not None:
        # out1 quedo suelto: el efecto original es el TOP que ya no sale a ningun lado
        loose = [c for c in comp.children if (c.isTOP or c.isCOMP) and c is not out and TAG not in c.tags
                 and not _down(c) and c.OPType not in ('inTOP', 'outTOP')]
        if len(loose) == 1:
            src = loose[0]
            print('   out1 estaba suelto: se reconecta desde %s' % src.name)
        elif loose:
            print('   [!] out1 suelto y varios candidatos: %s' % ', '.join(c.name for c in loose))
    if out is None or src is None or src is out:
        print('   [!] sin out1 conectado: no se arma la cadena (solo parametros)')
        return
    if inp is None or inp.parent().path != comp.path or inp.errors():
        inp = _clean_source(comp, src)
        if inp is not None:
            print('   entrada limpia: %s (%s)' % (inp.name, inp.OPType))
    x, y = out.nodeX - 150 * 6, out.nodeY - 250
    B = "op('%s')" % comp.path
    cur = src

    if 'estela' in specs:
        fb = _new(comp, feedbackTOP, 'tdvj_fb', x, y - 120)
        trail = _new(comp, crossTOP, 'tdvj_trail', x + 150, y)
        fb.inputConnectors[0].connect(cur)
        fb.par.top = trail.name
        trail.inputConnectors[0].connect(cur)
        trail.inputConnectors[1].connect(fb)
        trail.par.cross.expr = '%s * 0.96' % _slot_eff(B, 'Tiempo')
        cur = trail
    if 'tono' in specs:
        hsv = _new(comp, hsvadjustTOP, 'tdvj_tono', x + 300, y)
        hsv.inputConnectors[0].connect(cur)
        hsv.par.hueoffset.expr = '%s * 360' % _slot_eff(B, 'Color')
        cur = hsv
    if inp is not None:
        if 'mezcla' in specs:
            mix = _new(comp, crossTOP, 'tdvj_mezcla', x + 450, y)
            mix.inputConnectors[0].connect(inp)
            mix.inputConnectors[1].connect(cur)
            mix.par.cross.expr = _slot_eff(B, 'Mezcla')
            cur = mix
        byp = _new(comp, switchTOP, 'tdvj_bypass', x + 600, y)
        byp.inputConnectors[0].connect(cur)
        byp.inputConnectors[1].connect(inp)
        byp.par.index.expr = 'int(%s.par.Bypass.eval())' % B
        cur = byp
    elif 'mezcla' in specs:
        print('   [!] sin In TOP: no hay Mezcla ni Bypass contra la entrada limpia')
    _connect(out, cur)


def build_audio(comp, src):
    B = "op('%s')" % comp.path
    out = _io(comp)[1]
    x, y = (out.nodeX if out else 0) - 900, (out.nodeY if out else 0) - 500
    sel = _new(comp, selectCHOP, 'tdvj_audio', x, y)
    sel.par.chop.expr = '%s.par.Audiochop.eval()' % B
    sm = _new(comp, lagCHOP, 'audio_smooth', x + 150, y)
    sm.inputConnectors[0].connect(sel)
    sm.par.lag1.expr = sm.par.lag2.expr = '%s.par.Smooth.eval()' % B

    ap = _page(comp, 'Audio')
    _toggle(ap, 'Audioreact', 'Audio React', src is not None)
    _toggle(ap, 'Low', 'Low', True)
    _toggle(ap, 'Mid', 'Mid', False)
    _toggle(ap, 'High', 'High', False)
    p, created = _upsert(ap, 'Menu', 'Audiotarget', 'Audio Target')
    p.menuNames = list(SLOTS)
    p.menuLabels = ['%d %s' % (i + 1, s) for i, s in enumerate(SLOTS)]
    p.default = 'Distorsion'
    if created:
        p.val = 'Distorsion'
    _float(ap, 'Audiomult', 'Audio Mult', 0.0, 3.0, 0.5)
    _float(ap, 'Smooth', 'Smooth (s)', 0.0, 1.0, 0.12)
    p, created = _upsert(ap, 'CHOP', 'Audiochop', 'Audio CHOP')
    if created and src is not None:
        p.val = src.path
    band = ("(me.op('audio_smooth')['{b}'].eval() if me.op('audio_smooth') is not None "
            "and me.op('audio_smooth')['{b}'] is not None else 0.0)")
    e = _float(ap, 'Energy', 'Energy (lectura)', 0.0, 3.0, 0.0)
    e.clampMax = False
    e.expr = ('({l} * me.par.Low + {m} * me.par.Mid + {h} * me.par.High) * me.par.Audiomult * me.par.Audioreact'
              .format(l=band.format(b='low'), m=band.format(b='mid'), h=band.format(b='high')))
    e.readOnly = True


# ─────────────────────────────────────────────────────────────── inspeccion 🔍
def inspect(comp):
    print('   --- adentro de %s (para elegir los slots pendientes)' % comp.name)
    for o in comp.findChildren(depth=None):
        if TAG in o.tags or o.isDAT:
            continue
        rel = o.path.replace(comp.path + '/', '')
        moved = []
        for p in o.pars():
            if p.isCustom or p.page is None or p.page.name in ('Common', 'Extensions', 'Layout', 'Look', 'Panel', 'Children'):
                continue
            if p.mode == ParMode.EXPRESSION and p.isNumber:
                moved.append('%s=%s (expr %s)' % (p.name, round(p.eval(), 3), p.expr))
            elif p.isNumber and p.mode == ParMode.CONSTANT and p.eval() != p.default:
                moved.append('%s=%s' % (p.name, round(p.eval(), 3)))
        print('      %s [%s] %s' % (rel, o.OPType, ', '.join(moved[:8])))
        for p in o.customPars:
            if p.isNumber or p.isMenu or p.isToggle:
                rng = '[%s..%s]' % (p.normMin, p.normMax) if p.isNumber else ''
                print('      %s.%s  "%s"  = %s  %s' % (o.path.replace(comp.path + '/', ''), p.name,
                                                   p.label, p.eval(), rng))
        if o.OPType in ('glslTOP', 'glslmultiTOP'):
            for i in range(32):
                n = getattr(o.par, 'vec%dname' % i, None)
                if n is None:
                    break
                if n.eval():
                    vals = [getattr(o.par, 'vec%dvalue%s' % (i, c)).eval() for c in 'xyzw']
                    ex = getattr(o.par, 'vec%dvaluex' % i)
                    src = (' expr: ' + ex.expr) if ex.mode == ParMode.EXPRESSION else ''
                    print('      %s uniform %s = %s%s' % (o.path.replace(comp.path + '/', ''), n.eval(),
                                                         vals[0], src))


# ─────────────────────────────────────────────────────────────── main
def run():
    print('MODO:', 'APLICAR CAMBIOS' if APPLY else 'SOLO REVISION (no cambia nada)')
    src = _audio_source()
    print('Audio:', src.path if src else '[!] no encontre un CHOP con low/mid/high en /project1 (Audioreact queda apagado)')
    backup = {}
    if APPLY and os.path.exists(BACKUP):
        with open(BACKUP, encoding='utf-8') as f:
            backup = json.load(f)

    for n in _bases():
        comp = op('%s/base%d' % (ROOT, n))
        if comp is None:
            print('\n[!] no existe base%d' % n)
            continue
        print('\n=== base%d' % n)
        if TAG in comp.tags or comp.fetch('tdvj_src', None, search=False, storeDefault=False):
            print('   (ya tenia contrato: se rearma)')
        plans, bad = [], False
        for slot, spec in zip(SLOTS, CONTRACT[n]):
            label, init, targets, problem = plan_slot(comp, slot, spec)
            if problem:
                print('   [!] %s: %s' % (slot, problem))
                bad = True
                continue
            plans.append((slot, label, init, targets))
            print('   %-10s -> %-28s arranca en %3d%%' % (slot, label, round(init * 100)))
        if n in INSPECT:
            inspect(comp)
        if not APPLY:
            continue
        if bad:
            print('   [!] se salta base%d por los errores de arriba' % n)
            continue

        key = comp.path
        if key not in backup:   # el primer respaldo manda (no se pisa al re-correr)
            entry = {}
            for _, _, _, targets in plans:
                for o, name, _ in targets:
                    p = getattr(o.par, name)
                    entry['%s|%s' % (o.path, name)] = {
                        'mode': str(p.mode), 'expr': p.expr, 'bind': p.bindExpr,
                        'val': p.eval()}
            backup[key] = entry

        orig = _clear(comp)
        pg = _page(comp, 'Contrato')
        for i, (slot, label, init, targets) in enumerate(plans):
            _float(pg, slot, '%d %s · %s' % (i + 1, slot, label), 0.0, 1.0, init, val=init)
        _toggle(pg, 'Bypass', 'Bypass', False)
        build_audio(comp, src)
        for slot, label, init, targets in plans:
            for o, name, expr in targets:
                getattr(o.par, name).expr = expr
        build_chain(comp, CONTRACT[n], orig)
        comp.tags.add(TAG)
        bad = [c for c in comp.children if TAG in c.tags and c.errors()]
        out = _io(comp)[1]
        if out is not None and not _up(out):
            print('   [!] out1 quedo sin conectar')
        elif bad:
            for c in bad:
                print('   [!] %s con error: %s' % (c.name, c.errors().strip().splitlines()[0]))
        else:
            print('   [ok] contrato aplicado, sin errores')

    if APPLY:
        with open(BACKUP, 'w', encoding='utf-8') as f:
            json.dump(backup, f, ensure_ascii=False, indent=1)
        print('\n[ok] respaldo -> %s' % BACKUP)
    else:
        print('\n[revision] nada se cambio. Prueba primero una: BASES = [18]; APPLY = True; exec(...)')


def restore():
    with open(BACKUP, encoding='utf-8') as f:
        backup = json.load(f)
    for n in _bases():
        comp = op('%s/base%d' % (ROOT, n))
        if comp is None or comp.path not in backup:
            continue
        _clear(comp)
        for key, b in backup[comp.path].items():
            path, name = key.split('|')
            o = op(path)
            p = getattr(o.par, name, None) if o else None
            if p is None:
                continue
            if b['mode'] == 'ParMode.EXPRESSION':
                p.expr = b['expr']
            elif b['mode'] == 'ParMode.BIND':
                p.bindExpr = b['bind']
                p.mode = ParMode.BIND
            else:
                p.mode = ParMode.CONSTANT
                p.val = b['val']
        for pg in list(comp.customPages):
            if pg.name in ('Contrato', 'Audio'):
                pg.destroy()
        comp.tags.discard(TAG)
        del backup[comp.path]
        print('[ok] base%d restaurada' % n)
    with open(BACKUP, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)


try:
    if RESTORE:
        restore()
    else:
        run()
finally:   # aunque truene, la siguiente corrida vuelve a modo revision
    APPLY = False
    RESTORE = False
    BASES = None
