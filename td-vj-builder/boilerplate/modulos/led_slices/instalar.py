# led_slices — el ADVANCED OUTPUT de Resolume rehecho en TD, desde su XML: alternativa / respaldo de Resolume.
# Idempotente: reinstalar = actualizar (conserva XML, prueba, monitor y lo armado). Ver LEEME.md (el proceso).
# Origen: Casa Bacardi x Corona Capital (2026-11-20).
#
# /project1/slices:
#   entrada (select del TOP que hoy va por Spout / NDI a Resolume) -> mapa (GLSL, Salidaw x Salidah) -> out_slices
#   tabla `slices` (nombre, x, y, w, h, on, entrada) en px de salida, origen ARRIBA-izquierda como en Resolume;
#   editar la tabla o "Leer XML otra vez" regenera el shader. Prueba: Ninguna · Bordes · Guia (pixel map del XML).
#   Avisa al leer el XML si hay algo que no reproduce (warp, rotacion, flip, color, mascara, soft edge).
# /salida_slices: ventana CERRADA y SIN ARMAR al instalar. Abrir = arma y va al monitor externo a pantalla completa
#   (sin externo: ventana de prueba en la lap). Armada: vigia cada 2 s y al arrancar; si se pierde el externo la
#   cierra y espera. No se arma si la salida LED (led_salida) esta armada: hay un solo monitor externo.
# proyecto.json -> "slices": {"xml": "...", "entrada": "/project1/...", "guia": "..."} (rutas relativas a project.folder).
import json, os

P1 = op('/project1')
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())


def config():
    ruta = project.folder + '/proyecto.json'
    try:
        return json.load(open(ruta, encoding='utf-8')).get('slices', {}) if os.path.exists(ruta) else {}
    except Exception:
        return {}


def entrada_default():
    """Lo que hoy va a Resolume: la entrada del Spout / NDI cuadrado o 16:9; si no, color_final."""
    for n in ('spout_cuadrado', 'ndiout_cuadrado', 'spoutout1', 'ndiout1'):
        o = P1.op(n)
        if o is not None and o.inputs:
            return o.inputs[0].path
    return '/project1/color_final'


cfg = config()
C = P1.op('slices') or P1.create(baseCOMP, 'slices')
ancla = P1.op('spout_cuadrado') or P1.op('color_final')
if ancla is not None:
    C.nodeX, C.nodeY = ancla.nodeX + 200, ancla.nodeY - 150
C.comment = 'Advanced Output de Resolume rehecho en TD (modulos/led_slices). Alternativa a Resolume.'

# ---- pagina Slices: prueba, salida, mapeo
pg = next((g for g in C.customPages if g.name == 'Slices'), None) or C.appendCustomPage('Slices')


def _int(n, label, v, lo, hi):
    if not hasattr(C.par, n):
        p = pg.appendInt(n, label=label)[0]
        p.default, p.val = v, v
    p = getattr(C.par, n)
    p.normMin, p.normMax = lo, hi
    return p


if not hasattr(C.par, 'Prueba'):
    pg.appendMenu('Prueba', label='Prueba')
_prev = C.par.Prueba.eval()                 # cambiar menuNames mueve el valor: se guarda y se regresa
C.par.Prueba.menuNames = ['ninguna', 'bordes', 'guia']
C.par.Prueba.menuLabels = ['Ninguna (visual)', 'Bordes de cada slice', 'Guia pixel map (slices del XML)']
C.par.Prueba = _prev if _prev in C.par.Prueba.menuNames else 'ninguna'
_int('Salidaw', 'Ancho de salida (px)', 1920, 640, 3840)
_int('Salidah', 'Alto de salida (px)', 1080, 360, 2160)
for n, label, v in (('Xml', 'XML de Advanced Output', cfg.get('xml', '')),
                    ('Guia', 'Guia pixel map (PNG)', cfg.get('guia', ''))):
    if not hasattr(C.par, n):
        pg.appendFile(n, label=label)
        getattr(C.par, n).val = v
if not hasattr(C.par, 'Entrada'):
    pg.appendTOP('Entrada', label='Entrada (lo que va a Resolume)')
    C.par.Entrada = cfg.get('entrada', '') or entrada_default()
if not hasattr(C.par, 'Leerxml'):
    pg.appendPulse('Leerxml', label='Leer XML otra vez')
if not hasattr(C.par, 'Lectura'):
    pg.appendStr('Lectura', label='Slices leidos')
if not hasattr(C.par, 'Avisosxml'):
    pg.appendStr('Avisosxml', label='No reproduce')
C.par.Lectura.readOnly = True
C.par.Avisosxml.readOnly = True
secciones(C, 'Slices', [
    ('Hprueba', 'PRUEBA', ['Prueba']),
    ('Hsalida', 'SALIDA', ['Salidaw', 'Salidah']),
    ('Hxml', 'MAPEO (XML DE RESOLUME)', ['Xml', 'Leerxml', 'Entrada', 'Guia']),
    ('Hlectura', 'LECTURA', ['Lectura', 'Avisosxml']),
])

