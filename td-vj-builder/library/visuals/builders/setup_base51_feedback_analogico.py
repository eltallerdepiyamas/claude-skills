# setup_base51_feedback_analogico.py: Feedback Analogico (CH8). Loop de video con frame delay y ganancia negativa en el kick.
# Recetario 40, ref. Hypno / Andrei Jay VIDEO_WAAAVES / LZX Memory Palace.
# glsl1 <- feedback1 (cuadro anterior, entrada 0) y <- eco (entrada 1): feedback1 -> historia (Texture 3D, 16 cuadros
# a 960x540) -> Time Machine con un mapa constante = Retardo/15 -> cuadro de hace N. Sin ciclo: el Feedback TOP corta el loop.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core
importlib.reload(rig)
importlib.reload(tdvj_core)

CACHE = 16
B = op('/project2/base51')
if B.op('red') is not None:
    B.op('red').destroy()


def _pon(o, nombre, valor):
    p = getattr(o.par, nombre, None)
    if p is None:
        tdvj_core.warn('%s no tiene el parametro %s' % (o.path, nombre))
        return
    if isinstance(valor, str) and valor.startswith('='):
        p.expr = valor[1:]
    else:
        p.val = valor


def extra(comp):
    specs = tdvj_core.kick_step(comp)          # u_step: la ganancia negativa dura una vuelta por kick
    fb = comp.op('feedback1')
    g = comp.op('glsl1')
    hist = tdvj_core.new_op(comp, td.texture3dTOP, 'historia', -200, -450)
    hist.inputConnectors[0].connect(fb)
    for n, v in (('cachesize', CACHE), ('outputresolution', 'custom'), ('resolutionw', 960),
                 ('resolutionh', 540), ('format', 'rgba16float')):
        _pon(hist, n, v)
    mapa = tdvj_core.new_op(comp, td.constantTOP, 'mapa_retardo', -200, -600)
    for n, v in (('outputresolution', 'custom'), ('resolutionw', 960), ('resolutionh', 540),
                 ('colorr', '=tdu.clamp(parent().par.Retardo / %0.1f, 0.0, 1.0)' % (CACHE - 1)),
                 ('colorg', '=tdu.clamp(parent().par.Retardo / %0.1f, 0.0, 1.0)' % (CACHE - 1)),
                 ('colorb', '=tdu.clamp(parent().par.Retardo / %0.1f, 0.0, 1.0)' % (CACHE - 1)),
                 ('alpha', 1)):
        _pon(mapa, n, v)
    eco = tdvj_core.new_op(comp, td.timemachineTOP, 'eco', 0, -450)
    eco.inputConnectors[0].connect(hist)
    eco.inputConnectors[1].connect(mapa)
    g.inputConnectors[1].connect(eco)
    return specs


tdvj_core.build_visual(
    base='base51',
    shader='shaders/visuales/feedback_analogico.glsl',
    source=None,
    feedback=True,
    extra=extra,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.7),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Retardo', 'u_firma', 1.0, 15.0, 6.0),
    ],
    signature_extras=[
        ('Ganancia', 'u_ganancia', 0.8, 0.98, 0.93),
        ('Negativo', 'u_negativo', 0.0, 1.0, 0.6),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
