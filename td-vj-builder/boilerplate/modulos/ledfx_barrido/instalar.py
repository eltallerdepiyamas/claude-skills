# ledfx_barrido — rampa con halo que barre la pantalla LED (venia del test de pantallas de Little Jesus, "glow").
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
B = op('/project1/led')
S = '/project2/show'

SHADER = r'''// barrido_led — rampa animada con halo, sumada encima de la cadena LED
uniform vec4 uGlow;     // x on · y forma · z velocidad · w intensidad
uniform vec4 uCfg;      // x espacio (0 banner, 1 pantalla) · y tiempo
uniform vec4 uTinta;    // rgb
uniform vec4 uGrid;     // x columnas, y filas
out vec4 fragColor;

void main() {
    vec2 uv = vUV.st;
    vec4 src = texture(sTD2DInputs[0], uv);
    if (uGlow.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    float COLS = max(uGrid.x, 1.0);
    float ROWS = max(uGrid.y, 1.0);

    // P en unidades de "alto de tablero = 1"; W = ancho en esas unidades
    vec2 P; float W;
    if (uCfg.x < 0.5) {
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
    float dist;
    if (forma == 0) {                         // linea diagonal
        float ang = 0.55;
        float cs = cos(ang), sn = sin(ang);
        float d = P.x * cs + P.y * sn;
        float total = W * cs + sn;
        dist = d - (fract(t * 0.18) * (total + 0.6) - 0.3);
    } else if (forma == 1) {                  // circulo expandiendo desde el centro
        float r = length(P - vec2(W * 0.5, 0.5));
        float maxR = sqrt(W * W * 0.25 + 0.25) + 0.1;
        dist = r - fract(t * 0.18) * (maxR + 0.2);
    } else if (forma == 2) {                  // barra horizontal (sube)
        dist = P.y - (fract(t * 0.15) * 1.6 - 0.3);
    } else {                                  // barra vertical (recorre de lado)
        dist = P.x - (fract(t * 0.15) * (W + 0.6) - 0.3);
    }

    float core  = exp(-abs(dist) * 60.0);
    float halo  = exp(-abs(dist) * 6.0);
    float trail = smoothstep(0.0, 0.25, -dist) * exp(dist * 2.8);
    float pulse = 0.7 + 0.3 * sin(t * 2.6);

    vec3 tinta = uTinta.rgb;
    vec3 g = tinta * halo * 0.40 * pulse + tinta * trail * 0.50 + min(tinta * 1.8, vec3(1.0)) * core * 1.40;
    fragColor = TDOutputSwizzle(vec4(src.rgb + g * uGlow.w, 1.0));
}
'''

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


if B is None or B.op('led_cadena') is None:
    print('[fallo] falta /project1/led con led_salida: instala antes led_salida')
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
    p.menuLabels = ['Tableros en linea (como cuelgan)', 'Imagen del mapeo']
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

    dat = nuevo(B, textDAT, 'barrido_led_pixel', 1000, 500)
    dat.text = SHADER
    g = nuevo(B, glslTOP, 'barrido_led', 1000, 400)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.par.format = 'rgba16float'
    g.seq.vec.numBlocks = 4
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
    g.par.vec3valuex.expr, g.par.vec3valuey.expr = 'parent().par.Columnas', 'parent().par.Filas'
    g.tags.add('ledfx')
    g.store('orden', 20)
    cadena = B.op('led_cadena').module.encadenar()
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
                             ('Hbalook', 'Como se ve', ['Barridovel', 'Barridoint', 'Barridotinta'])])
    orden_paginas(B, ['LED', 'Chaser', 'Barrido', 'Banner'])