# ---- nodos
ent = C.op('entrada') or C.create(selectTOP, 'entrada')
ent.par.top.expr = 'parent().par.Entrada'
ent.nodeX, ent.nodeY = 0, 0
gu = C.op('guia') or C.create(moviefileinTOP, 'guia')
gu.par.file.expr = 'parent().par.Guia'
gu.nodeX, gu.nodeY = 0, -150
tb = C.op('slices') or C.create(tableDAT, 'slices')
tb.nodeX, tb.nodeY = 0, 200
lib = C.op('slices_lib') or C.create(textDAT, 'slices_lib')
lib.nodeX, lib.nodeY = 200, 200
fr = C.op('mapa_frag') or C.create(textDAT, 'mapa_frag')
fr.nodeX, fr.nodeY = 400, 200
g = C.op('mapa') or C.create(glslTOP, 'mapa')
g.nodeX, g.nodeY = 200, 0
g.inputConnectors[0].connect(ent)
g.inputConnectors[1].connect(gu)
epa = C.op('entrada_pano') or C.create(selectTOP, 'entrada_pano')
epa.nodeX, epa.nodeY = 0, -300
g.inputConnectors[2].connect(epa)
g.par.pixeldat = fr
g.par.outputresolution = 'custom'
g.par.resolutionw.expr = 'parent().par.Salidaw'
g.par.resolutionh.expr = 'parent().par.Salidah'
if getattr(g.par, 'inputfiltertype', None) is not None:
    g.par.inputfiltertype = 'mipmap'          # composicion grande -> slice chico: sin aliasing
g.par.uniname0 = 'u_prueba'
g.par.value0x.expr = 'parent().par.Prueba.menuIndex'
g.par.uniname1 = 'uPano'
g.par.value1x.expr = "op('pano_lib').module.cantidad() if absTime.frame >= 0 else 0"
g.par.value1y.expr = "op('pano_lib').module.recorte(0)"
g.par.value1z.expr = "op('pano_lib').module.recorte(1)"
# indice: por pixel de salida, que slice es (r, -1 = ninguno), cuantos hay (g) y donde cae adentro (b, a = u, v
# desde abajo-izquierda del slice). Lo leen los efectos ledfx_* (chaser, barrido) para ir slice por slice.
fi = C.op('indice_frag') or C.create(textDAT, 'indice_frag')
fi.nodeX, fi.nodeY = 400, 350
gi = C.op('indice') or C.create(glslTOP, 'indice')
gi.nodeX, gi.nodeY = 200, -150
gi.par.pixeldat = fi
gi.par.outputresolution = 'custom'
gi.par.resolutionw.expr = 'parent().par.Salidaw'
gi.par.resolutionh.expr = 'parent().par.Salidah'
gi.par.format = 'rgba32float'
out = C.op('out_slices') or C.create(nullTOP, 'out_slices')
out.nodeX, out.nodeY = 800, 0
out.viewer = True
cad = C.op('slices_cadena') or C.create(textDAT, 'slices_cadena')
cad.nodeX, cad.nodeY = 600, 200
cad.text = r'''# slices_cadena — efectos de la segunda capa (tag 'ledfx', store 'orden') entre mapa y out_slices.
# La llaman los ledfx_* al instalarse (lo escribe modulos/led_slices; no editar aqui).
def encadenar():
    C = parent()
    fx = sorted([o for o in C.children if o.isTOP and 'ledfx' in o.tags],
                key=lambda o: (o.fetch('orden', 50, search=False), o.name))
    prev = C.op('base') or C.op('mapa')      # base = el visual o, en SOLO EFECTOS, color solido
    for i, f in enumerate(fx):
        f.inputConnectors[0].connect(prev)
        f.inputConnectors[1].connect(C.op('indice'))
        f.nodeX, f.nodeY = 400 + 150 * i, 0
        prev = f
    mk = C.op('mascara')                       # mascara redonda al final: todo (visual y efectos) sigue el circulo
    if mk is not None:
        mk.inputConnectors[0].connect(prev)
        mk.inputConnectors[1].connect(C.op('indice'))
        prev = mk
    C.op('out_slices').inputConnectors[0].connect(prev)
    C.op('out_slices').nodeX = 400 + 150 * len(fx)
    return [f.name for f in fx]
'''

