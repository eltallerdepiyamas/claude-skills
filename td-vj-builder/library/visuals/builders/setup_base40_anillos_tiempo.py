# setup_base40_anillos_tiempo.py: Anillos de Tiempo (CH10 10-15). Cordillera en polar: centro = ahora, afuera = el pasado del track.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)
B = op('/project2/base40')
if B.op('logo_in') is not None:
    B.op('logo_in').destroy()
# red: historia del audio 1 x 128 (la misma de Cordillera, cordillera_hist.glsl). Para rehacerla: borrar base40/red.
fuente = '/project2/base40/red/out1'
if B.op('red') is not None and B.op('red/historia') is None:
    B.op('red').destroy()                  # red de otro visual
if B.op('red') is None:
    b, r = rn.base(40)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'hist_frag')
    frag.text = open(project.folder + '/shaders/visuales/cordillera_hist.glsl', encoding='utf-8').read().lstrip('\ufeff')
    vacio = rn.nodo(r, td.constantTOP, 'vacio', outputresolution='custom', resolutionw=1, resolutionh=128,
                    format='rgba32float', colorr=0, colorg=0, colorb=0, alpha=0)
    fb = rn.nodo(r, td.feedbackTOP, 'fb', [vacio])
    h = rn.nodo(r, td.glslTOP, 'historia', [fb], pixeldat='hist_frag', format='rgba32float',
                outputresolution='custom', resolutionw=1, resolutionh=128)
    for d in list(h.docked):
        d.destroy()
    fb.par.top = 'historia'
    tdvj_core.bind_vectors(h, [('u_now', ["op('audio')['%s'] * parent(2).par.Audiomult" % ch
                                          for ch in ('low', 'mid', 'high', 'kick')])])
    fuente = rn.salida(r, h)

tdvj_core.build_visual(
    base='base40',
    shader='shaders/visuales/anillos_tiempo.glsl',
    source=fuente,
    feedback=False,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Anillos', 'u_firma', 8.0, 60.0, 32.0),
    ],
    signature_extras=[],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
