# ledfx_chaser — chaser por tableros en la salida LED (idea del Chaser de Resolume, hecho en TD).
# Va en la cadena LED (led_cadena, orden 10): fuente_led -> chaser_led -> (barrido) -> lienzo_led.
# Cada tablero tiene una "luz" que prende y se apaga encima del visual, en el orden en que cuelgan (fila de
# arriba primero, todos en una linea). Lo apagado queda en Fondo (0 = negro, 1 = sin efecto).
# Patrones: corrida · ida y vuelta · centro -> afuera · afuera -> centro · pares / impares · aleatorio ·
#           acumular · todos (golpe completo). Sirve para cualquier Columnas x Filas de led_mapeo.
# Avanza: BPM detectado (modulo audio_tempo: sigue en los breaks, se engancha al kick), cada N kicks
# (canal kick de /project2/audio/master_audio) o BPM fijo. Ataque minimo para que no sea strobe.
# Pagina Chaser de /project1/led. Apagado por default. Requiere led_salida (audio_tempo opcional).
B = op('/project1/led')
AUDIO = '/project2/audio/master_audio'

SHADER = r'''// chaser_led — luz por tablero, secuenciada por pasos
uniform vec4 uCh;      // x on · y patron · z ancho (tableros) · w fondo
uniform vec4 uPaso;    // x paso · y segundos desde el paso · z segundos entre pasos · w decaimiento (s)
uniform vec4 uAtq;     // x ataque (s)
uniform vec4 uGrid;    // x columnas, y filas
out vec4 fragColor;

float COLS, ROWS, N;

float hash(float a, float b) { return fract(sin(a * 12.9898 + b * 78.233) * 43758.5453); }
float md(float a, float b) { return a - b * floor(a / b); }

float prendido(int pat, float s, float p, float w) {
    if (s < 0.0) return 0.0;
    if (pat == 0) {                                   // corrida A1 -> C4
        return md(s - p, N) < w ? 1.0 : 0.0;
    } else if (pat == 1) {                            // ida y vuelta
        float per = 2.0 * (N - 1.0);
        float q = md(s, per);
        float pos = q < N ? q : per - q;
        return abs(p - pos) < w * 0.5 + 0.01 ? 1.0 : 0.0;
    } else if (pat == 2 || pat == 3) {                // centro -> afuera / afuera -> centro (anillos simetricos)
        float anillos = ceil(N * 0.5);
        float r = floor(abs(p - (N - 1.0) * 0.5) + 0.25);
        if (pat == 3) r = anillos - 1.0 - r;
        return md(s - r, anillos) < w ? 1.0 : 0.0;
    } else if (pat == 4) {                            // pares / impares
        return md(p + s, 2.0) < 0.5 ? 1.0 : 0.0;
    } else if (pat == 5) {                            // aleatorio: ~ancho tableros por paso
        return hash(s, p) < w / N ? 1.0 : 0.0;
    } else if (pat == 6) {                            // acumular y volver a empezar
        return p < md(s, N + 1.0) ? 1.0 : 0.0;
    }
    return 1.0;                                       // todos
}

void main() {
    vec2 uv = vUV.st;
    vec4 src = texture(sTD2DInputs[0], uv);
    if (uCh.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    COLS = max(uGrid.x, 1.0);
    ROWS = max(uGrid.y, 1.0);
    N = COLS * ROWS;

    float c = floor(uv.x * COLS);
    float rTop = ROWS - 1.0 - floor(uv.y * ROWS);       // fila de arriba primero
    float p = rTop * COLS + c;                          // posicion en el banner colgado (0..N-1)

    int pat = int(uCh.y + 0.5);
    float w = max(1.0, floor(uCh.z + 0.5));
    float dec = max(uPaso.w, 0.01);
    float dur = max(uPaso.z, 0.05);
    float nivel = 0.0;
    for (int k = 0; k < 8; k++) {
        float edad = uPaso.y + float(k) * dur;
        float e = exp(-edad / dec);
        if (k == 0) e *= smoothstep(0.0, max(uAtq.x, 0.001), uPaso.y);
        nivel = max(nivel, prendido(pat, uPaso.x - float(k), p, w) * e);
    }
    vec3 col = src.rgb * mix(uCh.w, 1.0, clamp(nivel, 0.0, 1.0));
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

LIB = r'''# chaser_lib — pasos del chaser (lo escribe chaser_led.py; no editar aqui)
import math


