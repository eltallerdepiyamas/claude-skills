# setup_base49_pixel_sort.py: Pixel Sort (CH9). Formas de luz que se derriten en chorros de pixeles (feedback).
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)

tdvj_core.build_visual(
    base='base49',
    shader='shaders/visuales/pixel_sort.glsl',
    source=None,
    feedback=True,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.0),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Umbral', 'u_firma', 0.02, 0.6, 0.25),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
