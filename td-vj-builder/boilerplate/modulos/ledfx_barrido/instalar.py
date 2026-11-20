# ledfx_barrido — rampa con halo que barre la pantalla (venia del test de pantallas de Little Jesus, "glow"). v2.1
# (2026-11-20): RITMO libre / al tiempo / al compas (una pasada exacta por beat o compas, BPM detectado) / disparado
# por el kick, y brillo que sigue la energia. v2
# (2026-11-20): va en los slices de led_slices si existen (segunda capa sobre el visual), si no en la LED.
# Va en la cadena LED (led_cadena, orden 20, despues del chaser): fuente_led -> ... -> barrido_led -> lienzo_led.
# Formas: linea diagonal · circulo que se expande · barra horizontal · barra vertical.
# Recorre:
#   banner   = la rampa cruza los tableros como cuelgan (todos en una linea); en el mapeo apilado se ve
#              partida, en el LED se ve continua. Default.
#   pantalla = la rampa cruza la imagen del mapeo tal cual.
# Tinta: Color A / Color B de la paleta del show (/project2/show Colora*/Colorb*) o Blanco.
# Pagina Barrido de /project1/led: Barridoon (apagado por default) · Barridoforma · Barridovel · Barridoint ·
#   Barridotinta · Barridorecorre. Para medir pixeles con el pixel map, apagarlo.
# Migra el glow_led / pagina Glow de Casa Bacardi (2026-11-17) si existe. Requiere led_salida.
import json


def _host():
    """Donde va el efecto: slices (led_slices) si existe, si no la cadena LED (led_salida).
    proyecto.json -> "ledfx": {"en": "led"} lo fuerza a la LED."""
    try:
        pref = json.load(open(project.folder + '/proyecto.json', encoding='utf-8')).get('ledfx', {}).get('en', '')
    except Exception:
        pref = ''
    S_, L_ = op('/project1/slices'), op('/project1/led')
    s_ok = S_ is not None and S_.op('slices_cadena') is not None
    l_ok = L_ is not None and L_.op('led_cadena') is not None
    if pref == 'led' and l_ok:
        return L_, 'led'
    if s_ok:
        return S_, 'slices'
    if l_ok:
        return L_, 'led'
    return None, ''


B, MODO = _host()
CADENA = 'slices_cadena' if MODO == 'slices' else 'led_cadena'
PAGINAS = ['Salida', 'Efectos', 'Capa', 'Chaser', 'Barrido', 'EQ', 'Onda', 'Cascada', 'Giro', 'Respira', 'Slices', 'LED', 'Banner'] if MODO == 'slices' else ['LED', 'Chaser', 'Barrido', 'Banner']


def migrar(nombres):
    """Al pasar a slices: trae los valores que tenia el efecto en /project1/led (una sola vez)."""
    L_ = op('/project1/led')
    if MODO != 'slices' or L_ is None or B.fetch('ledfx_migrado_' + nombres[0], False, search=False):
        return []
    hechos = []
    for n in nombres:
        a, b = getattr(L_.par, n, None), getattr(B.par, n, None)
        if a is not None and b is not None and a.mode == ParMode.CONSTANT and not b.readOnly:
            b.val = a.eval()
            hechos.append(n)
    B.store('ledfx_migrado_' + nombres[0], True)
    return hechos
S = '/project2/show'

