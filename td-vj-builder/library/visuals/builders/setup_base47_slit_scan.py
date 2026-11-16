# setup_base47_slit_scan.py: Slit Scan (CH9). Cintas de luz estiradas en el tiempo: cada franja es otro instante.
# Red: fuente (slit_scan_src.glsl) -> historia (Texture 3D, 64 cuadros) -> Time Machine con mapa
# (slit_scan_mapa.glsl) -> out1 -> slit_scan.glsl la pinta con la paleta. Mismo truco que Time Glitch (base3).
import sys, importlib
import td
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import rig, tdvj_core, red_nodos as rn
importlib.reload(rig)
importlib.reload(tdvj_core)
importlib.reload(rn)

W, H = 1280, 720


def glsl(r, nombre, archivo, entradas=()):
    d = rn.nodo(r, td.textDAT, nombre + '_frag')
    # texto directo, sin syncfile: TD reescribe el archivo con BOM. Shader nuevo = borrar red y correr esto.
    d.text = open(project.folder + '/shaders/visuales/' + archivo, encoding='utf-8').read().lstrip('\ufeff')
    g = rn.nodo(r, td.glslTOP, nombre, entradas, pixeldat=nombre + '_frag', format='rgba16float',
                outputresolution='custom', resolutionw=W, resolutionh=H)
    for x in list(g.docked):
        x.destroy()
    return g


def unis(g, specs):
    tdvj_core.bind_vectors(g, [(n, [e]) for n, e in specs])


fuente = '/project2/base47/red/out1'
if op('/project2/base47/red') is None:
    b, r = rn.base(47)
    rn.audio(r)
    src = glsl(r, 'fuente', 'slit_scan_src.glsl')
    unis(src, [('u_time', 'absTime.seconds'), ('u_low', "op('audio')['low'] * parent(2).par.Audiomult"),
               ('u_kick', "op('audio')['kick']"), ('u_speed', 'parent(2).par.Speed')])
    t3 = rn.nodo(r, td.texture3dTOP, 'historia', [src], cachesize=64)
    mapa = glsl(r, 'mapa', 'slit_scan_mapa.glsl')
    unis(mapa, [('u_time', 'absTime.seconds'), ('u_warp', 'parent(2).par.Warp'),
                ('u_retraso', 'parent(2).par.Retraso'), ('u_kick', "op('audio')['kick']")])
    tm = rn.nodo(r, td.timemachineTOP, 'tiempo', [t3, mapa])
    fuente = rn.salida(r, tm)

tdvj_core.build_visual(
    base='base47',
    shader='shaders/visuales/slit_scan.glsl',
    source=fuente,
    five_slots=[
        ('Intensity', 'u_intensity', 0.0, 2.0, 1.0),
        ('Speed', 'u_speed', 0.0, 3.0, 0.8),
        ('Warp', 'u_warp', 0.0, 1.0, 0.0),
        ('Tono', 'u_tono', 0.0, 1.0, 0.0),
        ('Retraso', 'u_firma', 0.0, 1.0, 0.8),
    ],
    color_uniforms=[
        ('Color1', 'u_color1', (1.0, 0.12, 0.22)),
        ('Color2', 'u_color2', (0.43, 0.77, 0.60)),
        ('Color3', 'u_color3', (0.0, 0.0, 0.0)),
    ],
)
