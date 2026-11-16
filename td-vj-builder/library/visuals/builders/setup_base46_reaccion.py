# setup_base46_reaccion.py: Reaccion (CH9). Reaccion-difusion Gray-Scott que crece como coral; el kick siembra.
# Red: vacio (U=1) -> fb -> sim1..sim6 (reaccion_sim.glsl, 960x540 float) -> out1 -> reaccion.glsl la pinta.
# Para rehacer la red: borrar base46/red. RESET del show reinicia el feedback (la red vuelve a vacio).
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)

W, H = 960, 540
PASOS = 6                     # pasos de simulacion por cuadro (mas = crece mas rapido)
fuente = '/project2/base46/red/out1'
if op('/project2/base46/red') is None:
    b, r = rn.base(46)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'sim_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    frag.text = open(project.folder + '/shaders/visuales/reaccion_sim.glsl', encoding='utf-8').read().lstrip('\ufeff')   # Drive no siempre avisa del cambio; TD a veces mete BOM
    vacio = rn.nodo(r, td.constantTOP, 'vacio', outputresolution='custom', resolutionw=W, resolutionh=H,
                    format='rgba32float', colorr=1, colorg=0, colorb=0, alpha=1)
    fb = rn.nodo(r, td.feedbackTOP, 'fb', [vacio])
    prev = fb
    # siembra: cada kick (o cada 1.3 s en silencio) pone un foco en un lugar al azar
    semilla = "int(absTime.seconds * 4)"
    toca ="(1.0 if op('audio')['kick'] > 0.5 or absTime.frame % 40 == 0 else 0.0)"
    for i in range(1, PASOS + 1):
        s = rn.nodo(r, td.glslTOP, 'sim%d' % i, [prev], pixeldat='sim_frag', format='rgba32float',
                    outputresolution='custom', resolutionw=W, resolutionh=H)
        for d in list(s.docked):
            d.destroy()
        siembra = ['tdu.rand(%s)' % semilla, 'tdu.rand(%s + 77)' % semilla, 0.02, toca] if i == 1 else [0, 0, 0, 0]
        tdvj_core.bind_vectors(s, [
            ('u_patron', ['parent(2).par.Patron']),
            ('u_bass', ["op('audio')['low'] * parent(2).par.Audiomult"]),
            ('u_warp', ['parent(2).par.Warp']),
            ('u_dt', ['min(max(parent(2).par.Speed, 0.05), 1.0)']),
            ('u_seed', siembra),
        ])
        prev = s
    fb.par.top = 'sim%d' % PASOS
    fuente = rn.salida(r, prev)

tdvj_core.build_visual(
    base='base46',
    shader='shaders/visuales/reaccion.glsl',
    source=fuente,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 1.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.3),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Patron', 'u_firma', 0.0, 1.0, 0.5),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
