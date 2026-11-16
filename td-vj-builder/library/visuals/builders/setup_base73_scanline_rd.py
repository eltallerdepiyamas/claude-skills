# setup_base73_scanline_rd.py: Scanline RD (CH8). Reaccion-difusion por renglones: un renglon nuevo por cuadro (depende del anterior) con feedback; textura de tejido.
# Recetario 44, ref. Basement Vibes "Scanline Reaction Diffusion". Un pase + feedback: el estado vive en el pixel central de cada celda.
# feedback=True: feedback1 (cuadro anterior) entra en sTD2DInputs[0]; Reset estela lo limpia.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base73')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base73',
    shader='shaders/visuales/scanline_rd.glsl',
    source=None,
    feedback=True,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Patron', 'u_firma', 0.0, 1.0, 0.5),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
