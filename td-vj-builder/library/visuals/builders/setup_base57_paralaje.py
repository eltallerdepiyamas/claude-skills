# setup_base57_paralaje.py: Paralaje (CH8). Paneles de lineas horizontales finas a distinta profundidad; cada kick mueve una capa.
# Recetario 26, ref. NONOTAK "Daydream". (Cortinas, base48, es la version de lineas verticales con aberturas.)
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base57')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base57',
    shader='shaders/visuales/paralaje.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.5),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Lineas', 'u_firma', 10.0, 200.0, 70.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