lib.text = r'''# slices_lib — lee el XML de Advanced Output de Resolume a la tabla `slices` y escribe el shader `mapa_frag`.
# Lo escribe modulos/led_slices/instalar.py (no editar aqui).
import xml.etree.ElementTree as ET
C = me.parent()


def _ruta(r):
    return r if (':' in r[:3] or r.startswith('/')) else project.folder + '/' + r


def _pts(el):
    return [(float(v.get('x')), float(v.get('y'))) for v in el.findall('v')] if el is not None else []


def _recto(p, tol=0.6):
    """4 vertices en orden (arriba-izq, arriba-der, abajo-der, abajo-izq) de un rectangulo sin girar."""
    return (len(p) == 4 and abs(p[0][1] - p[1][1]) < tol and abs(p[2][1] - p[3][1]) < tol
            and abs(p[0][0] - p[3][0]) < tol and abs(p[1][0] - p[2][0]) < tol and p[1][0] > p[0][0] and p[3][1] > p[0][1])


def _avisos(sl, o):
    """Lo que tiene el slice en Resolume y este mapeo NO reproduce."""
    av = []
    val = {p.get('name'): p.get('value') for p in sl.iter() if p.get('name') and p.get('value') is not None}
    if not _recto(o):
        av.append('salida girada / no rectangular')
    if not _recto(_pts(sl.find('InputRect'))):
        av.append('entrada girada')
    h = sl.find('.//Homography')
    if h is not None and any(abs(a[0] - b[0]) > 0.5 or abs(a[1] - b[1]) > 0.5
                             for a, b in zip(_pts(h.find('src')), _pts(h.find('dst')))):
        av.append('warp (perspectiva)')
    bz = sl.find('.//BezierWarper')
    if bz is not None and _recto(o):
        vs = _pts(bz.find('vertices'))
        cw, chh = int(bz.get('controlWidth', 4)), int(bz.get('controlHeight', 4))
        x0, y0, x1, y1 = o[0][0], o[0][1], o[2][0], o[2][1]
        for k, (x, y) in enumerate(vs):
            i, j = k % cw, k // cw
            if abs(x - (x0 + (x1 - x0) * i / max(1, cw - 1))) > 0.6 or abs(y - (y0 + (y1 - y0) * j / max(1, chh - 1))) > 0.6:
                av.append('warp curvo (bezier)')
                break
    if val.get('Flip', '0') not in ('0', ''):
        av.append('flip')
    if any(abs(float(val.get(n, '0') or 0)) > 1e-6 for n in ('Brightness', 'Contrast', 'Red', 'Green', 'Blue')):
        av.append('color / brillo')
    if val.get('SoftEdgeEnable', '0') == '1':
        av.append('soft edge')
    if any('mask' in e.tag.lower() for e in sl.iter()):
        av.append('mascara')
    return av


def leer_xml():
    tb = C.op('slices')
    tb.clear()
    tb.appendRow(['nombre', 'x', 'y', 'w', 'h', 'on', 'entrada', 'celda'])
    ruta = C.par.Xml.eval()
    if not ruta:
        C.par.Lectura = 'sin XML: poner la ruta en "XML de Advanced Output" y "Leer XML otra vez"'
        C.par.Avisosxml = ''
        generar()
        return
    r = ET.parse(_ruta(ruta)).getroot()
    avisos = []
    pantallas = len(r.findall('.//screens/Screen')) or 1
    if pantallas > 1:
        avisos.append('%d pantallas en el XML: van todas a la misma salida' % pantallas)
    for sl in r.iter('Slice'):
        nom = next((p.get('value') for p in sl.iter('Param') if p.get('name') == 'Name'), '?')
        on = next((p.get('value') for p in sl.iter('Param') if p.get('name') == 'Enabled'), '1')
        o = _pts(sl.find('OutputRect'))
        i = _pts(sl.find('InputRect'))
        xs, ys = [p[0] for p in o], [p[1] for p in o]
        ix, iy = [p[0] for p in i], [p[1] for p in i]
        tb.appendRow([nom, min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), on,
                      '%g %g %g %g' % (min(ix), min(iy), max(ix) - min(ix), max(iy) - min(iy)),
                      '%d %d' % celda_de(nom, tb.numRows - 1)])
        for a in _avisos(sl, o):
            avisos.append('%s: %s' % (nom, a))
    d = r.find('.//OutputDeviceDisplay')
    if d is not None and d.get('width'):
        C.par.Salidaw, C.par.Salidah = int(d.get('width')), int(d.get('height'))
    comp = r.find('.//CurrentCompositionTextureSize')
    C.store('comp', (float(comp.get('width')), float(comp.get('height'))) if comp is not None else (1920.0, 1080.0))
    C.par.Avisosxml = ' · '.join(avisos) if avisos else 'nada: todo se reproduce igual'
    if avisos:
        print('[led_slices] OJO, no se reproduce:', '; '.join(avisos))
    generar()


def celda_de(nom, i):
    """(columna, fila) en el lienzo panoramico: 'A-1' -> (0, 0), 'C-4' -> (3, 2). Sin letra-numero: de 4 en 4."""
    import re
    m = re.match(r'^\s*([A-Za-z])\s*-?\s*(\d+)\s*$', nom or '')
    if m:
        return int(m.group(2)) - 1, ord(m.group(1).upper()) - 65
    return i % 4, i // 4


def generar():
    tb = C.op('slices')
    cw, ch = C.fetch('comp', (1920.0, 1080.0), search=False)
    rects, ins, ons, n, celdas = [], [], [], 0, []
    for r in range(1, tb.numRows):
        x, y, w, h = (float(tb[r, c].val) for c in ('x', 'y', 'w', 'h'))
        e = [float(v) for v in (tb[r, 'entrada'].val or '0 0 %g %g' % (cw, ch)).split()]
        rects.append('vec4(%.3f, %.3f, %.3f, %.3f)' % (x, y, w, h))
        ins.append('vec4(%.5f, %.5f, %.5f, %.5f)' % (e[0] / cw, e[1] / ch, e[2] / cw, e[3] / ch))
        ons.append('1.0' if tb[r, 'on'].val in ('1', 'True', 'true') else '0.0')
        cel = tb[r, 'celda'].val.split() if tb[r, 'celda'] is not None and tb[r, 'celda'].val.strip() else None
        cx, cy = (int(cel[0]), int(cel[1])) if cel else celda_de(tb[r, 'nombre'].val, r - 1)
        celdas.append((cx, cy))
        n += 1
    if n == 0:
        rects, ins, ons, n, celdas = ['vec4(0.0)'], ['vec4(0.0, 0.0, 1.0, 1.0)'], ['0.0'], 1, [(0, 0)]
    cols = max(c for c, f in celdas) + 1
    filas = max(f for c, f in celdas) + 1
    C.store('lienzo', (cols, filas))
    k = {'N': n, 'R': ',\n    '.join(rects), 'I': ',\n    '.join(ins), 'O': ', '.join(ons),
         'CEL': ', '.join('vec2(%d.0, %d.0)' % c for c in celdas), 'COLS': cols, 'FILAS': filas}
    C.op('mapa_frag').text = SHADER % k
    C.op('indice_frag').text = INDICE % k
    if tb.numRows > 1:
        C.par.Lectura = '%d slices · salida %dx%d · composicion %dx%d' % (
            tb.numRows - 1, C.par.Salidaw.eval(), C.par.Salidah.eval(), cw, ch)


SHADER = """// mapa_frag — generado por slices_lib desde la tabla `slices` (Advanced Output de Resolume). No editar a mano.
// Cada slice: rectangulo de salida en px (origen arriba-izquierda, como Resolume) <- rectangulo de entrada (0-1).
uniform float u_prueba;      // 0 visual · 1 bordes · 2 guia pixel map
uniform vec4 uPano;          // x cantidad panoramico (0-1) · y x inicial del recorte · z ancho del recorte (fuente 2)
out vec4 fragColor;
const int N = %(N)d;
const vec2 GRID = vec2(%(COLS)d.0, %(FILAS)d.0);   // lienzo panoramico: columnas x filas de bocinas pegadas
const vec4 R[N] = vec4[N](
    %(R)s);
const vec4 IN[N] = vec4[N](
    %(I)s);
const float ON[N] = float[N](%(O)s);
const vec2 CELDA[N] = vec2[N](%(CEL)s);
void main() {
    vec2 res = uTDOutputInfo.res.zw;
    vec2 p = vec2(vUV.s, 1.0 - vUV.t) * res;              // px desde arriba-izquierda
    if (u_prueba > 1.5) { fragColor = TDOutputSwizzle(texture(sTD2DInputs[1], vUV.st)); return; }
    vec3 col = vec3(0.0);
    float borde = 0.0;
    for (int i = 0; i < N; i++) {
        if (ON[i] < 0.5) continue;
        vec2 u = (p - R[i].xy) / R[i].zw;
        if (u.x < 0.0 || u.y < 0.0 || u.x >= 1.0 || u.y >= 1.0) continue;
        vec2 e = IN[i].xy + u * IN[i].zw;                 // en la composicion, arriba-izquierda
        col = texture(sTD2DInputs[0], vec2(e.x, 1.0 - e.y)).rgb;
        if (uPano.x > 0.001) {                            // PANORAMICO: una sola imagen en todas las bocinas
            vec2 cv = (CELDA[i] + u) / GRID;              // en el lienzo, arriba-izquierda
            vec3 pan = texture(sTD2DInputs[2], vec2(uPano.y + cv.x * uPano.z, 1.0 - cv.y)).rgb;
            col = mix(col, pan, uPano.x);
        }
        vec2 d = min(p - R[i].xy, R[i].xy + R[i].zw - p);
        borde = max(borde, 1.0 - step(2.0, min(d.x, d.y)));
    }
    if (u_prueba > 0.5) col = mix(col, vec3(0.43, 0.77, 0.60), borde);
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
"""

INDICE = """// indice_frag — generado por slices_lib: r = slice (-1 ninguno, en el orden del XML), g = cuantos,
// b, a = posicion dentro del slice (0-1, desde abajo-izquierda). Lo usan los efectos ledfx_* en modo slices.
out vec4 fragColor;
const int N = %(N)d;
const vec4 R[N] = vec4[N](
    %(R)s);
const float ON[N] = float[N](%(O)s);
void main() {
    vec2 p = vec2(vUV.s, 1.0 - vUV.t) * uTDOutputInfo.res.zw;
    vec4 o = vec4(-1.0, float(N), 0.0, 0.0);
    for (int i = 0; i < N; i++) {
        if (ON[i] < 0.5) continue;
        vec2 u = (p - R[i].xy) / R[i].zw;
        if (u.x < 0.0 || u.y < 0.0 || u.x >= 1.0 || u.y >= 1.0) continue;
        o = vec4(float(i), float(N), u.x, 1.0 - u.y);
    }
    fragColor = o;
}
"""
'''

