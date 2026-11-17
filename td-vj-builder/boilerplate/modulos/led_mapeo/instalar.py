# led_mapeo — mapea el visual a los tableros de una pantalla LED, en el orden en que los recibe el procesador.
# Arma /project1/led (no toca color_final ni ndiout1):
#   master_banner   (Columnas*Tablero) x (Filas*Tablero)  -> lo que va al procesador (fila de arriba = 1a fila)
#   preview_banner  (N*Tablero) x Tablero                 -> los N tableros en una linea, como cuelgan (con guias)
# Pagina Banner: Columnas · Filas · Tablero (px) · Modo · Zoom.
#   cuadros  = cada tablero muestra el cuadro central del visual (sellos y circulares completos)
#   franja   = una franja horizontal del visual recorre los tableros de corrido
#   palnorte = bloque del centro cortado en tableros (Pal Norte 2026: 4x3 de 1920x1080; las figuras salen partidas)
# Primera instalacion: la cuadricula sale de proyecto.json -> "led": {"columnas", "filas", "tablero"} (default 4x3 de 256).
# Si existe el /project1/banner viejo (Casa Bacardi 2026-11), lo renombra a /project1/led.
# Modulo del boilerplate: modulos/led_mapeo. Instalar con modulos/modulos.py.
import json, os

LED = '/project1/led'
P1 = op('/project1')
FUENTE = op('/project1/color_final')

SHADER = r'''// led_mapeo — visual -> tableros (uGrid: columnas, filas, px por tablero)
uniform vec4 uCfg;   // x modo (0 cuadros, 1 franja, 2 palnorte), y vista (0 procesador, 1 en linea), z zoom, w guias
uniform vec4 uGrid;  // x columnas, y filas, z px por tablero
out vec4 fragColor;

void main() {
    float COLS = max(uGrid.x, 1.0);
    float ROWS = max(uGrid.y, 1.0);
    float N = COLS * ROWS;
    vec2 uv = vUV.st;
    float idx;
    vec2 lu;   // uv local del tablero, origen abajo-izquierda
    if (uCfg.y < 0.5) {
        float c = floor(uv.x * COLS);
        float rTop = ROWS - 1.0 - floor(uv.y * ROWS);   // fila 0 = arriba
        idx = rTop * COLS + c;
        lu = vec2(fract(uv.x * COLS), fract(uv.y * ROWS));
    } else {
        idx = floor(uv.x * N);
        lu = vec2(fract(uv.x * N), uv.y);
    }
    vec2 res = uTD2DInfos[0].res.zw;
    int m = int(uCfg.x + 0.5);
    vec2 s;
    if (m == 0) {
        float a = res.y / res.x;   // cuadro central del visual
        s = vec2(0.5 + (lu.x - 0.5) * a * uCfg.z, 0.5 + (lu.y - 0.5) * uCfg.z);
    } else if (m == 1) {
        float bandH = (res.x / N) / res.y;   // franja N:1 centrada
        s = vec2((idx + lu.x) / N, 0.5 + (lu.y - 0.5) * bandH);
    } else {
        // Pal Norte: bloque x 416..1432, y 128..894 (desde arriba) de 1920x1080, cortado en COLS x ROWS
        float c = mod(idx, COLS);
        float rTop = floor(idx / COLS);
        vec2 o = vec2(416.0, 128.0) / vec2(1920.0, 1080.0);
        vec2 t = vec2(1016.0 / COLS, 766.0 / ROWS) / vec2(1920.0, 1080.0);
        s = vec2(o.x + (c + lu.x) * t.x, 1.0 - (o.y + (rTop + 1.0 - lu.y) * t.y));
    }
    vec4 col = texture(sTD2DInputs[0], s);
    if (any(lessThan(s, vec2(0.0))) || any(greaterThan(s, vec2(1.0)))) col = vec4(0.0, 0.0, 0.0, 1.0);
    if (uCfg.w > 0.5) {
        float T = max(uGrid.z, 2.0);
        vec2 px = lu * T;
        float borde = step(px.x, 1.0) + step(T - 1.0, px.x) + step(px.y, 1.0) + step(T - 1.0, px.y);
        col.rgb = mix(col.rgb, vec3(0.35), clamp(borde, 0.0, 1.0) * 0.8);
    }
    col.a = 1.0;
    fragColor = TDOutputSwizzle(col);
}
'''


def nuevo(comp, tipo, nombre, x, y):
    o = comp.op(nombre)
    if o is None:
        o = comp.create(tipo, nombre)
    o.nodeX, o.nodeY = x, y
    return o


def bind(g, bloques):
    """[(nombre, [x, y, z, w])] -> vecN de un GLSL TOP (expresion si es texto, numero si no)."""
    g.seq.vec.numBlocks = max(g.seq.vec.numBlocks, len(bloques))
    for i, (nombre, vals) in enumerate(bloques):
        getattr(g.par, 'vec%dname' % i).val = nombre
        for c, v in zip('xyzw', vals):
            p = getattr(g.par, 'vec%dvalue%s' % (i, c))
            if isinstance(v, str):
                p.expr = v
            else:
                p.expr = ''
                p.val = v