def kick(val, prev):
    B = parent()
    thr = B.par.Chaserumbral.eval()
    if not (prev < thr <= val):
        return
    n = B.fetch('ch_kicks', 0, search=False) + 1
    B.store('ch_kicks', n)
    if B.par.Chaseravance.eval() == 'kick' and n % max(1, int(B.par.Chasercada.eval())) == 0:
        avanzar()


def avanzar():
    B = parent()
    ahora = absTime.seconds
    t = B.fetch('ch_t', ahora, search=False)
    dt = ahora - t
    if 0.08 < dt < 4.0:
        B.store('ch_dur', 0.7 * B.fetch('ch_dur', 0.5, search=False) + 0.3 * dt)
    B.store('ch_t', ahora)
    B.par.Chaserpaso = (int(B.par.Chaserpaso.eval()) + 1) % 720720     # multiplo de 2..16


def info(i):
    """0 paso · 1 segundos desde el paso · 2 segundos entre pasos"""
    B = parent()
    ahora = absTime.seconds
    cada = max(1, int(B.par.Chasercada.eval()))
    modo = B.par.Chaseravance.eval()
    if modo == 'tempo':
        t = op('/project2/audio/tempo/tempo_lib')
        if t is not None:
            dur = 60.0 / max(1.0, t.module.bpm()) * cada
            x = t.module.fase() / cada
            return [float(math.floor(x)), (x - math.floor(x)) * dur, dur][i]
        modo = 'bpm'
    if modo == 'bpm':
        dur = 60.0 / max(1.0, B.par.Chaserbpm.eval()) * cada
        x = ahora / dur
        return [float(math.floor(x)), (x - math.floor(x)) * dur, dur][i]
    return [float(B.par.Chaserpaso.eval()), ahora - B.fetch('ch_t', ahora - 10.0, search=False),
            B.fetch('ch_dur', 0.5, search=False)][i]
