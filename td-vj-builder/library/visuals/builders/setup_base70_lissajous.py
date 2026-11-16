# setup_base70_lissajous.py: Lissajous (CH8). Figura de Lissajous en osciloscopio XY con fosforo (feedback); el kick avanza la razon de frecuencias.
# Recetario 32, ref. oscilloscope music (Jerobeam Fenderson). Distinto del Osciloscopio de CH10 (forma de onda) y del Armonografo.
# feedback=True: feedback1 (cuadro anterior) entra en sTD2DInputs[0]; Reset estela lo limpia.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base70')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base70',
    shader='shaders/visuales/lissajous.glsl',
    source=None,
    feedback=True,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Razon', 'u_firma', 0.0, 7.0, 2.0),
    ],
    signature_extras=[
        ('Persistencia', 'u_persist', 0.7, 0.97, 0.9),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
