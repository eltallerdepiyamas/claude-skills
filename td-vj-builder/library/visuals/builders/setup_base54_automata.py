# setup_base54_automata.py: Automata (CH8). Automata celular 1D; la historia baja, el kick siembra / cambia de regla.
# Recetarios 2 y 41, ref. Ryoji Ikeda (test pattern) / LZX Castle.
# Red: vacio -> fb -> ca (automata_sim.glsl, 240x135 rgba32float: celdas de 8x8 px a 1080p) -> out1 -> automata.glsl la pinta.
# Para rehacer la red: borrar base54/red. RESET del show reinicia el feedback (la red vuelve a vacio).
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)

W, H = 240, 135
STEP = ("float(parent(2).par.Step) if parent(2).par.Stepmode.eval() == 'kick' "
        "else float(math.floor(absTime.seconds * parent(2).par.Bpm / 60.0))")
fuente = '/project2/base54/red/out1'
if op('/project2/base54/red') is None:
    b, r = rn.base(54)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'sim_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    frag.text = open(project.folder + '/shaders/visuales/automata_sim.glsl', encoding='utf-8').read().lstrip('﻿')
    vacio = rn.nodo(r, td.constantTOP, 'vacio', outputresolution='custom', resolutionw=W, resolutionh=H,
                    format='rgba32float', colorr=0, colorg=0, colorb=0, alpha=0)
    fb = rn.nodo(r, td.feedbackTOP, 'fb', [vacio])
    s = rn.nodo(r, td.glslTOP, 'ca', [fb], pixeldat='sim_frag', format='rgba32float',
                outputresolution='custom', resolutionw=W, resolutionh=H)
    for d in list(s.docked):
        d.destroy()
    tdvj_core.bind_vectors(s, [
        ('u_time', ['absTime.seconds']),
        ('u_rate', ['20.0 * parent(2).par.Speed']),
        ('u_regla', ['parent(2).par.Regla']),
        ('u_variar', ['parent(2).par.Variar']),
        ('u_step', [STEP]),
        ('u_mut', ["0.0015 + 0.02 * op('audio')['high'] * parent(2).par.Audiomult"]),
    ])
    fb.par.top = 'ca'
    fuente = rn.salida(r, s)

tdvj_core.build_visual(
    base='base54',
    shader='shaders/visuales/automata.glsl',
    source=fuente,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 1.0),
        ('Warp', 'u_warp', 0.0, 1.0, 0.0),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Regla', 'u_firma', 0.0, 255.0, 30.0),
    ],
    signature_extras=[('Variar', 'u_variar', 0.0, 1.0, 0.0)],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