dx = C.op('slices_cambio') or C.create(datexecuteDAT, 'slices_cambio')
dx.par.dat = tb
dx.par.tablechange = True
dx.text = '\n'.join(['# tabla `slices` cambiada a mano -> regenera el shader',
                     'def onTableChange(dat):', "    op('slices_lib').module.generar()", '    return', ''])
dx.nodeX, dx.nodeY = 200, 350
px = C.op('slices_pulso') or C.create(parameterexecuteDAT, 'slices_pulso')
px.par.op = C.path
px.par.pars = 'Leerxml'
px.par.onpulse = True
px.text = '\n'.join(['def onPulse(par):', "    op('slices_lib').module.leer_xml()", '    return', ''])
px.nodeX, px.nodeY = 400, 350

lib.module.leer_xml()
# ---- QUE SALE (2026-11-20): VISUAL + EFECTOS (los efectos ledfx_* encima del visual) o SOLO EFECTOS (el visual se
# cambia por un color solido de la paleta y los efectos trabajan sobre el: chaser, EQ y respiracion quedan como
# patrones de color por bocina; cascada y giro necesitan visual). Pagina Efectos.
pe = next((x for x in C.customPages if x.name == 'Efectos'), None) or C.appendCustomPage('Efectos')
if not hasattr(C.par, 'Salemezcla'):
    pe.appendMenu('Salemezcla', label='Que sale')
