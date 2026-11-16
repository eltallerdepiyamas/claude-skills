# setup_base72_crt.py: CRT (CH8). Osciladores de video (rejilla) vistos en un CRT: ancho de banda, scanlines, barra de rolado; el kick salta la sincronia.
# Recetarios 36 y 43, ref. LZX Industries (Prismatic Ray, DWO3) / Basement Vibes ANALOG_TV. CRT sutil, sin VHS de colores.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base72')
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base72',
    shader='shaders/visuales/crt.glsl',
    source=None,
    feedback=False,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.35),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Anchobanda', 'u_firma', 0.0, 16.0, 5.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
