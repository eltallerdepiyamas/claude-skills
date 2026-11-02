"""
tracking_hub_callbacks.py — Script CHOP  <padre>/tracking_input/hub

UNA sola entrada de tracking para todas las bases. Todas leen  tracking_input/out1.
Salida (contrato): p{i}x p{i}y (0..1, origen abajo-izquierda) · p{i}a (0/1) · p{i}id   i = 0..7

Parámetros en el COMP tracking_input (página Input):
    Source        simulate = caminantes sintéticos · webcam = webcam_tracker/tracking
                  external = CHOP del Hokuyo · top = TOP con manchas blancas (una mancha = una persona)
    Externalchop  CHOP del Hokuyo (arrástralo aquí)
    Externaltop   TOP con manchas blancas sobre negro; el cuadro completo = el piso
    Format        contract = ya trae p0x p0y p0a p0id… · samples = un canal X y uno Y, un sample por persona
    Xchan/Ychan/Idchan   nombres de canal para Format = samples
    Units         normalized (0..1) · meters (se divide entre Floor W/H después de restar el origen)
    Originx/y     dónde cae el (0,0) del sensor respecto a la esquina abajo-izquierda del piso (m)
    Swapxy/Flipx/Flipy   alinear ejes del sensor con el piso (también aplican a Source = top)
    Clip          descarta puntos fuera del piso
    Simcount/Simspeed    caminantes sintéticos
    Retrack       (Format = samples) ignora el orden de filas y los IDs que llegan: re-sigue los
                  puntos con el mismo tracker que el TOP (para listas que saltan / IDs que cambian)

Página Seguimiento. Source = top: el TOP se reduce en blob_small (Analysisw px de ancho) y aquí
se umbraliza, se buscan manchas y se siguen con ID estable. Matchdist/Smooth/Hold/Maxpeople
también aplican a Retrack:
    Threshold     brillo mínimo (0..1) para contar como mancha
    Minarea       píxeles mínimos de una mancha (en la resolución de análisis)
    Dilate        engorda la máscara N px: une pedazos de una misma persona
    Matchdist     distancia máx. (0..1) para considerar que una mancha es la misma persona
    Smooth        suavizado de posición 0..0.95
    Hold          frames que se conserva una persona perdida antes de soltarla
    Maxpeople     1..8
El estado (máscara, manchas, personas) vive en el storage del COMP → lo lee blob_view.
"""
import math
import numpy as np

MAX = 8
STATE_KEY = 'tdvj_hub_blobs'


def onSetupParameters(scriptOp):
    return


def _chan(chop, name, i=0, default=0.0):
    # ojo: en TD un Channel NO tiene numSamples (eso es del CHOP); sus valores están en .vals
    c = chop[name] if chop is not None and name else None
    if c is None:
        return default
    vals = c.vals
    return float(vals[i]) if i < len(vals) else default


def _simulate(p, t):
    n, s = int(p.Simcount), float(p.Simspeed)
    return [(0.5 + 0.38 * math.sin(t * s * (0.13 + 0.037 * i) + i * 1.9),
             0.5 + 0.36 * math.sin(t * s * (0.11 + 0.029 * i) + i * 0.7 + 1.3),
             1.0 if i < n else 0.0, float(i)) for i in range(MAX)]


def _contract(chop):
    return [(_chan(chop, 'p%dx' % i), _chan(chop, 'p%dy' % i),
             _chan(chop, 'p%da' % i), _chan(chop, 'p%did' % i, default=float(i))) for i in range(MAX)]


def _samples(chop, p):
    xs = chop[p.Xchan.eval()] if chop is not None else None
    ys = chop[p.Ychan.eval()] if chop is not None else None
    if xs is None or ys is None:
        return []
    xv, yv = xs.vals, ys.vals
    n = min(len(xv), len(yv), MAX)
    return [(float(xv[i]), float(yv[i]), 1.0, _chan(chop, p.Idchan.eval(), i, float(i))) for i in range(n)]


def _transform(pt, p, meters=None):
    x, y, a, pid = pt
    if meters is None:
        meters = p.Units.eval() == 'meters'
    if p.Swapxy:
        x, y = y, x
    if meters:
        x = (x - float(p.Originx)) / max(float(p.Floorw), 1e-3)
        y = (y - float(p.Originy)) / max(float(p.Floorh), 1e-3)
    if p.Flipx:
        x = 1.0 - x
    if p.Flipy:
        y = 1.0 - y
    if p.Clip and not (-0.05 <= x <= 1.05 and -0.05 <= y <= 1.05):
        a = 0.0
    return (x, y, a, pid)


# ─────────────────────────────────────────── Source = top: manchas blancas → personas
def get_state(comp):
    st = comp.fetch(STATE_KEY, None, search=False)
    if st is None:
        st = {'tracks': [], 'next_id': 0, 'mask': None, 'blobs': []}
        comp.store(STATE_KEY, st)
    return st


def _blobs(mask, min_area):
    """Componentes conexas (4-vecinos) recorriendo solo los píxeles encendidos.
    numpyArray de TD: fila 0 = abajo → y sale ya con origen abajo-izquierda."""
    h, w = mask.shape
    todo = set(map(tuple, np.argwhere(mask).tolist()))
    out = []
    while todo:
        stack = [todo.pop()]
        sx = sy = n = 0
        while stack:
            y, x = stack.pop()
            sx += x
            sy += y
            n += 1
            for nb in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if nb in todo:
                    todo.remove(nb)
                    stack.append(nb)
        if n >= min_area:
            out.append([(sx / n + 0.5) / w, (sy / n + 0.5) / h, n])
    out.sort(key=lambda b: -b[2])
    return out