_v = C.par.Salemezcla.eval()
C.par.Salemezcla.menuNames = ['visual', 'efectos']
C.par.Salemezcla.menuLabels = ['Visual + efectos', 'Solo efectos (sobre color solido)']
C.par.Salemezcla = _v if _v in C.par.Salemezcla.menuNames else 'visual'
if not hasattr(C.par, 'Basetinta'):
    pe.appendMenu('Basetinta', label='Color de fondo (solo efectos)')
_v = C.par.Basetinta.eval()
C.par.Basetinta.menuNames = ['a', 'b', 'blanco']
C.par.Basetinta.menuLabels = ['Color A (paleta)', 'Color B (paleta)', 'Blanco']
C.par.Basetinta = _v if _v in C.par.Basetinta.menuNames else 'a'
if not hasattr(C.par, 'Basenivel'):
    p = pe.appendFloat('Basenivel', label='Nivel del fondo (solo efectos)')[0]
    p.default, p.val = 0.6, 0.6
C.par.Basenivel.normMin, C.par.Basenivel.normMax = 0.0, 1.0
# ---- MASCARA REDONDA (2026-11-20): bocinas circulares. AUTOMATICA = solo cuando esta al aire un visual que no es
# circular ni logo (en Corona Capital: los generativos de CH9); los grupos CIRCULARES / LOGOS ya son redondos. Entra y
# sale con un fundido corto. Siempre / Nunca para forzarla. Va al final de la cadena; con Prueba (bordes / guia) no actua.
if not hasattr(C.par, 'Mascaramodo'):
    pe.appendMenu('Mascaramodo', label='Mascara redonda')
_v = C.par.Mascaramodo.eval()
C.par.Mascaramodo.menuNames = ['auto', 'siempre', 'nunca']
C.par.Mascaramodo.menuLabels = ['Automatica (solo visuales no circulares)', 'Siempre', 'Nunca']
C.par.Mascaramodo = _v if _v in C.par.Mascaramodo.menuNames else 'auto'
for _n, _l, _d, _lo, _hi in (('Mascaratam', 'Tamano del circulo (1 = toca los bordes)', 1.0, 0.6, 1.1),
                             ('Mascarasuave', 'Borde suave', 0.04, 0.0, 0.2)):
    if not hasattr(C.par, _n):
        _p = pe.appendFloat(_n, label=_l)[0]
        _p.default, _p.val = _d, _d
    getattr(C.par, _n).normMin, getattr(C.par, _n).normMax = _lo, _hi
if not hasattr(C.par, 'Mascaraahora'):
    pe.appendStr('Mascaraahora', label='Ahora')
C.par.Mascaraahora.readOnly = True
# ---- PANORAMICO (2026-11-20): una sola imagen en todas las bocinas, como si fueran una pantalla de COLS x FILAS
# bocinas pegadas (celdas de la tabla: A-1 = columna 0 fila 0 ...). Fuente: el cuadro completo (16:9) del visual,
# recortado al centro a la proporcion del lienzo (o estirado). Modos: SOLO PANORAMICOS (los del grupo PANORAMICOS de
# GRUPOS; default: no cambia nada hasta que haya ese canal) · AUTOMATICO (panoramicos + los que no son redondos: los
# generativos) · SIEMPRE · NUNCA. Entra y sale con 0.4 s de fundido.
if not hasattr(C.par, 'Panomodo'):
    pe.appendMenu('Panomodo', label='Panoramico (todas las bocinas)')
_v = C.par.Panomodo.eval()
C.par.Panomodo.menuNames = ['panoramicos', 'auto', 'siempre', 'nunca']
C.par.Panomodo.menuLabels = ['Solo canal PANORAMICOS', 'Automatico (+ generativos)', 'Siempre', 'Nunca']
C.par.Panomodo = _v if _v in C.par.Panomodo.menuNames else 'panoramicos'
if not hasattr(C.par, 'Panoencuadre'):
    pe.appendMenu('Panoencuadre', label='Encuadre')
_v = C.par.Panoencuadre.eval()
C.par.Panoencuadre.menuNames = ['recorte', 'estirar']
C.par.Panoencuadre.menuLabels = ['Recorte al centro (sin deformar)', 'Estirar (todo el cuadro)']
C.par.Panoencuadre = _v if _v in C.par.Panoencuadre.menuNames else 'recorte'
if not hasattr(C.par, 'Panoentrada'):
    pe.appendTOP('Panoentrada', label='Fuente panoramica (cuadro completo)')
    C.par.Panoentrada = '/project1/color_final' if op('/project1/color_final') else ''
if not hasattr(C.par, 'Panoahora'):
    pe.appendStr('Panoahora', label='Ahora')
