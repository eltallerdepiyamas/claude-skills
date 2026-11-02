"""
tracker_view_callbacks.py — Script TOP /project2/webcam_tracker/view
Muestra lo que "ve" el tracker (misma orientación/espejo que el render):

    rojo oscuro  (todo el cuadro) el tracker no está recibiendo imagen
    gris tenue   diferencia con el fondo (por debajo del Threshold)
    blanco       máscara: lo que cuenta como "persona"
    rojo         blob detectado que NO se sigue (muy chico o sobra por Max People)
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
    comp.op('tracking').numChans          # jala el cook del tracker antes de leer su estado
    st = comp.fetch('tdvj_tracker', None, search=False) or {}
    p = comp.par
    diff, mask = st.get('diff'), st.get('mask')
    if diff is None:
        # rojo oscuro = el tracker no ha producido datos (ver Textport / st['status'])
        img = np.zeros((60, 80, 4), np.float32)
        img[..., 0], img[..., 3] = 0.35, 1.0
        scriptOp.copyNumpyArray(img)
        return
    h, w = mask.shape
    img = np.zeros((h, w, 4), np.float32)
    g = np.clip(diff * 3.0, 0, 1) * 0.35
    img[..., 0] = img[..., 1] = img[..., 2] = g
    img[mask, :3] = 0.85
    img[..., 3] = 1.0

    for x, y, _n in st.get('blobs', []):
        _cross(img, x, y, (1, 0, 0), 1)
    for t in st['tracks']:
        if t['miss'] == 0:
            _cross(img, t['x'], t['y'], SLOT_COLORS[t['slot']], 3)

    if p.Mirror:
        img = img[:, ::-1]
    scriptOp.copyNumpyArray(np.ascontiguousarray(img))
