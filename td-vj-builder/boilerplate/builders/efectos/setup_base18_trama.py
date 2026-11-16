# setup_base18_trama.py — FX Trama (Rio Salvaje): halftone con paleta del album, sobre la escena.
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
op('/project2/base18').allowCooking = True

CONFIG = dict(
    base='base18',
    shader='shaders/efectos/trama.frag',
    five_slots=[
        ('Mezcla', 'uMezcla', 0.0, 1.0, 0.8),
        ('Speed', 'uSpeed', 0.0, 2.0, 0.1),
        ('Angulo', 'uAngulo', 0.0, 1.57, 0.4),
        ('Color', 'uTinte', 0.0, 1.0, 0.0),
        ('Punto', 'uPunto', 4.0, 40.0, 12.0),
    ],
    color_uniforms=[
        ('Tinta', 'uTinta', (0.87, 0.12, 0.13)),
        ('Papel', 'uPapel', (0.06, 0.06, 0.07)),
    ],
)


def run():
    tdvj_core.build_effect(**CONFIG)

run()
