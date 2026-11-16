# setup_base66_marmol.py: Marmol (CH8). Vetas de marmol/humo por domain warping; el bajo empuja el warp, el kick enciende una veta.
# Recetario 12, ref. Inigo Quilez (domain warping fbm(p + fbm(p + fbm(p)))). Solo isolineas finas del campo, negro domina.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base66')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base66',
    shader='shaders/visuales/marmol.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.45),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Torsion', 'u_firma', 0.0, 3.0, 1.2),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
