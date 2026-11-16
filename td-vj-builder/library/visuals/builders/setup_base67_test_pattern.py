# setup_base67_test_pattern.py: Test Pattern (CH8). Reticula de datos tipo test pattern: celdas modulo, contadores de 7 segmentos, marcas de registro.
# Recetarios 1 y 3, ref. Ryoji Ikeda "test pattern" / Alva Noto "unitxt" (raster-noton). Kick = pagina nueva; agudos = titileo.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base67')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base67',
    shader='shaders/visuales/test_pattern.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.25),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Densidad', 'u_firma', 8.0, 48.0, 20.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
