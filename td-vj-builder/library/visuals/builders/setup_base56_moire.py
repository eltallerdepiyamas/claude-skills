# setup_base56_moire.py: Moire (CH8). Interferencia de dos familias de anillos finos; el bajo separa los centros.
# Recetario 34, ref. raster-noton / Carsten Nicolai. Circular: dentro del disco del sello.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base56')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base56',
    shader='shaders/visuales/moire.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.5),
        ('Warp', 'u_warp', 0.0, 1.0, 0.2),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Diferencia', 'u_firma', 0.0, 0.2, 0.03),
    ],
    signature_extras=[('Densidad', 'u_densidad', 40.0, 260.0, 140.0)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
