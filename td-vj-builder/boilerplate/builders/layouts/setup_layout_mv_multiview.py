# ─────────────────────────────────────────────────────────────
# setup_layout_mv_multiview.py — "Multiview" · MULTIVIEW (Río Salvaje)
# Las cámaras en mosaico limpio tipo multiview de transmisión, sobre crema. El acomodo sigue a
# "Camaras en multicam" (2 · 3 · 4 · 5). Borde del color de cada cámara, esquinas redondeadas y un
# tally que recorre las celdas.
#
# Uso: Text DAT con File = este .py → clic derecho → Run Script.
# Idempotente: conserva valores/MIDI de los sliders; rehace solo nodos con tag 'tdvj'.
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core, layout_core
importlib.reload(tdvj_core)
importlib.reload(layout_core)

CONFIG = dict(
    name='layout_mv_multiview',
    shader='shaders/layouts/layout_mv_multiview.frag',
    hero=False,
    audio_target='Border',   # el borde de color late con el audio
    five_slots=[
        # (Par, uniform, min, max, default) — orden de ROL
        ('Border', 'uBorder', 0.0, 1.0,  0.3),     # 1 intensidad: grosor del borde de color
        ('Tally',  'uTally',  0.0, 1.0,  0.0),     # 2 velocidad: tally que resalta una celda (0 = apagado)
        ('Round',  'uRound',  0.0, 1.0,  0.4),     # 3 distorsión: esquinas redondeadas
        ('Tint',   'uTint',   0.0, 1.0,  0.0),     # 4 color: duotono con el color de cada cámara
        ('Gap',    'uGap',    0.0, 0.08, 0.02),    # 5 firma: separación entre celdas
    ],
    extras=[],
    colors=[
        ('Color1',  'uColor1',  (0.96, 0.76, 0.06)),   # amarillo
        ('Color2',  'uColor2',  (0.09, 0.53, 0.36)),   # verde
        ('Color3',  'uColor3',  (0.10, 0.33, 0.78)),   # azul
        ('Color4',  'uColor4',  (0.06, 0.06, 0.07)),   # negro
        ('Color5',  'uColor5',  (0.87, 0.12, 0.13)),   # rojo
        ('Bgcolor', 'uBgColor', (0.93, 0.91, 0.86)),   # crema
    ],
)


def run():
    layout_core.build_layout(**CONFIG)

run()