def config_proyecto():
    ruta = project.folder + '/proyecto.json'
    try:
        return json.load(open(ruta, encoding='utf-8')).get('led', {}) if os.path.exists(ruta) else {}
    except Exception:
        return {}


if FUENTE is None:
    print('[fallo] no existe /project1/color_final')
else:
    viejo = op('/project1/banner')
    if op(LED) is None and viejo is not None:
        viejo.name = 'led'
        print('[ok] /project1/banner -> /project1/led')
    nd = op('/project1/ndiout1')
    bx = (nd.nodeX if nd else FUENTE.nodeX + 200)
    by = (nd.nodeY if nd else FUENTE.nodeY) - 250
    b = nuevo(P1, baseCOMP, 'led', bx, by)
    b.color = (0.55, 0.2, 0.2)
    b.comment = 'Salida LED: visual -> tableros (master_banner al procesador). modulos/led_*'

    pg = next((p for p in b.customPages if p.name == 'Banner'), None) or b.appendCustomPage('Banner')
    cfg = config_proyecto()
    for n, label, d in (('Columnas', 'Columnas (tableros)', cfg.get('columnas', 4)),
                        ('Filas', 'Filas (tableros)', cfg.get('filas', 3)),
                        ('Tablero', 'Tablero (px por lado)', cfg.get('tablero', 256))):
        if not hasattr(b.par, n):
            pg.appendInt(n, label=label)
            getattr(b.par, n).default = d
            getattr(b.par, n).val = d
        getattr(b.par, n).min, getattr(b.par, n).clampMin = 1, True
    b.par.Columnas.normMax = b.par.Filas.normMax = 16
    b.par.Tablero.normMin, b.par.Tablero.normMax = 32, 512
    if not hasattr(b.par, 'Modo'):
        pg.appendMenu('Modo', label='Modo')
    b.par.Modo.menuNames = ['cuadros', 'franja', 'palnorte']
    b.par.Modo.menuLabels = ['Cuadros (visual completo por tablero)', 'Franja corrida', 'Bloque del centro (Pal Norte)']
    if not hasattr(b.par, 'Zoom'):
        pg.appendFloat('Zoom', label='Zoom cuadro')
        b.par.Zoom.default = 1.0
        b.par.Zoom.val = 1.0
    b.par.Zoom.normMin, b.par.Zoom.normMax = 0.3, 1.0
    b.par.Zoom.min, b.par.Zoom.clampMin = 0.1, True
    pg.sort('Columnas', 'Filas', 'Tablero', 'Modo', 'Zoom')

    src = nuevo(b, selectTOP, 'fuente', 0, 0)
    src.par.top = FUENTE.path
    dat = nuevo(b, textDAT, 'banner_pixel', 0, -200)
    dat.text = SHADER
    grid = ['parent().par.Columnas', 'parent().par.Filas', 'parent().par.Tablero', 0]
    salidas = (('master_banner', 'parent().par.Columnas * parent().par.Tablero', 'parent().par.Filas * parent().par.Tablero', 0, 0, 200),
               ('preview_banner', 'parent().par.Columnas * parent().par.Filas * parent().par.Tablero', 'parent().par.Tablero', 1, 1, -100))
    for nombre, w, h, vista, guias, y in salidas:
        g = nuevo(b, glslTOP, nombre + '_glsl', 200, y)
        g.inputConnectors[0].connect(src)
        g.par.pixeldat = dat.name
        g.par.outputresolution = 'custom'
        g.par.resolutionw.expr, g.par.resolutionh.expr = w, h
        g.par.inputfiltertype = 'linear'
        bind(g, [('uCfg', ['parent().par.Modo.menuIndex', vista, 'parent().par.Zoom', guias]), ('uGrid', grid)])
        n = nuevo(b, nullTOP, nombre, 400, y)
        n.inputConnectors[0].connect(g)
        o = nuevo(b, outTOP, 'out_' + nombre, 600, y)
        o.inputConnectors[0].connect(n)
    if b.op('lienzo_led') is None:
        b.par.opviewer = './master_banner'
    if hasattr(b.par, 'nodeview'):
        b.par.nodeview = 'opviewer'
    b.viewer = True
    mb = b.op('master_banner')
    mb.cook(force=True)
    print('[ok] led_mapeo: %s | %dx%d tableros de %d px | master_banner %dx%d | modo=%s' % (
        b.path, b.par.Columnas.eval(), b.par.Filas.eval(), b.par.Tablero.eval(), mb.width, mb.height, b.par.Modo.eval()))
    for nombre in ('master_banner_glsl', 'preview_banner_glsl'):
        e = b.op(nombre).errors() or b.op(nombre).warnings()
        if e:
            print('[aviso]', nombre, e)
    # legibilidad: secciones con titulo (modulos/secciones.py)
    exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
    secciones(b, 'Banner', [('Hcuadricula', 'Cuadricula de la pantalla', ['Columnas', 'Filas', 'Tablero']),
                            ('Hmapeo', 'Como se reparte el visual', ['Modo', 'Zoom'])])
