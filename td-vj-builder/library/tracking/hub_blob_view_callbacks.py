"""
hub_blob_view_callbacks.py — Script TOP  <padre>/tracking_input/blob_view
Muestra lo que "ve" el hub con Source = top (misma orientación que el TOP de entrada):

    rojo oscuro  (todo el cuadro) no hay imagen (Source ≠ top o falta el TOP)
    gris tenue   brillo del TOP por debajo del Threshold
    blanco       máscara: lo que cuenta como mancha
    rojo         mancha detectada que NO se sigue (muy chica o sobra por Max People)
    color        persona seguida: un color por slot (p0 amarillo, p1 cian, p2 magenta…)
"""
import numpy as np

SLOT_COLORS = [(1, .9, 0), (0, .9, 1), (1, 0, 1), (.2, 1, .2),
               (1, .5, 0), (.4, .4, 1), (1, .3, .3), (1, 1, 1)]


def onSetupParameters(scriptOp):
    return


def _cross(img, x, y, color, r):
    h, w = img.shape[:2]
    cx, cy = int(x * w), int(y * h)
    for d in range(-r, r + 1):
        for yy, xx in ((cy, cx + d), (cy + d, cx)):
            if 0 <= yy < h and 0 <= xx < w:
                img[yy, xx, :3] = color


def onCook(scriptOp):
    comp = scriptOp.parent()
    comp.op('out1').numChans               # jala el cook del hub antes de leer su estado
    st = comp.fetch('tdvj_hub_blobs', None, search=False) or {}
    mask = st.get('mask')
    small = comp.op('blob_small')
    img_in = small.numpyArray(delayed=True) if (small is not None and mask is not None) else None
    if mask is None or img_in is None:
        img = np.zeros((60, 80, 4), np.float32)
        img[..., 0], img[..., 3] = 0.35, 1.0
        scriptOp.copyNumpyArray(img)
        return
    h, w = mask.shape
    img = np.zeros((h, w, 4), np.float32)
    lum = img_in[..., :3].max(axis=2)
    if lum.shape == mask.shape:
        img[..., 0] = img[..., 1] = img[..., 2] = np.clip(lum, 0, 1) * 0.35
    img[mask, :3] = 0.85
    img[..., 3] = 1.0
    for x, y, _n in st.get('blobs', []):
        _cross(img, x, y, (1, 0, 0), 1)
    r = max(2, w // 40)
    for t in st.get('tracks', []):
        if t['miss'] == 0:
            _cross(img, t['x'], t['y'], SLOT_COLORS[t['slot']], r)
    scriptOp.copyNumpyArray(np.ascontiguousarray(img))
