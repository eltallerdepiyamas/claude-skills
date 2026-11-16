# setup_base44_laser.py: Laser (CH9). Haces en humo con estela; cada kick cambia la figura (Pagina Secuencia).
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)

tdvj_core.build_visual(
    base='base44',
    shader='shaders/visuales/laser.glsl',
    source=None,
    feedback=True,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Haces', 'u_firma', 1.0, 24.0, 9.0),
    ],
    signature_extras=[('Estela', 'u_estela', 0.6, 0.97, 0.86)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
