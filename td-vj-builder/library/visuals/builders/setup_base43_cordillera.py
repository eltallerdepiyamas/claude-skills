# setup_base43_cordillera.py: Cordillera (CH9). Ridgeline del track: enfrente el audio de ahora, atras su historia.
# Red: historia de audio de 1 x 128 con feedback (cordillera_hist.glsl) -> entra al shader principal.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)

fuente = '/project2/base43/red/out1'
if op('/project2/base43/red') is None:
    b, r = rn.base(43)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'hist_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    frag.text = open(project.folder + '/shaders/visuales/cordillera_hist.glsl', encoding='utf-8').read().lstrip('\ufeff')   # Drive no siempre avisa del cambio; TD a veces mete BOM
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
    base='base43',
    shader='shaders/visuales/cordillera.glsl',
    source=fuente,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Lineas', 'u_firma', 12.0, 90.0, 48.0),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
