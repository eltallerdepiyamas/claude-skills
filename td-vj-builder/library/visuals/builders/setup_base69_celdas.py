# setup_base69_celdas.py: Celdas (CH8). Voronoi barato (3x3): solo bordes finos F2-F1 que respiran; el kick reacomoda las semillas.
# Recetario 33, ref. Inigo Quilez (voronoi y bordes) / Andy Lomas - Max Cooper. Sin logo, sin relleno de celdas.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base69')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base69',
    shader='shaders/visuales/celdas.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Celdas', 'u_firma', 3.0, 24.0, 8.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