SHADER = r'''// barrido_led — rampa animada con halo, sumada encima de la cadena LED
uniform vec4 uGlow;     // x on · y forma · z velocidad · w intensidad
uniform vec4 uCfg;      // x espacio (0 banner, 1 pantalla) · y tiempo
uniform vec4 uTinta;    // rgb
uniform vec4 uGrid;     // x columnas, y filas (LED) · z 1 = slices (indice en la entrada 1)
uniform vec4 uRitmo;    // x fase (1 = una pasada completa) · y 1 = al beat (usa la fase) · z brillo por energia
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 src = texture(sTD2DInputs[0], uv);
    if (uGlow.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    float COLS = max(uGrid.x, 1.0);
    float ROWS = max(uGrid.y, 1.0);

    // P en unidades de "alto de tablero = 1"; W = ancho en esas unidades
    vec2 P; float W;
    if (uCfg.x < 0.5 && uGrid.z > 0.5) {               // SLICES en linea, en el orden del XML (indice en la entrada 1)
        vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
        if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
        W = max(m.g, 1.0);
        P = vec2(m.r + m.b, m.a);
    } else if (uCfg.x < 0.5) {
        float c = floor(uv.x * COLS);
        float rTop = ROWS - 1.0 - floor(uv.y * ROWS);       // fila de arriba primero
        float idx = rTop * COLS + c;
        vec2 lu = vec2(fract(uv.x * COLS), fract(uv.y * ROWS));
        P = vec2(idx + lu.x, lu.y);
        W = COLS * ROWS;
    } else {
        vec2 res = uTDOutputInfo.res.zw;
        W = res.x / max(res.y, 1.0);
        P = vec2(uv.x * W, uv.y);
    }

    int forma = int(uGlow.y + 0.5);
    float t = uCfg.y * clamp(uGlow.z, 0.0, 4.0);
    bool alBeat = uRitmo.y > 0.5;
    float fa = fract(uRitmo.x);                // posicion de la pasada si va al beat
    float dist;
    if (forma == 0) {                         // linea diagonal
        float ang = 0.55;
        float cs = cos(ang), sn = sin(ang);
        float d = P.x * cs + P.y * sn;
        float total = W * cs + sn;
        dist = d - ((alBeat ? fa : fract(t * 0.18)) * (total + 0.6) - 0.3);
    } else if (forma == 1) {                  // circulo expandiendo desde el centro
        float r = length(P - vec2(W * 0.5, 0.5));
        float maxR = sqrt(W * W * 0.25 + 0.25) + 0.1;
        dist = r - (alBeat ? fa : fract(t * 0.18)) * (maxR + 0.2);
    } else if (forma == 2) {                  // barra horizontal (sube)
        dist = P.y - ((alBeat ? fa : fract(t * 0.15)) * 1.6 - 0.3);
    } else {                                  // barra vertical (recorre de lado)
        dist = P.x - ((alBeat ? fa : fract(t * 0.15)) * (W + 0.6) - 0.3);
    }

    float core  = exp(-abs(dist) * 60.0);
    float halo  = exp(-abs(dist) * 6.0);
    float trail = smoothstep(0.0, 0.25, -dist) * exp(dist * 2.8);
    float pulse = 0.7 + 0.3 * sin(t * 2.6);

    vec3 tinta = uTinta.rgb;
    vec3 g = tinta * halo * 0.40 * pulse + tinta * trail * 0.50 + min(tinta * 1.8, vec3(1.0)) * core * 1.40;
    fragColor = TDOutputSwizzle(vec4(src.rgb + g * uGlow.w * uRitmo.z, 1.0));
}
'''

LIB_RITMO = r"""# barrido_lib — fase del barrido al beat (lo escribe modulos/ledfx_barrido; no editar aqui)
B = parent()


def _tempo():
    t = op('/project2/audio/tempo/tempo_lib')
    return t.module if t is not None else None


def kick(val, prev):
    if not (prev < B.par.Barridoumbral.eval() <= val):
        return
    n = B.fetch('ba_kicks', 0, search=False) + 1
    B.store('ba_kicks', n)
    if B.par.Barridoritmo.eval() == 'kick' and n % max(1, int(B.par.Barridocada.eval())) == 0:
        B.store('ba_t', absTime.seconds)


def fase():
    # 1 = una pasada completa. Libre: no se usa (el shader va con la Velocidad).
    modo = B.par.Barridoritmo.eval()
    cada = max(1, int(B.par.Barridocada.eval()))
    t = _tempo()
    bpm = t.bpm() if t is not None else 120.0
    if modo == 'tiempo' and t is not None:
        return t.fase() / cada
    if modo == 'compas' and t is not None:
        return t.fase() / (4.0 * cada)
    if modo == 'kick':
        dur = 60.0 / max(1.0, bpm) * 2.0                     # una pasada dura dos tiempos
        return min(0.999, (absTime.seconds - B.fetch('ba_t', -100.0, search=False)) / dur)
    return absTime.seconds * 0.5


def energia():
    if not B.par.Barridoaudio.eval():
        return 1.0
    m = op('/project2/audio/master_audio')
    try:
        e = float(m['low'].eval()) + float(m['kick'].eval())
    except Exception:
        return 1.0
    return 0.3 + 0.9 * max(0.0, min(1.0, e))
"""

