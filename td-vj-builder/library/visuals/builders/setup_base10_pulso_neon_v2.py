# setup_base10_pulso_neon.py: Pulso neon
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core
importlib.reload(tdvj_core)

CONFIG = dict(
    base='base10',
    shader='shaders/visuales/pulso_neon.glsl',
    source=None,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),      # 0 rojo, 1 turquesa
        ('Lineas', 'u_lineas', 1.0, 24.0, 7.0),
    ],
    signature_extras=[('Grosor', 'u_grosor', 0.0002, 0.004, 0.0012),],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)

tdvj_core.build_visual(**CONFIG)