C.par.Panoahora.readOnly = True
epa.par.top.expr = 'parent().par.Panoentrada'
pl_ = C.op('pano_lib') or C.create(textDAT, 'pano_lib')
pl_.nodeX, pl_.nodeY = 900, 500
pl_.text = r"""# pano_lib — cuanto se aplica el PANORAMICO y el recorte (lo escribe modulos/led_slices; no editar aqui)
C = me.parent()


def panoramicas():
    # entradas de switch2 del grupo PANORAMICOS (cache)
    r = C.fetch('pano_entradas', None, search=False)
    if r is None:
        m = op('mascara_lib').module
        B, G = m._ui_bancos('BANCOS') or {}, m._ui_bancos('GRUPOS') or {}
        r = sorted(x[1] for canal, pads in B.items() if 'PANORAM' in G.get(canal, '').upper() for x in pads if x)
        C.store('pano_entradas', r)
    return r


def objetivo():
    modo = C.par.Panomodo.eval()
    if modo in ('siempre', 'nunca'):
        return 1.0 if modo == 'siempre' else 0.0
    sw = op('/project2/switch2')
    k = int(sw.par.index.eval()) if sw is not None else -1
    if k in panoramicas():
        return 1.0
    if modo == 'auto' and k not in op('mascara_lib').module.redondas():
        return 1.0
    return 0.0


def cantidad():
    t = absTime.seconds
    v, t0 = C.fetch('pano_v', (objetivo(), t), search=False)
    obj = objetivo()
    paso = max(0.0, t - t0) / 0.4
    v = obj if abs(obj - v) <= paso else v + (paso if obj > v else -paso)
    C.store('pano_v', (v, t))
    txt = 'panoramico' if v > 0.99 else ('cada bocina con su visual' if v < 0.01 else 'cambiando')
    if C.par.Panoahora.eval() != txt:
        C.par.Panoahora = txt
    return v


def recorte(i):
    # (x inicial, ancho) del cuadro fuente que entra al lienzo; recorte = sin deformar
    if C.par.Panoencuadre.eval() == 'estirar':
        return (0.0, 1.0)[i]
    cols, filas = C.fetch('lienzo', (4, 3), search=False)
    f = op(C.par.Panoentrada.eval()) if C.par.Panoentrada.eval() else None
    a = (f.width / max(1.0, float(f.height))) if f is not None else 16.0 / 9.0
    k = cols / float(filas)
    ancho = min(1.0, k / a)
    return ((1.0 - ancho) * 0.5, ancho)[i]
"""
C.unstore('pano_entradas')
secciones(C, 'Efectos', [('Hsale', 'QUE SALE', ['Salemezcla']),
                         ('Hpano', 'PANORAMICO', ['Panomodo', 'Panoencuadre', 'Panoentrada', 'Panoahora']),
                         ('Hmascara', 'MASCARA REDONDA', ['Mascaramodo', 'Mascaratam', 'Mascarasuave', 'Mascaraahora']),
                         ('Hbase', 'SOLO EFECTOS: FONDO', ['Basetinta', 'Basenivel'])])
ml = C.op('mascara_lib') or C.create(textDAT, 'mascara_lib')
ml.nodeX, ml.nodeY = 900, 200
ml.text = r"""# mascara_lib — cuanto se aplica la mascara redonda (lo escribe modulos/led_slices; no editar aqui)
import ast
C = me.parent()
REDONDOS = ('CIRCULAR', 'LOGO')           # grupos de BANCOS que ya son redondos


def _ui_bancos(nombre):
    try:
        body = ast.parse(open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read()).body
        n = next(n for n in body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == nombre)
        return eval(compile(ast.Expression(n.value), 'ui_bancos', 'eval'), {'__builtins__': {}})
    except Exception:
        return None


def redondas():
    # entradas de switch2 de visuales que ya son redondos (cache)
    r = C.fetch('mascara_redondas', None, search=False)
    if r is None:
        B, G = _ui_bancos('BANCOS') or {}, _ui_bancos('GRUPOS') or {}
        r = sorted(x[1] for canal, pads in B.items() if any(k in G.get(canal, '') for k in REDONDOS) for x in pads if x)
        C.store('mascara_redondas', r)
    return r


def objetivo():
    modo = C.par.Mascaramodo.eval()
    if modo != 'auto':
        return 1.0 if modo == 'siempre' else 0.0
    sw = op('/project2/switch2')
    k = int(sw.par.index.eval()) if sw is not None else -1
    return 0.0 if k in redondas() else 1.0


def cantidad():
    # fundido de 0.4 s hacia el objetivo (se evalua cada cuadro desde el uniform)
    t = absTime.seconds
    v, t0 = C.fetch('mascara_v', (objetivo(), t), search=False)
    obj = objetivo()
    paso = max(0.0, t - t0) / 0.4                       # fundido lineal: 0.4 s de punta a punta
    v = obj if abs(obj - v) <= paso else v + (paso if obj > v else -paso)
    C.store('mascara_v', (v, t))
    txt = 'aplicada' if v > 0.99 else ('quitada' if v < 0.01 else 'cambiando')
    if C.par.Mascaraahora.eval() != txt:
        C.par.Mascaraahora = txt
    return v
"""
C.unstore('mascara_redondas')
fm = C.op('mascara_frag') or C.create(textDAT, 'mascara_frag')
fm.nodeX, fm.nodeY = 900, 350
fm.text = """// mascara — bocinas redondas: lo de fuera del circulo de cada slice va a negro, con borde suave
uniform vec4 uMas;     // x cantidad (0 - 1) · y tamano (1 = toca los bordes) · z borde suave · w prueba
out vec4 fragColor;
void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uMas.x < 0.001 || uMas.w > 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    float r = length(m.ba - 0.5) * 2.0;                   // 0 centro, 1 = toca el borde del slice
    float k = 1.0 - smoothstep(uMas.y - uMas.z, uMas.y, r);
    fragColor = TDOutputSwizzle(vec4(src.rgb * mix(1.0, k, uMas.x), 1.0));
}
"""
gm = C.op('mascara') or C.create(glslTOP, 'mascara')
gm.nodeX, gm.nodeY = 1100, 0
gm.par.pixeldat = fm
gm.par.outputresolution = 'useinput'
gm.seq.vec.numBlocks = 1
gm.par.vec0name = 'uMas'
gm.par.vec0valuex.expr = "op('mascara_lib').module.cantidad() if absTime.frame >= 0 else 1"
gm.par.vec0valuey.expr = 'parent().par.Mascaratam'
gm.par.vec0valuez.expr = 'parent().par.Mascarasuave'
gm.par.vec0valuew.expr = 'parent().par.Prueba.menuIndex'

