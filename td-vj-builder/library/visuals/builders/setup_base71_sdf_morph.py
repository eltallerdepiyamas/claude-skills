# setup_base71_sdf_morph.py: SDF Morph (CH8). Isolineas finas de una forma SDF que pasa de circulo a anillo, cruz y rombo con cada kick.
# Recetario 22, ref. Inigo Quilez (distance functions 2D) / Shader Park. Los bajos engrosan las lineas.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base71')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base71',
    shader='shaders/visuales/sdf_morph.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Isolineas', 'u_firma', 4.0, 40.0, 14.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
