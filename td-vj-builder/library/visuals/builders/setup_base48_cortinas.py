# setup_base48_cortinas.py: Cortinas (CH9). Capas de lineas verticales con paralaje y moire; el bajo abre las cortinas.
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)

tdvj_core.build_visual(
    base='base48',
    shader='shaders/visuales/cortinas.glsl',
    source=None,
    feedback=False,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.2),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Densidad', 'u_firma', 8.0, 120.0, 40.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