fb = C.op('base_frag') or C.create(textDAT, 'base_frag')
fb.nodeX, fb.nodeY = 300, 350
fb.text = """// base — lo que reciben los efectos: el visual (mapa) o, en SOLO EFECTOS, color solido en las bocinas
uniform vec4 uBase;    // x 1 = solo efectos · y nivel · z prueba (bordes / guia: pasa el mapa tal cual)
uniform vec4 uTinta;
out vec4 fragColor;
void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uBase.x < 0.5 || uBase.z > 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
    float dentro = m.r < -0.5 ? 0.0 : 1.0;
    fragColor = TDOutputSwizzle(vec4(uTinta.rgb * uBase.y * dentro, 1.0));
}
"""
gb = C.op('base') or C.create(glslTOP, 'base')
gb.nodeX, gb.nodeY = 300, -150
gb.par.pixeldat = fb
gb.par.outputresolution = 'useinput'
gb.inputConnectors[0].connect(g)
gb.inputConnectors[1].connect(gi)
gb.seq.vec.numBlocks = 2
gb.par.vec0name = 'uBase'
gb.par.vec0valuex.expr = "1 if parent().par.Salemezcla.eval() == 'efectos' else 0"
gb.par.vec0valuey.expr = 'parent().par.Basenivel'
gb.par.vec0valuez.expr = 'parent().par.Prueba.menuIndex'
gb.par.vec1name = 'uTinta'
for _c, _k in (('r', 'x'), ('g', 'y'), ('b', 'z')):
    getattr(gb.par, 'vec1value' + _k).expr = (
        "[op('/project2/show').par.Colora%s, op('/project2/show').par.Colorb%s, 1.0][parent().par.Basetinta.menuIndex] "
        "if hasattr(op('/project2/show').par, 'Colora%s') else 1.0" % (_c, _c, _c))
cadena = cad.module.encadenar()

# ================================================================ VENTANA /salida_slices
pv = next((x for x in C.customPages if x.name == 'Salida'), None) or C.appendCustomPage('Salida')
if not hasattr(C.par, 'Slicesarmada'):
    pv.appendToggle('Slicesarmada', label='Salida TD armada')
    C.par.Slicesarmada.default = False
    C.par.Slicesarmada = False
if not hasattr(C.par, 'Abrirslices'):
    pv.appendPulse('Abrirslices', label='Abrir ventana (arma)')
    pv.appendPulse('Cerrarslices', label='Cerrar ventana (desarma)')
if not hasattr(C.par, 'Monitor'):
    p = pv.appendInt('Monitor', label='Monitor de salida (0 = lap)')[0]
    p.default, p.val = 1, 1
C.par.Monitor.normMax = 4
if not hasattr(C.par, 'Estado'):
    pv.appendStr('Estado', label='Estado')
C.par.Estado.readOnly = True
secciones(C, 'Salida', [
    ('Hsalidatd', 'SALIDA DESDE TD (ALTERNATIVA A RESOLUME)', ['Slicesarmada', 'Abrirslices', 'Cerrarslices']),
    ('Hmonitor', 'MONITOR', ['Monitor']),
    ('Hestado', 'LECTURA', ['Estado']),
])
orden_paginas(C, ['Salida', 'Efectos', 'Capa', 'Chaser', 'Barrido', 'EQ', 'Onda', 'Cascada', 'Giro', 'Respira', 'Slices'])

