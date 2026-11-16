# ─────────────────────────────────────────────────────────────
# setup_base1_formas.py — Formas (Río Salvaje)
# Filas de figuras sólidas sobre crema (flyer) y discos de vinil con etiqueta verde/azul (foto de
# los viniles). Paleta del álbum: amarillo, verde, azul, negro, rojo. Generativo puro.
#
# Uso: Text DAT con File = este .py → clic derecho → Run Script (o build_all.py).
# Idempotente: conserva valores/MIDI de los sliders; rehace solo nodos con tag 'tdvj'.
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core
importlib.reload(tdvj_core)

CONFIG = dict(
    base='base1',
    shader='shaders/visuales/formas.glsl',
    source=None,
    five_slots=[
        # (Par, uniform, min, max, default) — orden de ROL
        ('Intensity', 'u_intensity', 0.0, 1.5, 1.0),   # 1 intensidad: tamaño de las figuras
        ('Speed',     'u_speed',     0.0, 2.0, 0.4),   # 2 velocidad: deslizamiento y giro
        ('Warp',      'u_warp',      0.0, 1.0, 0.3),   # 3 distorsión: desorden
        ('Palette',   'u_palette',   0.0, 1.0, 0.0),   # 4 color: rota la paleta
        ('Shapes',    'u_shapes',    2.0, 9.0, 4.0),   # 5 firma: figuras por fila
    ],
    signature_extras=[
        ('Vinyl',     'u_vinyl',     0.0, 1.0, 0.45),  # cuántas figuras son discos
        ('Dark',      'u_dark',      0.0, 1.0, 0.0),   # fondo crema → negro
    ],
    # paleta Río Salvaje: viniles (amarillo, verde, azul, negro, rojo) + crema del flyer
    color_uniforms=[
        ('Color1',  'u_c1', (0.96, 0.76, 0.06)),
        ('Color2',  'u_c2', (0.09, 0.53, 0.36)),
        ('Color3',  'u_c3', (0.10, 0.33, 0.78)),
        ('Color4',  'u_c4', (0.06, 0.06, 0.07)),
        ('Color5',  'u_c5', (0.87, 0.12, 0.13)),
        ('Bgcolor', 'u_bg', (0.93, 0.91, 0.86)),
    ],
)


def run():
    tdvj_core.build_visual(**CONFIG)

run()
