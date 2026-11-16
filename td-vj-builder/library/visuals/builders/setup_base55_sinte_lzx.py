# setup_base55_sinte_lzx.py: Sinte LZX (CH8). Patch de sintetizador de video: rampas -> osciladores -> wavefolder -> colorizer + CRT.
# Recetarios 35-38, 42 y 43, ref. LZX Industries / Sandin Image Processor. Osciladores a tempo con el kick (kick_step).
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base55')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base55',
    shader='shaders/visuales/sinte_lzx.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.35),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Pliegues', 'u_firma', 1.0, 8.0, 3.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
