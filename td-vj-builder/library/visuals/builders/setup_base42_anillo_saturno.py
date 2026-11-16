# setup_base42_anillo_saturno.py: Anillo Saturno (CH10 10-16). Anillo planetario de polvo con divisiones; el kick lanza una onda espiral.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)
B = op('/project2/base42')
if B.op('logo_in') is not None:
    B.op('logo_in').destroy()
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base42',
    shader='shaders/visuales/anillo_saturno.glsl',
    source=None,
    feedback=False,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.45),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Finura', 'u_firma', 20.0, 400.0, 160.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
