# setup_base52_atractor.py: Atractor (CH8). Atractor de Clifford acumulado en feedback; el kick cambia de rama.
# Recetario 14, ref. Max Cooper / Refik Anadol (nubes de puntos finos).
# Red: orbita (atractor_orbita.glsl, N x 1 rgba32float: N puntos nuevos por cuadro) -> out1 -> atractor.glsl
# (entrada 0) los suma a la memoria (feedback, entrada 1). Para rehacer la red: borrar base52/red.
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)

N = 256                       # puntos nuevos por cuadro (cada pixel recorre los N: sube o baja segun la GPU)
fuente = '/project2/base52/red/out1'
if op('/project2/base52/red') is None:
    b, r = rn.base(52)
    rn.audio(r)
    frag = rn.nodo(r, td.textDAT, 'orbita_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    frag.text = open(project.folder + '/shaders/visuales/atractor_orbita.glsl', encoding='utf-8').read().lstrip('﻿')
    g = rn.nodo(r, td.glslTOP, 'orbita', [], pixeldat='orbita_frag', format='rgba32float',
                outputresolution='custom', resolutionw=N, resolutionh=1)
    for d in list(g.docked):
        d.destroy()
    tdvj_core.bind_vectors(g, [
        ('u_frame', ['absTime.frame']),
        ('u_time', ['absTime.seconds']),
        ('u_speed', ['parent(2).par.Speed']),
        ('u_warp', ['parent(2).par.Warp']),
        ('u_low', ["op('audio')['low'] * parent(2).par.Audiomult"]),
        ('u_forma', ['parent(2).par.Atractor']),
        ('u_step', ["float(parent(2).par.Step) if parent(2).par.Stepmode.eval() == 'kick' "
                    "else float(math.floor(absTime.seconds * parent(2).par.Bpm / 60.0))"]),
        ('u_cada', ['parent(2).par.Cada']),
    ])
    fuente = rn.salida(r, g)

tdvj_core.build_visual(
    base='base52',
    shader='shaders/visuales/atractor.glsl',
    source=fuente,
    feedback=True,
    extra=tdvj_core.kick_step,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.6),
        ('Warp', 'u_warp', 0.0, 1.0, 0.4),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Atractor', 'u_firma', 0.0, 1.0, 0.0),
    ],
    signature_extras=[
        ('Estela', 'u_estela', 0.9, 0.995, 0.985),
        ('Cada', 'u_cada', 1.0, 16.0, 4.0),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