'''


def nuevo(comp, tipo, nombre, x, y):
    o = comp.op(nombre)
    if o is None:
        o = comp.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def pagina(comp, nombre):
    for p in comp.customPages:
        if p.name == nombre:
            return p
    return comp.appendCustomPage(nombre)


def par(pg, kind, nombre, label, default=None, rango=None, **kw):
    if not hasattr(B.par, nombre):
        getattr(pg, 'append' + kind)(nombre, label=label, **kw)
        p = getattr(B.par, nombre)
        if default is not None:
            p.default = default
            p.val = default
    p = getattr(B.par, nombre)
    if rango:
        p.normMin, p.normMax = rango
    return p


if B is None or B.op('led_cadena') is None:
    print('[fallo] falta /project1/led con led_salida: instala antes led_salida')
else:
    pg = pagina(B, 'Chaser')
    par(pg, 'Toggle', 'Chaseron', 'Chaser prendido', False)
    p = par(pg, 'Menu', 'Chaserpatron', 'Patron')
    p.menuNames = ['corrida', 'idavuelta', 'centro', 'afuera', 'pares', 'aleatorio', 'acumular', 'todos']
    p.menuLabels = ['Corrida (en orden)', 'Ida y vuelta', 'Centro -> afuera', 'Afuera -> centro',
                    'Pares / impares', 'Aleatorio', 'Acumular', 'Todos (golpe)']
    p = par(pg, 'Menu', 'Chaseravance', 'Avanza con')
    p.menuNames = ['tempo', 'kick', 'bpm']
    p.menuLabels = ['BPM detectado (audio)', 'Kick (audio)', 'BPM fijo']
    par(pg, 'Int', 'Chasercada', 'Cada (kicks o tiempos)', 1, (1, 8))
    par(pg, 'Float', 'Chaserbpm', 'BPM fijo', 124.0, (60.0, 200.0))
    d = par(pg, 'Float', 'Chaserbpmdet', 'BPM detectado (lectura)', None, (60.0, 200.0))
    d.expr = "op('/project2/show').par.Tempobpm if hasattr(op('/project2/show').par, 'Tempobpm') else 0"
    d.readOnly = True
    par(pg, 'Float', 'Chaserumbral', 'Umbral del kick', 0.5, (0.05, 1.0))
    par(pg, 'Int', 'Chaserancho', 'Ancho (tableros)', 1, (1, 6))
    par(pg, 'Float', 'Chaserdecay', 'Decaimiento (s)', 0.35, (0.02, 2.0))
    par(pg, 'Float', 'Chaserataque', 'Ataque (s)', 0.04, (0.0, 0.3))
    par(pg, 'Float', 'Chaserfondo', 'Fondo (lo apagado)', 0.15, (0.0, 1.0))
    par(pg, 'Int', 'Chaserpaso', 'Paso (lectura)', 0, (0, 64))
    pg.sort('Chaseron', 'Chaserpatron', 'Chaseravance', 'Chasercada', 'Chaserbpmdet', 'Chaserbpm', 'Chaserumbral',
            'Chaserancho', 'Chaserdecay', 'Chaserataque', 'Chaserfondo', 'Chaserpaso')

    lib = nuevo(B, textDAT, 'chaser_lib', 600, 850)
    lib.text = LIB
    k = nuevo(B, selectCHOP, 'chaser_kick', 600, 750)
    k.par.chops = AUDIO
    k.par.channames = 'kick'
    kx = nuevo(B, chopexecuteDAT, 'chaser_kick_exec', 800, 750)
    kx.par.chop = k.name
    for pn in ('channels', 'channel'):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = 'kick'
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False), ('whileon', False), ('whileoff', False)):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = v
    kx.text = ("def onValueChange(channel, sampleIndex, val, prev):\n"
               "    mod('chaser_lib').kick(val, prev)\n"
               "    return\n")

    dat = nuevo(B, textDAT, 'chaser_led_pixel', 800, 500)
    dat.text = SHADER
    g = nuevo(B, glslTOP, 'chaser_led', 800, 400)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 4
    g.par.vec0name = 'uCh'
    g.par.vec0valuex.expr = 'int(parent().par.Chaseron.eval())'
    g.par.vec0valuey.expr = 'parent().par.Chaserpatron.menuIndex'
    g.par.vec0valuez.expr = 'parent().par.Chaserancho'
    g.par.vec0valuew.expr = 'parent().par.Chaserfondo'
    g.par.vec1name = 'uPaso'
    for i, c in enumerate('xyz'):
        getattr(g.par, 'vec1value' + c).expr = "op('chaser_lib').module.info(%d) if absTime.frame >= 0 else 0" % i
    g.par.vec1valuew.expr = 'parent().par.Chaserdecay'
    g.par.vec2name = 'uAtq'
    g.par.vec2valuex.expr = 'parent().par.Chaserataque'
    g.par.vec3name = 'uGrid'
    g.par.vec3valuex.expr, g.par.vec3valuey.expr = 'parent().par.Columnas', 'parent().par.Filas'

    # en la cadena LED antes del barrido (el barrido va encima del chaser, no se apaga con el)
    g.tags.add('ledfx')
    g.store('orden', 10)
    cadena = B.op('led_cadena').module.encadenar()
    g.cook(force=True)
    print('[ok] ledfx_chaser | cadena %s | prendido=%s | patron=%s | avanza=%s'
          % (cadena, B.par.Chaseron.eval(), B.par.Chaserpatron.eval(), B.par.Chaseravance.eval()))
    print('kick:', k.numChans and [c.name for c in k.chans()], '| errores:', g.errors() or g.warnings() or 'ninguno')