def _track(st, blobs, p):
    """Empareja manchas con personas del frame anterior → ID estable. Sin lista que crezca:
    cada frame se reconstruye desde la imagen y las personas perdidas se sueltan tras Hold frames."""
    tracks = st['tracks']
    maxp = max(1, min(MAX, int(p.Maxpeople)))
    match_d = float(p.Matchdist)
    smooth = min(max(float(p.Smooth), 0.0), 0.95)
    hold = int(p.Hold)

    pairs = sorted(((math.hypot(t['x'] - b[0], t['y'] - b[1]), ti, bi)
                    for ti, t in enumerate(tracks) for bi, b in enumerate(blobs)), key=lambda e: e[0])
    used_t, used_b = set(), set()
    for d, ti, bi in pairs:
        if d > match_d or ti in used_t or bi in used_b:
            continue
        t = tracks[ti]
        t['x'] = t['x'] * smooth + blobs[bi][0] * (1 - smooth)
        t['y'] = t['y'] * smooth + blobs[bi][1] * (1 - smooth)
        t['miss'] = 0
        used_t.add(ti)
        used_b.add(bi)

    for ti, t in enumerate(tracks):
        if ti not in used_t:
            t['miss'] += 1
    tracks[:] = [t for t in tracks if t['miss'] <= hold]

    taken = {t['slot'] for t in tracks}
    for bi, b in enumerate(blobs):
        if bi in used_b or len(tracks) >= maxp:
            continue
        slot = next(s for s in range(MAX) if s not in taken)
        taken.add(slot)
        tracks.append({'slot': slot, 'id': st['next_id'], 'x': b[0], 'y': b[1], 'miss': 0})
        st['next_id'] += 1
    return tracks


def _to_slots(tracks):
    by_slot = {t['slot']: t for t in tracks}
    return [(t['x'], t['y'], 1.0, float(t['id'])) if t else (0.0, 0.0, 0.0, float(i))
            for i, t in ((i, by_slot.get(i)) for i in range(MAX))]


def _retrack(comp, p, pts):
    """Puntos ya transformados → personas con slot e ID propios (orden e IDs de entrada se ignoran)."""
    st = get_state(comp)
    blobs = [[x, y, 1] for x, y, a, _ in pts if a > 0.5]
    st['mask'], st['blobs'] = None, blobs
    return _to_slots(_track(st, blobs, p)), '%d punto(s)' % len(blobs)


def _from_top(comp, p):
    """Devuelve (puntos por slot, mensaje de status)."""
    st = get_state(comp)
    small = comp.op('blob_small')
    img = small.numpyArray(delayed=True) if small is not None else None
    if img is None:
        st['mask'], st['blobs'] = None, []
        return [], 'esperando imagen'
    lum = img[..., :3].max(axis=2)          # manchas blancas (o de cualquier color) sobre negro
    mask = lum > float(p.Threshold)
    for _ in range(int(p.Dilate)):
        m = mask.copy()
        m[1:] |= mask[:-1]
        m[:-1] |= mask[1:]
        m[:, 1:] |= mask[:, :-1]
        m[:, :-1] |= mask[:, 1:]
        mask = m
    blobs = _blobs(mask, int(p.Minarea))
    tracks = _track(st, blobs, p)
    st['mask'], st['blobs'] = mask, blobs

    pts = [_transform(pt, p, meters=False) if pt[2] > 0.5 else pt for pt in _to_slots(tracks)]
    return pts, '%d mancha(s)' % len(blobs)


def onCook(scriptOp):
    comp = scriptOp.parent()
    p = comp.par
    src = p.Source.eval()
    extra = ''

    if src == 'simulate':
        pts = _simulate(p, absTime.seconds)
    elif src == 'webcam':
        pts = _contract(comp.parent().op('webcam_tracker/tracking'))
    elif src == 'top':
        pts, extra = _from_top(comp, p)
    else:
        chop = p.Externalchop.eval()
        samples = p.Format.eval() == 'samples'
        raw = _samples(chop, p) if samples else _contract(chop)
        pts = [_transform(pt, p) for pt in raw]
        if samples and p.Retrack:
            pts, extra = _retrack(comp, p, pts)

    pts = (pts + [(0.0, 0.0, 0.0, float(i)) for i in range(len(pts), MAX)])[:MAX]
    scriptOp.clear()
    scriptOp.numSamples = 1
    for i, (x, y, a, pid) in enumerate(pts):
        for suffix, v in (('x', x), ('y', y), ('a', a), ('id', pid)):
            scriptOp.appendChan('p%d%s' % (i, suffix))[0] = v

    status = '%s · %d persona(s)' % (src, sum(1 for pt in pts if pt[2] > 0.5))
    if extra:
        status += ' · ' + extra
    if src == 'external' and p.Externalchop.eval() is None:
        status = 'external · falta el CHOP del Hokuyo'
    if src == 'top' and p.Externaltop.eval() is None:
        status = 'top · falta el TOP de manchas'
    if p.Status.eval() != status:
        try:
            p.Status = status
        except Exception:
            pass
    return
