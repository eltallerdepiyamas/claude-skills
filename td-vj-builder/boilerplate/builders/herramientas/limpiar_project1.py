# ─────────────────────────────────────────────────────────────
# limpiar_project1.py — /project1 = SOLO FX globales + salida. APPLY = True: solo dice que haria.
#   Se queda:  select47 (visuales, null19 de /project2) · select2 (FX, null28) -> feedback_HSV1 -> (null42, lookup2 + rampas/base6/switch5/blend_switch2-3)
#              -> V2_COLOR -> curcuitBending1 -> color_final -> ndiout1
#   CONTROL (MIDI, selects, math, nulls, tablas...)  -> /project2/control_p1
#   AUDIO (archivo, vivo, fuente, gain, switch6, audioAnalysis, null4, monitor) -> /project2/audio
#   Lo demas (monochrome, overlays, strobe, PIP, blend_switch, curcuitBending duplicado) -> _respaldo
# Antes de quitar nada reescribe TODAS las referencias (op('x'), '/project1/x', selects, OP params)
# en /project1, /project2 y las copias, a la ruta nueva. Los cables entre grupos distintos no se
# pueden conservar: se listan (y si es CHOP -> se reemplaza por un Select en el destino).
# ─────────────────────────────────────────────────────────────
import re

APPLY = True
P1, P2 = op('/project1'), op('/project2')
KEEP = ['select2', 'select47', 'color_final_info', 'color_final_pixel', 'color_final_compute', 'feedback_HSV1', 'null42', 'lookup2', 'base6', 'switch5', 'blend_switch2', 'blend_switch3',
        'V2_COLOR', 'curcuitBending1', 'color_final', 'color_final_frag', 'ndiout1'] + ['ramp%d' % i for i in range(1, 33)]
AUDIO = ['Little_Jesus___La_Magia', 'audio_vivo', 'audio_fuente', 'audio_gain', 'switch6', 'audioAnalysis', 'null4', 'audiodevout1']
CADENA = ['select2', 'feedback_HSV1', None, 'V2_COLOR', 'curcuitBending1', 'color_final', 'ndiout1']   # cables finales

kids = {o.name: o for o in P1.children if not (o.OPType == 'annotateCOMP')}
grupo = {}
for n, o in kids.items():
    if n in KEEP:
        grupo[n] = 'keep'
    elif n in AUDIO:
        grupo[n] = 'audio'
    elif o.isCHOP or o.isDAT:
        grupo[n] = 'control'
    else:
        grupo[n] = 'viejo'
DEST = {'keep': '/project1', 'audio': '/project2/audio', 'control': '/project2/control_p1',
        'viejo': '/project2/_respaldo/project1_fx_viejos'}
nueva = {n: DEST[g] + '/' + n for n, g in grupo.items()}
movidos = [n for n, g in grupo.items() if g != 'keep']
NAMES = sorted(movidos + [n for n in KEEP if n in kids], key=len, reverse=True)
ABS = re.compile(r"/project1/(%s)(?=[/\W]|$)" % '|'.join(re.escape(n) for n in NAMES))
REL = re.compile(r"""op\((['"])(%s)\1\)""" % '|'.join(re.escape(n) for n in NAMES))


def fix_abs(t):
    return ABS.sub(lambda m: nueva[m.group(1)], t)


def fix_rel(t):
    return REL.sub(lambda m: "op('%s')" % nueva[m.group(2)], t)


def es_op_par(p):
    return p.style in ('TOP', 'CHOP', 'DAT', 'COMP', 'SOP', 'MAT', 'OP', 'Object', 'PanelCOMP', 'OBJ')


def reescribir(o, relativo):
    """Reescribe los parametros de o. relativo=True: o estaba en el primer nivel de /project1."""
    n = 0
    for p in o.pars():
        try:
            if p.mode == ParMode.EXPRESSION:
                t = p.expr
                t2 = fix_abs(fix_rel(t) if relativo else t)
                if t2 != t:
                    if APPLY:
                        p.expr = t2
                    n += 1
            elif p.mode == ParMode.CONSTANT and es_op_par(p) and isinstance(p.val, str) and p.val:
                toks = p.val.split()
                new = []
                for tk in toks:
                    tk2 = fix_abs(tk)
                    if relativo and tk2 == tk:
                        head = tk.split('/')[0]
                        if head in nueva and not tk.startswith('/'):
                            tk2 = nueva[head] + tk[len(head):]
                    new.append(tk2)
                v2 = ' '.join(new)
                if v2 != p.val:
                    if APPLY:
                        p.val = v2
                    n += 1
        except Exception:
            pass
    return n