vm = C.op('slices_ventana') or C.create(textDAT, 'slices_ventana')
vm.nodeX, vm.nodeY = 600, 350
vm.text = r"""# slices_ventana — coloca y vigila /salida_slices (lo escribe modulos/led_slices/instalar.py; no editar aqui)
import time
C = me.parent()
W = '/salida_slices'


def _pon(w, n, v):
    p = getattr(w.par, n, None)
    if p is not None:
        p.val = v


def log(txt):
    print('[salida_slices] ' + txt)
    try:
        with open(project.folder + '/control/slices_log.txt', 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S  ') + txt + chr(10))
    except Exception:
        pass


def externos():
    return [i for i, m in enumerate(monitors) if not m.isPrimary]


def led_armada():
    L = op('/project1/led')
    return L is not None and hasattr(L.par, 'Ledarmada') and bool(L.par.Ledarmada.eval())


def colocar(abrir=True):
    w = op(W)
    if w is None:
        return ''
    sec = externos()
    if sec:
        if int(C.par.Monitor.eval()) not in sec:
            C.par.Monitor = sec[0]
        m = monitors[int(C.par.Monitor.eval())]
        _pon(w, 'justifyoffsetto', 'specifymonitor')
        _pon(w, 'size', 'fill')
        _pon(w, 'borders', False)
        _pon(w, 'alwaysontop', True)
        _pon(w, 'cursorvisible', 'nocursor')
        _pon(w, 'closeescape', False)
        donde = 'monitor externo %d (%dx%d)' % (C.par.Monitor.eval(), m.width, m.height)
    else:
        m = monitors[0]
        k = min(1.0, 0.6 * m.width / max(1, C.par.Salidaw.eval()), 0.6 * m.height / max(1, C.par.Salidah.eval()))
        _pon(w, 'justifyoffsetto', 'primarymonitor')
        _pon(w, 'size', 'custom')
        _pon(w, 'winw', int(C.par.Salidaw.eval() * k))
        _pon(w, 'winh', int(C.par.Salidah.eval() * k))
        _pon(w, 'winoffsetx', 0)
        _pon(w, 'winoffsety', 0)
        _pon(w, 'borders', True)
        _pon(w, 'alwaysontop', False)
        _pon(w, 'cursorvisible', 'alwaysvisible')
        _pon(w, 'closeescape', True)
        donde = 'la lap, ventana de prueba (no hay monitor externo)'
    if abrir:
        if w.isOpen:
            w.par.winclose.pulse()
            run("op('%s').par.winopen.pulse()" % W, delayFrames=3)
        else:
            w.par.winopen.pulse()
        log('abre en ' + donde)
    return donde


def abrir():
    if led_armada():
        log('NO se abre: la salida LED (/project1/led) esta armada y solo hay un monitor externo')
        C.par.Slicesarmada = False
        return
    C.par.Slicesarmada = True
    colocar(True)


def cerrar():
    C.par.Slicesarmada = False
    w = op(W)
    if w is not None and w.isOpen:
        w.par.winclose.pulse()
        log('cerrada (desarmada)')


def en_externo(w):
    return not bool(w.par.borders.eval())


def vigilar():
    w = op(W)
    C.par.Estado = estado()[0]
    if w is None or not C.par.Slicesarmada.eval():
        return
    if led_armada():
        log('la salida LED se armo: desarmo la de slices')
        cerrar()
        return
    sec = externos()
    if sec:
        if not w.isOpen:
            log('abre en el externo (estaba cerrada)')
            colocar(True)
        elif not en_externo(w) or int(C.par.Monitor.eval()) not in sec:
            log('pasa al externo')
            colocar(True)
    elif w.isOpen and en_externo(w):
        log('se perdio la pantalla externa: cierra y espera a que vuelva')
        w.par.winclose.pulse()


def estado():
    w = op(W)
    abierta = w is not None and w.isOpen
    en_ext = abierta and en_externo(w) and bool(externos())
    if C.par.Slicesarmada.eval():
        if en_ext:
            return ('SLICES · AL AIRE', 1)
        if not externos():
            return ('SLICES · SIN PANTALLA', 3)
        return ('SLICES · ABRIENDO', 2)
    if abierta:
        return ('SLICES · PRUEBA LAP', 2)
    return ('SLICES · APAGADA', 0)
"""
sx = C.op('slices_salida_pulsos') or C.create(parameterexecuteDAT, 'slices_salida_pulsos')
sx.nodeX, sx.nodeY = 800, 350
sx.par.op = C.path
sx.par.pars = 'Abrirslices Cerrarslices'
sx.par.onpulse = True
sx.par.valuechange = False
sx.text = '\n'.join(['def onPulse(par):', "    m = op('slices_ventana').module",
                     "    m.abrir() if par.name == 'Abrirslices' else m.cerrar()", '    return', ''])
md = C.op('slices_monitores') or C.create(monitorsDAT, 'slices_monitores')
md.nodeX, md.nodeY = 600, 500
mx = C.op('slices_monitores_exec') or C.create(datexecuteDAT, 'slices_monitores_exec')
mx.nodeX, mx.nodeY = 800, 500
mx.par.dat = md
mx.par.tablechange = True
mx.text = '\n'.join(['def onTableChange(dat):', "    op('slices_ventana').module.vigilar()", '    return', ''])
vx = C.op('slices_vigia') or C.create(executeDAT, 'slices_vigia')
vx.nodeX, vx.nodeY = 1000, 350
vx.par.start = True
vx.par.framestart = True
vx.text = '\n'.join(['def onStart():',
                     "    run(\"op('/project1/slices/slices_ventana').module.vigilar()\", delayFrames=60)", '    return', '',
                     'def onFrameStart(frame):', '    if frame % 60 == 0:',
                     "        op('slices_ventana').module.vigilar()", '    return', ''])

w = op('/salida_slices') or op('/').create(windowCOMP, 'salida_slices')
sl = op('/salida_led') or op('/perform')
if sl is not None:
    w.nodeX, w.nodeY = sl.nodeX, sl.nodeY - 150
w.comment = 'Advanced Output en TD (modulos/led_slices). Cerrada y sin armar por default.'
w.par.winop = out.path
if hasattr(w.par, 'monitor'):
    w.par.monitor.expr = "op('%s').par.Monitor" % C.path
if hasattr(w.par, 'dpiscaling'):
    w.par.dpiscaling = 'native'
w.par.interact = False
vm.module.colocar(False)                    # solo deja los ajustes listos; NO abre
C.par.Estado = vm.module.estado()[0]
print('[ok] led_slices:', C.par.Lectura.eval(), '| efectos:', cadena or '(ninguno)', '| no reproduce:', C.par.Avisosxml.eval(), '| GLSL:', g.errors() or 'ok')
print('[ok] ventana', w.path, '· abierta:', w.isOpen, '· armada:', C.par.Slicesarmada.eval(), '·', C.par.Estado.eval())
