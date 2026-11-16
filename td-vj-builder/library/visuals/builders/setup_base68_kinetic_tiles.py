# setup_base68_kinetic_tiles.py: Kinetic Tiles (CH8). Reticula de tiles Truchet que giran/voltean; el kick lanza una ola de volteo desde el centro.
# Recetario 28, ref. Matthew Ragan (instancing) / tutorial Ikeda de Jack DiLaura. En shader (un pase): orientacion por hash + Step.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base68')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base68',
    shader='shaders/visuales/kinetic_tiles.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Tamano', 'u_firma', 24.0, 160.0, 64.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
