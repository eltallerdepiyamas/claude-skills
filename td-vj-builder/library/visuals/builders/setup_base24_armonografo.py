# setup_base24_armonografo.py: Armonografo (CH9 9-8). Plumas que dibujan curvas de armonografo 3D con estela larga.
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base24')
for viejo in ('red', 'logo_in'):          # restos del visual anterior de esta base
    if B.op(viejo) is not None:
        B.op(viejo).destroy()

tdvj_core.build_visual(
    base='base24',
    shader='shaders/visuales/armonografo.glsl',
    source=None,
    feedback=True,
    extra=lambda comp: [('u_paso', ['absTime.stepSeconds'])],
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.4),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Plumas', 'u_firma', 1.0, 6.0, 3.0),
    ],
    signature_extras=[('Estela', 'u_estela', 0.9, 0.999, 0.994)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
