# ─────────────────────────────────────────────────────────────
# setup_base1_industrial_grid.py — Rejilla industrial (pantalla central · techno industrial)
# Rejilla de acero + moiré sobre placas metálicas; el audio enciende celdas, abre cortes
# horizontales y empuja el brillo. Generativo puro.
#
# Uso: Text DAT con File = este .py → clic derecho → Run Script.
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
    shader='shaders/visuales/industrial_grid.glsl',
    source=None,
    five_slots=[
        # (Par, uniform, min, max, default) — orden de ROL
        ('Intensity', 'u_intensity', 0.0, 2.0,  1.0),   # 1 intensidad: brillo general
        ('Speed',     'u_speed',     0.0, 4.0,  1.0),   # 2 velocidad: scroll, barrido, cortes
        ('Warp',      'u_warp',      0.0, 1.0,  0.3),   # 3 distorsión: cortes + ondulación
        ('Accent',    'u_accent',    0.0, 1.0,  0.3),   # 4 color: blanco → acento
        ('Cells',     'u_cells',     4.0, 48.0, 12.0),  # 5 firma: densidad de la rejilla
    ],
    signature_extras=[
        ('Moire',     'u_moire',     0.0, 1.0,  0.4),   # segunda rejilla girada
        ('Line',      'u_line',      0.02, 0.3, 0.06),  # grosor de línea (fracción de celda)
    ],
    # paleta Corona: blanco · amarillo Corona (acento) · negro
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 1.0, 1.0)),
        ('Color2', 'u_color2', (1.0, 0.78, 0.17)),
        ('Color3', 'u_color3', (0.008, 0.008, 0.01)),
    ],
)


def run():
    tdvj_core.build_visual(**CONFIG)

run()
