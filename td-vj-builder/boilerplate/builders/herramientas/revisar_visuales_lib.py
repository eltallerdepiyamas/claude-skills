# revisar_visuales_lib.py — modulo (vive como texto en /project2/show/revisar_visuales_lib). Pone al aire cada pad de
# BANCOS, deja que se caliente y mide la salida real (master_visuales) durante unos segundos:
#   brillo medio, % negro, % saturado, movimiento entre cuadros, correlacion con el audio, FPS y errores de la base.
# Escribe control/revision_visuales.json y control/revision_visuales.md. Lo arranca revisar_visuales.py.
import ast, json, math, re, time

CALENTAR = 180      # cuadros antes de medir (feedback acumulado como en show)
MUESTRAS = 24
CADA = 6            # cuadros entre muestras
R = op('/project2')


def bancos():
    src = open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read()
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'BANCOS':
            return ast.literal_eval(n.value)
    return {}


def base_de(k):
    sw = R.op('switch2')
    if k >= len(sw.inputs):
        return None
    o = sw.inputs[k]
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


def estado():
    return me.fetch('rv', None, search=False)


def arrancar(solo=None):
    lista = []
    for canal, pads in sorted(bancos().items()):
        if solo and canal not in solo:
            continue
        for i, p in enumerate(pads):
            if p:
                lista.append({'canal': canal, 'pad': i + 1, 'nombre': p[0], 'entrada': p[1]})
    me.store('rv', {'lista': lista, 'i': 0, 'res': [], 'antes': int(R.op('switch2').par.index.eval()),
                    't0': time.time()})
    siguiente()


def siguiente():
    st = estado()
    if st['i'] >= len(st['lista']):
        return terminar()
    v = st['lista'][st['i']]
    R.op('switch2').par.index = v['entrada']
    v['muestras'] = []
    run("op('%s').module.medir()" % me.path, delayFrames=CALENTAR)


def _frame():
    a = R.op('master_visuales').numpyArray(delayed=False)
    return a[::12, ::12, :3]


def medir():
    st = estado()
    v = st['lista'][st['i']]
    m = R.op('show').op('master_audio') or op('/project2/audio/master_audio')
    f = _frame()
    lum = f.max(axis=2)
    au = 0.0
    if m is not None:
        au = sum(float(m[c].eval()) for c in ('low', 'kick') if m[c] is not None)
    import numpy as np
    v['muestras'].append({'f': f, 'lum': float(lum.mean()), 'pico': float(np.percentile(lum, 99.5)), 'negro': float((lum < 0.02).mean()),
                          'sat': float((f.max(axis=2) > 0.97).mean()), 'audio': au, 't': time.perf_counter()})
    if len(v['muestras']) < MUESTRAS:
        run("op('%s').module.medir()" % me.path, delayFrames=CADA)
        return
    st['res'].append(resumir(v))
    st['i'] += 1
    siguiente()


def _corr(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va < 1e-9 or vb < 1e-9:
        return 0.0
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def resumir(v):
    ms = v.pop('muestras')
    lums = [s['lum'] for s in ms]
    mov = [float(abs(ms[k]['f'] - ms[k - 1]['f']).mean()) for k in range(1, len(ms))]
    aud = [s['audio'] for s in ms]
    dt = ms[-1]['t'] - ms[0]['t']
    fps = (len(ms) - 1) * CADA / dt if dt > 0 else 0
    b = base_de(v['entrada'])
    err = ''
    if b is not None:
        try:
            err = (b.errors(recurse=True) or '').splitlines()[0][:140] if b.errors(recurse=True) else ''
        except Exception:
            err = ''
    r = dict(v, base=b.name if b else '?',
             brillo=round(sum(lums) / len(lums), 3),
             pico=round(sum(s['pico'] for s in ms) / len(ms), 3),
             negro=round(sum(s['negro'] for s in ms) / len(ms), 3),
             saturado=round(sum(s['sat'] for s in ms) / len(ms), 3),
             movimiento=round(sum(mov) / len(mov), 4),
             audio_medio=round(sum(aud) / len(aud), 3),
             reaccion_brillo=round(_corr(lums, aud), 2),
             reaccion_mov=round(_corr(mov, aud[1:]), 2),
             fps=round(fps, 1), error=err)
    r['avisos'] = avisos(r)
    return r


def avisos(r):
    a = []
    # negro = no se ve NADA (pico de brillo), no 'fondo negro con lineas finas' que es el estilo de la casa
    if r['pico'] < 0.08:
        a.append('NEGRO')
    if r['saturado'] > 0.30 or r['brillo'] > 0.55:
        a.append('SATURA')
    if r['movimiento'] < 0.002:
        a.append('QUIETO')
    if r['audio_medio'] > 0.02 and abs(r['reaccion_brillo']) < 0.15 and abs(r['reaccion_mov']) < 0.15:
        a.append('REACCION DEBIL')
    if r['fps'] and r['fps'] < 0.85 * project.cookRate:
        a.append('FPS BAJO')
    if r['error']:
        a.append('ERROR')
    return a


def terminar():
    st = estado()
    R.op('switch2').par.index = st['antes']
    res = st['res']
    json.dump(res, open(project.folder + '/control/revision_visuales.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    L = ['# Revision de visuales (%s)' % time.strftime('%Y-%m-%d %H:%M'), '',
         'Medido en master_visuales con el audio real: %d visuales, %.0f s.' % (len(res), time.time() - st['t0']),
         'Brillo = media; Pico = brillo del 0.5%% mas brillante (NEGRO solo si pico < 0.08); negro/satura = fraccion de pantalla.',
         'Reaccion = correlacion con low+kick (-1..1); 0.00 exacto = el audio estaba en silencio en esa ventana. FPS vs cookRate %d.' % project.cookRate, '',
         '| Pad | Visual | Base | Brillo | Pico | Negro | Satura | Mov | Reacc brillo | Reacc mov | FPS | Avisos |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in res:
        L.append('| %d-%d | %s | %s | %.2f | %.2f | %.2f | %.2f | %.4f | %.2f | %.2f | %.0f | %s |' % (
            r['canal'], r['pad'], r['nombre'], r['base'], r['brillo'], r['pico'], r['negro'], r['saturado'], r['movimiento'],
            r['reaccion_brillo'], r['reaccion_mov'], r['fps'], ', '.join(r['avisos']) + (' — ' + r['error'] if r['error'] else '')))
    malos = [r for r in res if r['avisos']]
    L += ['', '## Con avisos: %d' % len(malos)] + ['- %d-%d %s: %s' % (r['canal'], r['pad'], r['nombre'], ', '.join(r['avisos'])) for r in malos]
    open(project.folder + '/control/revision_visuales.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    st['fin'] = True
    if me.fetch('luego_piloto', False, search=False):      # noche: al terminar prende el piloto (soak test)
        me.store('luego_piloto', False)
        S = op('/project2/show')
        if getattr(S.par, 'Pilotoauto', None) is not None:
            S.par.Pilotoauto = True
    print('[revision_visuales] listo:', len(res), 'visuales,', len(malos), 'con avisos')