# --- exports (CHOP -> parametro): se pierden al mover el CHOP: avisar
exports = []
for n, o in kids.items():
    if grupo[n] == 'keep':
        for p in o.pars():
            if p.mode == ParMode.EXPORT:
                exports.append('%s.%s' % (n, p.name))
# --- cables entre grupos
cruces = []
for n, o in kids.items():
    for k, i in enumerate(o.inputs):
        if i.parent() == P1 and grupo.get(i.name) != grupo[n]:
            cruces.append((i.name, grupo.get(i.name), n, grupo[n], k, o.isCHOP))

print('==== limpiar_project1 (%s) ====' % ('APLICANDO' if APPLY else 'PRUEBA: APPLY = True para hacerlo'))
for g in ('keep', 'control', 'audio', 'viejo'):
    ns = sorted(n for n in grupo if grupo[n] == g)
    print('  %-8s %3d  %s' % (g, len(ns), ', '.join(ns[:14]) + (' ...' if len(ns) > 14 else '')))
print('  exports en lo que se queda (se perderian):', exports or 'ninguno')
print('  cables entre grupos:', len(cruces))
for c in cruces:
    if c[1] != 'viejo' and c[3] != 'viejo':
        print('     %s (%s) -> %s (%s) entrada %d %s' % (c[0], c[1], c[2], c[3], c[4], 'CHOP' if c[5] else ''))

if APPLY:
    # 1. copias en su destino (copyOPs conserva los cables dentro del grupo)
    for g in ('control', 'audio', 'viejo'):
        path = DEST[g]
        parent_path, name = path.rsplit('/', 1)
        d = op(path) or op(parent_path).create(baseCOMP, name)
        if g == 'viejo':
            d.allowCooking = False
        falta = [kids[n] for n in grupo if grupo[n] == g and d.op(n) is None]   # idempotente: no duplica
        if falta:
            d.copyOPs(falta)
    # 2. referencias
    total = 0
    faltan = []
    for n, g in grupo.items():
        if g == 'viejo':
            continue
        o = op(nueva[n])
        if o is None:
            faltan.append(n)
            continue
        total += reescribir(o, True)
        for c in (o.findChildren() if o.isCOMP else []):
            total += reescribir(c, False)
    for root in (P2,):
        for o in root.findChildren():
            if '/_respaldo' in o.path or o.path.startswith(('/project2/control_p1', '/project2/audio')):
                continue
            total += reescribir(o, False)
    print('[ok] referencias reescritas:', total, '· sin copia en destino (no se quitan):', faltan)
    movidos[:] = [n for n in movidos if n not in faltan]
    # 3. cables CHOP entre control <-> audio: Select en el destino
    for src, gs, dst, gd, k, chop in cruces:
        if gs in ('viejo',) or gd in ('viejo',) or not chop:
            continue
        o = op(nueva[dst])
        s = o.parent().create(selectCHOP, 'sel_' + src)
        s.par.chops = nueva[src]
        o.inputConnectors[k].connect(s)
        print('    cable %s -> %s ahora por Select %s' % (src, dst, s.path))
    # 4. quitar de /project1 lo movido
    for n in movidos:
        if kids[n].valid:
            kids[n].destroy()
    # 5. cadena final de lo que se queda (dst, entrada, src)
    PARES = [('feedback_HSV1', 0, 'select2'), ('null42', 0, 'feedback_HSV1'), ('lookup2', 0, 'feedback_HSV1'),
             ('V2_COLOR', 0, 'null42'), ('V2_COLOR', 1, 'lookup2'), ('curcuitBending1', 0, 'V2_COLOR'),
             ('color_final', 0, 'curcuitBending1'), ('ndiout1', 0, 'color_final')]
    for dst, k, src in PARES:
        d, s_ = P1.op(dst), P1.op(src)
        if d is not None and s_ is not None:
            d.inputConnectors[k].connect(s_.outputConnectors[0])
    print('[ok] /project1 =', ', '.join(sorted(o.name for o in P1.children)))