# nombre nuevo <- nombre viejo (glow de Casa Bacardi)
MIGRA = (('Barridoon', 'Glowon'), ('Barridoforma', 'Glowforma'), ('Barridovel', 'Glowvel'),
         ('Barridoint', 'Glowint'), ('Barridotinta', 'Glowtinta'), ('Barridorecorre', 'Glowespacio'))


def nuevo(comp, tipo, nombre, x, y):
    o = comp.op(nombre)
    if o is None:
        o = comp.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def par(pg, kind, nombre, label, default=None, rango=None):
    if not hasattr(B.par, nombre):
        getattr(pg, 'append' + kind)(nombre, label=label)
        p = getattr(B.par, nombre)
        if default is not None:
            p.default = default
            p.val = default
    p = getattr(B.par, nombre)
    if rango:
        p.normMin, p.normMax = rango
    return p


if B is None:
    print('[fallo] barrido: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    viejos = {v: getattr(B.par, v).eval() for _, v in MIGRA if hasattr(B.par, v)}
    pg = next((p for p in B.customPages if p.name == 'Barrido'), None) or B.appendCustomPage('Barrido')
    par(pg, 'Toggle', 'Barridoon', 'Barrido prendido', False)
    p = par(pg, 'Menu', 'Barridoforma', 'Forma')
    p.menuNames = ['linea', 'circulo', 'horizontal', 'vertical']
    p.menuLabels = ['Linea diagonal', 'Circulo expandiendo', 'Barra horizontal', 'Barra vertical']
    par(pg, 'Float', 'Barridovel', 'Velocidad', 1.0, (0.0, 3.0))
    par(pg, 'Float', 'Barridoint', 'Intensidad', 1.0, (0.0, 2.0))
    p = par(pg, 'Menu', 'Barridotinta', 'Tinta')
    p.menuNames = ['a', 'b', 'blanco']
    p.menuLabels = ['Color A (paleta)', 'Color B (paleta)', 'Blanco']
    p = par(pg, 'Menu', 'Barridorecorre', 'Recorre')
    p.menuNames = ['banner', 'pantalla']
    p.menuLabels = ['Tableros / slices en linea (en orden)', 'Imagen completa (la pantalla)']
    p = par(pg, 'Menu', 'Barridoritmo', 'Ritmo')
    _v = p.eval()
    p.menuNames = ['libre', 'tiempo', 'compas', 'kick']
    p.menuLabels = ['Libre (Velocidad)', 'Al tiempo (una pasada por beat)', 'Al compas (una por compas)',
                    'Disparado por el kick']
    p.val = _v if _v in p.menuNames else 'libre'
    par(pg, 'Int', 'Barridocada', 'Una pasada cada N (tiempos / compases / kicks)', 1, (1, 8))
    par(pg, 'Float', 'Barridoumbral', 'Umbral del kick', 0.5, (0.05, 1.0))
    par(pg, 'Toggle', 'Barridoaudio', 'Brillo sigue la energia', False)
    pg.sort('Barridoon', 'Barridoforma', 'Barridovel', 'Barridoint', 'Barridotinta', 'Barridorecorre')
    # migracion del glow: valores a los nombres nuevos, fuera la pagina Glow y sus nodos
    for nuevo_n, viejo_n in MIGRA:
        if viejo_n in viejos:
            getattr(B.par, nuevo_n).val = viejos[viejo_n]
    for g in [p for p in B.customPages if p.name == 'Glow']:
        g.destroy()
    for n in ('glow_led', 'glow_led_pixel'):
        if B.op(n) is not None:
            B.op(n).destroy()

    migrados = migrar(['Barridoon', 'Barridoforma', 'Barridovel', 'Barridoint', 'Barridotinta', 'Barridorecorre'])
    dat = nuevo(B, textDAT, 'barrido_led_pixel', 1000, 500)
    dat.text = SHADER
    g = nuevo(B, glslTOP, 'barrido_led', 1000, 400)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.par.format = 'rgba16float'
    g.seq.vec.numBlocks = 5
    g.par.vec0name = 'uGlow'
    g.par.vec0valuex.expr = 'int(parent().par.Barridoon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Barridoforma.menuIndex'
    g.par.vec0valuez.expr = 'parent().par.Barridovel'
    g.par.vec0valuew.expr = 'parent().par.Barridoint'
    g.par.vec1name = 'uCfg'
    g.par.vec1valuex.expr = 'parent().par.Barridorecorre.menuIndex'
    g.par.vec1valuey.expr = 'absTime.seconds'
    g.par.vec2name = 'uTinta'
    for c, k in (('r', 'x'), ('g', 'y'), ('b', 'z')):
        getattr(g.par, 'vec2value' + k).expr = (
            "[op('%s').par.Colora%s, op('%s').par.Colorb%s, 1.0][parent().par.Barridotinta.menuIndex] "
            "if hasattr(op('%s').par, 'Colora%s') else 1.0" % (S, c, S, c, S, c))
    g.par.vec3name = 'uGrid'
    if MODO == 'slices':                     # uGrid.z = 1: la posicion sale del indice de led_slices (entrada 1)
        g.par.vec3valuex.expr, g.par.vec3valuey.expr = '', ''
        g.par.vec3valuex.mode = g.par.vec3valuey.mode = ParMode.CONSTANT
        g.par.vec3valuex, g.par.vec3valuey, g.par.vec3valuez = 1, 1, 1
    else:
        g.par.vec3valuex.expr, g.par.vec3valuey.expr = 'parent().par.Columnas', 'parent().par.Filas'
        g.par.vec3valuez = 0
    lb = nuevo(B, textDAT, 'barrido_lib', 1000, 650)
    lb.text = LIB_RITMO
    kk = nuevo(B, selectCHOP, 'barrido_kick', 1200, 650)
    kk.par.chops = '/project2/audio/master_audio'
    kk.par.channames = 'kick'
    kx = nuevo(B, chopexecuteDAT, 'barrido_kick_exec', 1200, 800)
    kx.par.chop = kk.name
    for pn in ('channels', 'channel'):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = 'kick'
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False), ('whileon', False), ('whileoff', False)):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = v
    kx.text = "def onValueChange(channel, sampleIndex, val, prev):\n    op('barrido_lib').module.kick(val, prev)\n    return\n"
    g.par.vec4name = 'uRitmo'
    g.par.vec4valuex.expr = "op('barrido_lib').module.fase() if absTime.frame >= 0 else 0"
    g.par.vec4valuey.expr = "1 if parent().par.Barridoritmo.eval() != 'libre' else 0"
    g.par.vec4valuez.expr = "op('barrido_lib').module.energia() if absTime.frame >= 0 else 1"
    g.tags.add('ledfx')
    g.store('orden', 20)
    cadena = B.op(CADENA).module.encadenar()
    g.cook(force=True)
    print('[ok] ledfx_barrido | cadena %s | prendido=%s forma=%s tinta=%s recorre=%s%s' % (
        cadena, B.par.Barridoon.eval(), B.par.Barridoforma.eval(), B.par.Barridotinta.eval(),
        B.par.Barridorecorre.eval(), ' | migrado del glow' if viejos else ''))
    e = g.errors() or g.warnings()
    if e:
        print('[aviso] barrido_led:', e)
    # legibilidad: secciones con titulo (modulos/secciones.py)
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    secciones(B, 'Barrido', [('Hbarrido', 'Barrido', ['Barridoon', 'Barridoforma', 'Barridorecorre']),
                             ('Hbaritmo', 'Ritmo', ['Barridoritmo', 'Barridocada', 'Barridoumbral', 'Barridoaudio']),
                             ('Hbalook', 'Como se ve', ['Barridovel', 'Barridoint', 'Barridotinta'])])
    orden_paginas(B, PAGINAS)
