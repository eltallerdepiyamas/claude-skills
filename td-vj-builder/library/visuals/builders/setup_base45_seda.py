# setup_base45_seda.py: Seda (CH9). Hilos de humo advectados por curl noise (feedback).
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)

tdvj_core.build_visual(
    base='base45',
    shader='shaders/visuales/seda.glsl',
    source=None,
    feedback=True,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.5),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Turbulencia', 'u_firma', 0.5, 6.0, 2.0),
    ],
    signature_extras=[('Estela', 'u_estela', 0.9, 0.998, 0.985)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
