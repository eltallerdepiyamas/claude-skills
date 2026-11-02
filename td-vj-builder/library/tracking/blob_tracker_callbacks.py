"""
blob_tracker_callbacks.py — callbacks del Script CHOP /project2/webcam_tracker/tracker

Webcam → máscara por sustracción de fondo → blobs → hasta 8 personas con ID estable.
Emite EXACTAMENTE el contrato que luego manda el Hokuyo:

    p{i}x, p{i}y   posición normalizada 0..1 (origen abajo-izquierda, como vUV)
    p{i}a          1 = activa, 0 = slot libre
    p{i}id         ID estable mientras la persona siga detectada

Parámetros en el COMP webcam_tracker (página Tracker, los crea setup_demo_tools.py).
Entrada: el TOP 'small' del mismo COMP (webcam reducida a ~80x60).
    Capturebg   pulso: guarda el fondo actual (sal del cuadro y púlsalo)
    Threshold   diferencia mínima con el fondo para contar como "persona"
    Adapt       0 = fondo fijo · >0 = el fondo se actualiza lento
    Minarea     píxeles mínimos de un blob (en la resolución reducida, 80x60 = 4800 px)
    Dilate      engorda la máscara N píxeles: une pedazos de una misma persona en un solo blob
    Matchdist   distancia máx. (0..1) para considerar que un blob es la misma persona
    Smooth      suavizado de posición 0..0.95
    Hold        frames que se conserva una persona perdida antes de soltarla
    Maxpeople   1..8
    Mirror      espejo horizontal (webcam frontal)
    Flipy       invierte Y si el punto se mueve al revés
"""
import numpy as np

MAX_SLOTS = 8
STATE_KEY = 'tdvj_tracker'
_state = None   # se asigna en cada cook desde el storage del COMP (compartido con tracker_view)


def get_state(comp):
    """Estado en el storage del COMP webcam_tracker: lo comparten tracker, view y Capture BG."""
    st = comp.fetch(STATE_KEY, None, search=False)
    if st is None:
        st = {'bg': None, 'tracks': [], 'next_id': 0, 'capture': False,
              'diff': None, 'mask': None, 'blobs': [], 'status': 'sin cocinar'}
        comp.store(STATE_KEY, st)
    return st


def onSetupParameters(scriptOp):
    return  # los parámetros los crea setup_demo_tools.py


def capture_bg(comp=None):
    """Lo llama el Parameter Execute DAT al pulsar Capturebg en el COMP."""
    get_state(comp if comp is not None else me.parent())['capture'] = True


def _blobs(mask, min_area):
    h, w = mask.shape
    m = mask.tolist()
    seen = [[False] * w for _ in range(h)]
    out = []
    for y0 in range(h):
        row = m[y0]
        for x0 in range(w):
            if not row[x0] or seen[y0][x0]:
                continue
            stack = [(y0, x0)]
            seen[y0][x0] = True
            sx = sy = n = 0
            while stack:
                y, x = stack.pop()
                sx += x
                sy += y
                n += 1
                for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= yy < h and 0 <= xx < w and m[yy][xx] and not seen[yy][xx]:
                        seen[yy][xx] = True
                        stack.append((yy, xx))
            if n >= min_area:
                out.append([(sx / n + 0.5) / w, (sy / n + 0.5) / h, n])
    out.sort(key=lambda b: -b[2])
    return out


def _track(blobs, p):
    tracks = _state['tracks']
    maxp = max(1, min(MAX_SLOTS, int(p.Maxpeople)))
    match_d = float(p.Matchdist)
    smooth = min(max(float(p.Smooth), 0.0), 0.95)
    hold = int(p.Hold)

    free = list(range(len(blobs)))
    # emparejado greedy por distancia (pocos blobs → suficiente)
    pairs = sorted(
        ((np.hypot(t['x'] - blobs[b][0], t['y'] - blobs[b][1]), ti, b)
         for ti, t in enumerate(tracks) for b in free),
        key=lambda e: e[0])
    used_t, used_b = set(), set()
    for d, ti, b in pairs:
        if d > match_d or ti in used_t or b in used_b:
            continue
        t = tracks[ti]
        t['x'] = t['x'] * smooth + blobs[b][0] * (1 - smooth)
        t['y'] = t['y'] * smooth + blobs[b][1] * (1 - smooth)
        t['miss'] = 0
        used_t.add(ti)
        used_b.add(b)

    for ti, t in enumerate(tracks):
        if ti not in used_t:
            t['miss'] += 1
    tracks[:] = [t for t in tracks if t['miss'] <= hold]

    taken = {t['slot'] for t in tracks}
    for b in free:
        if b in used_b or len(tracks) >= maxp:
            continue
        slot = next(s for s in range(MAX_SLOTS) if s not in taken)
        taken.add(slot)
        tracks.append({'slot': slot, 'id': _state['next_id'],
                       'x': blobs[b][0], 'y': blobs[b][1], 'miss': 0})
        _state['next_id'] += 1
    return tracks


def onCook(scriptOp):
    global _state
    _state = get_state(scriptOp.parent())
    p = scriptOp.parent().par
    scriptOp.clear()
    scriptOp.numSamples = 1

    tracks = []
    top = scriptOp.parent().op('small')
    img = top.numpyArray(delayed=True) if top is not None else None
    _state['status'] = 'sin TOP small' if top is None else ('esperando imagen' if img is None else 'ok')
    if img is not None:
        lum = img[..., :3].mean(axis=2)
        bg = _state['bg']
        if bg is None or bg.shape != lum.shape or _state['capture']:
            bg = lum.copy()
            _state['capture'] = False
            _state['tracks'] = []
        diff = np.abs(lum - bg)
        mask = diff > float(p.Threshold)
        for _ in range(int(p.Dilate)):
            m = mask.copy()
            m[1:] |= mask[:-1]
            m[:-1] |= mask[1:]
            m[:, 1:] |= mask[:, :-1]
            m[:, :-1] |= mask[:, 1:]
            mask = m
        adapt = float(p.Adapt)
        if adapt > 0:
            bg = bg * (1 - adapt) + lum * adapt
        _state['bg'] = bg
        blobs = _blobs(mask, int(p.Minarea))
        tracks = _track(blobs, p)
        _state['diff'], _state['mask'], _state['blobs'] = diff, mask, blobs

    by_slot = {t['slot']: t for t in tracks}
    for i in range(MAX_SLOTS):
        t = by_slot.get(i)
        x, y, a, pid = (t['x'], t['y'], 1.0, float(t['id'])) if t else (0.0, 0.0, 0.0, float(i))
        if t and p.Mirror:
            x = 1.0 - x
        if t and p.Flipy:
            y = 1.0 - y
        for suffix, v in (('x', x), ('y', y), ('a', a), ('id', pid)):
            scriptOp.appendChan('p%d%s' % (i, suffix))[0] = v
    return
