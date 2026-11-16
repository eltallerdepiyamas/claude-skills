# setup_base18_red_nodos.py: Red de Nodos (CH9 9-3). Plexus: nodos que derivan y se conectan; el kick abre el radio.
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)
B = op('/project2/base18')
for viejo in ('red', 'logo_in'):          # restos del visual anterior de esta base
    if B.op(viejo) is not None:
        B.op(viejo).destroy()

tdvj_core.build_visual(
    base='base18',
    shader='shaders/visuales/red_nodos.glsl',
    source=None,
    feedback=False,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.5),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Densidad', 'u_firma', 3.0, 16.0, 7.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
