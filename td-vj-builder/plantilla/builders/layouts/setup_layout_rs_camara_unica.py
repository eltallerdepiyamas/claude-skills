# ─────────────────────────────────────────────────────────────
# setup_layout_rs_camara_unica.py — "Cámara única" (Río Salvaje)
# Una sola cámara (la que elija "Cámara única", pestaña Camaras de escena_modular,
# Cam 1–6). Marco de color del álbum, vaivén lento y duotono opcionales. Para solos y momentos de uno.
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
    name='layout_rs_camara_unica',
    shader='shaders/layouts/layout_rs_camara_unica.frag',
    hero=False,
    sources=['SLOT_UNICA'],   # 1 cámara: la que elige "Cámara única" (Menu2)
    audio_target='Frame',     # el marco / bloque de color respira con el audio
    five_slots=[
        # (Par, uniform, min, max, default) — orden de ROL
        ('Frame',  'uFrame', 0.0, 1.0, 0.0),    # 1 intensidad: marco (Figura 0) / bloque de color (Figura 1-5)
        ('Drift',  'uDrift', 0.0, 1.0, 0.15),   # 2 velocidad: vaivén lento
        ('Zoom',   'uZoom',  1.0, 1.6, 1.05),   # 3 distorsión: acercamiento
        ('Tint',   'uTint',  0.0, 1.0, 0.0),    # 4 color: duotono con el color del marco
        ('Figura', 'uShape', 0.0, 5.0, 0.0),    # 5 firma: 0 pantalla completa · 1 círculo · 2 cuadrado ·
                                                #          3 triángulo · 4 medio disco · 5 rombo
    ],
    extras=[
        ('Hue',  'uHue',  0.0,  1.0,  0.0),     # color del marco / bloque (paleta del álbum)
        ('Size', 'uSize', 0.25, 0.48, 0.42),    # tamaño de la figura
    ],
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
