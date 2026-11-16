# setup_base50_physarum.py: Physarum (CH8). Red de venas viva (slime mold); el kick la hace respirar. Recetario 9, ref. Sage Jenson.
# Red: vacio (masa 1, sin rastro) -> fb -> girar1/mover1 ... girarN/moverN (physarum_sim.glsl, 960x540 float) -> out1
# -> physarum.glsl la pinta. Para rehacer la red: borrar base50/red. RESET del show reinicia el feedback.
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
PASOS = 3                     # pares girar/mover por cuadro (mas = la red se arma mas rapido, cuesta mas)
fuente = '/project2/base50/red/out1'
if op('/project2/base50/red') is None:
    b, r = rn.base(50)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'sim_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    frag.text = open(project.folder + '/shaders/visuales/physarum_sim.glsl', encoding='utf-8').read().lstrip('﻿')
    # masa 1 en cada celda, rastro 0, direccion (1, 0): el primer paso le da un rumbo al azar a cada celda
    vacio = rn.nodo(r, td.constantTOP, 'vacio', outputresolution='custom', resolutionw=W, resolutionh=H,
                    format='rgba32float', colorr=0, colorg=1, colorb=1, alpha=1)   # alpha 1: el Constant premultiplica y con 0 la masa quedaba en 0
    fb = rn.nodo(r, td.feedbackTOP, 'fb', [vacio])
    prev = fb
    for i in range(1, PASOS + 1):
        for fase, nombre in ((0, 'girar%d' % i), (1, 'mover%d' % i)):
            s = rn.nodo(r, td.glslTOP, nombre, [prev], pixeldat='sim_frag', format='rgba32float',
                        outputresolution='custom', resolutionw=W, resolutionh=H)
            for d in list(s.docked):
                d.destroy()
            tdvj_core.bind_vectors(s, [
                ('u_pass', [fase]),
                ('u_time', ['absTime.seconds + %0.3f' % (i * 0.37 + fase * 0.11)]),
                ('u_paso', ['tdu.clamp(0.25 + 0.75 * parent(2).par.Speed, 0.05, 1.0)']),
                ('u_giro', ['0.15 + 0.85 * parent(2).par.Warp']),
                ('u_sensor', ['0.2 + 0.9 * parent(2).par.Ramificacion']),
                ('u_dist', ['14.0 - 7.0 * parent(2).par.Ramificacion']),
                ('u_deposito', ["0.05 + 0.12 * op('audio')['low'] * parent(2).par.Audiomult"]),
                ('u_decay', ['parent(2).par.Estela']),
                ('u_kick', ["op('audio')['kick']"]),
                ('u_jitter', ["0.15 + 0.6 * op('audio')['high'] * parent(2).par.Audiomult"]),
            ])
            prev = s
    fb.par.top = prev.name
    fuente = rn.salida(r, prev)

tdvj_core.build_visual(
    base='base50',
    shader='shaders/visuales/physarum.glsl',
    source=fuente,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 1.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.35),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Ramificacion', 'u_firma', 0.0, 1.0, 0.3),
    ],
    signature_extras=[('Estela', 'u_estela', 0.8, 0.97, 0.9)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
