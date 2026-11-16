# setup_base26_cimatica.py: Cimatica (CH10 10-8). Placa de Chladni circular: la arena dibuja los nodos; el kick cambia el modo.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)
B = op('/project2/base26')
if B.op('logo_in') is not None:
    B.op('logo_in').destroy()
if B.op('red') is not None:
    B.op('red').destroy()

tdvj_core.build_visual(
    base='base26',
    shader='shaders/visuales/cimatica.glsl',
    source=None,
    feedback=True,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Complejidad', 'u_firma', 2.0, 14.0, 7.0),
    ],
    signature_extras=[('Estela', 'u_estela', 0.5, 0.98, 0.85)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
