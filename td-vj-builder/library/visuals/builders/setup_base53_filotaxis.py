# setup_base53_filotaxis.py: Filotaxis (CH8). Espiral de Vogel con los primos marcados; el kick recorre una onda por los indices.
# Recetario 30, ref. Max Cooper "Emergence" (espiral de Sacks). Circular: respeta el sello.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base53')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base53',
    shader='shaders/visuales/filotaxis.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.0),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Divergencia', 'u_firma', 130.0, 145.0, 137.508),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
