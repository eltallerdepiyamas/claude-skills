# ─────────────────────────────────────────────────────────────
# setup_test_pantallas.py — generador de patrones de prueba para calibrar / alinear pantallas.
#
# Crea en /project2/show:
#   test_pantallas      (containerCOMP con un GLSL TOP que renderiza el patron + test_out)
#   pagina 'Pantallas' en /project2/show con:
#     Pantallas         (Toggle)  -> prendido = la salida final es el test pattern (NDI) y se abre la ventana
#     Patron            (Menu)    -> Barras, Grid, Blanco, Negro, Ajedrez, Gradiente, Gamma
#     Monitor           (Menu)    -> Primary, Monitor 2, Monitor 3, Monitor 4, Monitor 5, Secondary
#     Pantallacompleta  (Toggle)  -> fullscreen sobre el monitor elegido (sin bordes)
#
# Inserta en /project1:
#   test_in       (selectTOP, apunta a /project2/show/test_pantallas/test_out)
#   test_switch   (switchTOP, entradas: color_final + test_in; .index = show.Pantallas)
#   perform_test  (windowCOMP, abre test_switch en el monitor elegido cuando Pantallas = ON)
#   y reconecta ndiout1 <- test_switch (antes era color_final -> ndiout1).
#
# Resolucion del test: igual a la del show (W/H de la pestaña Resolucion de /project2/show).
# Las escenas / visuales / FX ya respetan show.W/H via expr, asi que un cambio de resolucion los
# actualiza a todos de manera proporcional (el aspect lo manejan los shaders con uResolution).
# Idempotente: nodos con tag 'tdvj_test_pantallas' se rehacen.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_test_pantallas.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────
import os

SHADER = 'shaders/test_pantallas.frag'
TAG = 'tdvj_test_pantallas'

show = op('/project2/show')
if show is None:
    raise SystemExit('No existe /project2/show')

# ---------- 1. subred test_pantallas en /project2/show ----------
c = show.op('test_pantallas') or show.create(containerCOMP, 'test_pantallas')
c.tags.add(TAG)
c.nodeX, c.nodeY = -500, -400
c.par.w, c.par.h = 320, 180

# borrar nodos previos tageados dentro de c (nombres primero: destroy invalida refs)
for nm in [n.name for n in c.children]:
    nn = c.op(nm)
    if nn is not None and TAG in nn.tags:
        nn.destroy()

pix = c.create(textDAT, 'test_pixel')
pix.tags.add(TAG)
pix.par.file = SHADER
pix.par.syncfile = True
pix.nodeX, pix.nodeY = -300, 100

gl = c.create(glslTOP, 'glsl_test')
gl.tags.add(TAG)
gl.par.pixeldat = pix
gl.par.resolutionw.expr = "op('/project2/show').par.W"
gl.par.resolutionh.expr = "op('/project2/show').par.H"
gl.par.outputresolution = 'custom'
gl.nodeX, gl.nodeY = -100, 100
# uniforms: GLSL TOP no pasa uResolution/uTime automáticamente (eso es del GLSL Multi); hay que declararlo
gl.par.vec0name = 'uModo'
gl.par.vec0valuex.expr = "int(op('/project2/show').par.Patron.menuIndex)"
gl.par.vec1name = 'uResolution'
gl.par.vec1valuex.expr = "op('/project2/show').par.W"
gl.par.vec1valuey.expr = "op('/project2/show').par.H"
gl.par.vec2name = 'uTime'
gl.par.vec2valuex.expr = 'absTime.seconds'
gl.par.vec3name = 'uGlowforma'
gl.par.vec3valuex.expr = "int(op('/project2/show').par.Glowforma.menuIndex)"
# vec4 ya existe para uGlowvel
gl.par.vec4name = 'uGlowvel'
gl.par.vec4valuex.expr = "op('/project2/show').par.Glowvel"
gl.par.vec5name = 'uGlowon'
gl.par.vec5valuex.expr = "int(op('/project2/show').par.Glowon.eval())"
gl.par.vec6name = 'uContorno'
gl.par.vec6valuex.expr = "op('/project2/show').par.Grosorcontorno"

# ---------- cargador de imagen ----------
img = c.op('test_img') or c.create(moviefileinTOP, 'test_img')
img.tags.add(TAG)
img.nodeX, img.nodeY = -300, -80
img.par.file.expr = "op('/project2/show').par.Imagenarchivo.eval()"
img.par.outputresolution = 'custom'
img.par.resolutionw.expr = "op('/project2/show').par.W"
img.par.resolutionh.expr = "op('/project2/show').par.H"
# conectar la imagen como input del GLSL (sTD2DInputs[0] en el shader)
for conn in gl.inputConnectors:
    try: conn.disconnect()
    except Exception: pass
gl.inputConnectors[0].connect(img)

out = c.create(nullTOP, 'test_out')
out.tags.add(TAG)
out.inputConnectors[0].connect(gl)
out.nodeX, out.nodeY = 150, 100

# ---------- 2. pagina 'Pantallas' en /project2/show ----------
pg = next((g for g in show.customPages if g.name == 'Pantallas'), None) or show.appendCustomPage('Pantallas')

def _ensure(pg, name, label, append, **kw):
    for p in pg.pars:
        if p.name == name:
            return p
    tup = append(name, label=label)
    p = tup[0] if isinstance(tup, (list, tuple)) else tup
    for k, v in kw.items():
        setattr(p, k, v)
    return p

def _ensure_header(pg, name, label):
    for p in pg.pars:
        if p.name == name:
            return p
    tup = pg.appendHeader(name, label=label)
    return tup[0] if isinstance(tup, (list, tuple)) else tup

# ── SALIDA ──────────────────────────────────────────────────────────────
_ensure_header(pg, 'Sepsalida', 'Salida')
p_on = _ensure(pg, 'Pantallas', 'Prendido (ON = sale test + abre ventana)', pg.appendToggle)
p_mon = _ensure(pg, 'Monitor', 'Monitor', pg.appendMenu,
                menuNames=['primary', 'monitor2', 'monitor3', 'monitor4', 'monitor5', 'secondary'],
                menuLabels=['Primary', 'Monitor 2', 'Monitor 3', 'Monitor 4', 'Monitor 5', 'Secondary'])
p_full = _ensure(pg, 'Pantallacompleta', 'Pantalla completa (sin bordes)', pg.appendToggle)
if p_full.default is None or p_full.val == p_full.default == 0:
    p_full.val = True
p_ndi = _ensure(pg, 'Ndi', 'NDI a Resolume (ON = envia)', pg.appendToggle)
if p_ndi.default is None or (p_ndi.val == 0 and p_ndi.default == 0):
    p_ndi.val = True
_nd = op('/project1/ndiout1')
if _nd is not None and hasattr(_nd.par, 'active'):
    _nd.par.active.expr = "op('/project2/show').par.Ndi.eval()"

# ── TEST PATTERN ───────────────────────────────────────────────────────
_ensure_header(pg, 'Septest', 'Test pattern')
# 'contorno' (2026-11-14): el borde exacto del lienzo en blanco, para cuadrar el LED.
# Mismo dibujo que la escena layout_sc_outline, pero sin pasar por la cadena del show.
_PATRONES = [('barras', 'Barras SMPTE'), ('empty', 'Empty (negro)'),
             ('imagen', 'Imagen cargada'), ('contorno', 'Contorno de pantalla')]
p_pat = _ensure(pg, 'Patron', 'Patron', pg.appendMenu,
                menuNames=[n for n, _ in _PATRONES],
                menuLabels=[l for _, l in _PATRONES])
p_pat.menuNames = [n for n, _ in _PATRONES]
p_pat.menuLabels = [l for _, l in _PATRONES]
# grosor del contorno, en PIXELES (no en fraccion: el lienzo es 3.6:1 y saldria disparejo)
_nuevo_g = not any(x.name == 'Grosorcontorno' for x in pg.pars)
p_gc = _ensure(pg, 'Grosorcontorno', 'Contorno: grosor (px)', pg.appendFloat)
p_gc.min, p_gc.max, p_gc.normMin, p_gc.normMax = 1.0, 40.0, 1.0, 40.0
p_gc.clampMin = True
if _nuevo_g:
    p_gc.val = 4.0
p_img = _ensure(pg, 'Imagenarchivo', 'Imagen (archivo)', pg.appendFile)

# ── GLOW ───────────────────────────────────────────────────────────────
_ensure_header(pg, 'Sepglow', 'Glow')
p_glowon = _ensure(pg, 'Glowon', 'Prendido', pg.appendToggle)
if p_glowon.default is None or (p_glowon.val == 0 and p_glowon.default == 0):
    p_glowon.val = True
    p_glowon.default = True
p_forma = _ensure(pg, 'Glowforma', 'Forma del glow', pg.appendMenu,
                  menuNames=['linea', 'circulo', 'horizontal', 'vertical'],
                  menuLabels=['Linea diagonal', 'Circulo expandiendo', 'Barra horizontal', 'Barra vertical'])
p_forma.menuNames = ['linea', 'circulo', 'horizontal', 'vertical']
p_forma.menuLabels = ['Linea diagonal', 'Circulo expandiendo', 'Barra horizontal', 'Barra vertical']
p_vel = _ensure(pg, 'Glowvel', 'Velocidad del glow', pg.appendFloat)
p_vel.normMin = 0.0
p_vel.normMax = 3.0
if p_vel.val == 0.0 and p_vel.default == 0.0:
    p_vel.val = 1.0
    p_vel.default = 1.0

# orden final de la pagina (TD respeta este orden al dibujar)
pg.sort('Sepsalida', 'Pantallas', 'Monitor', 'Pantallacompleta', 'Ndi',
        'Septest', 'Patron', 'Grosorcontorno', 'Imagenarchivo',
        'Sepglow', 'Glowon', 'Glowforma', 'Glowvel')

# ---------- 3. switch en /project1 antes de ndiout1 ----------
p1 = op('/project1')
nd = p1.op('ndiout1')
cf = p1.op('color_final')
if nd is None or cf is None:
    raise SystemExit('No existe /project1/ndiout1 o /project1/color_final')

ti = p1.op('test_in') or p1.create(selectTOP, 'test_in')
ti.tags.add(TAG)
ti.par.top = '/project2/show/test_pantallas/test_out'
ti.nodeX, ti.nodeY = cf.nodeX, cf.nodeY + 180

sw = p1.op('test_switch') or p1.create(switchTOP, 'test_switch')
sw.tags.add(TAG)
# limpiar conexiones (iterando sobre inputConnectors, sin indexar)
for conn in sw.inputConnectors:
    try:
        conn.disconnect()
    except Exception:
        pass
sw.inputConnectors[0].connect(cf)
sw.inputConnectors[1].connect(ti)
sw.par.index.expr = "int(op('/project2/show').par.Pantallas.eval())"
sw.nodeX, sw.nodeY = cf.nodeX + 220, cf.nodeY

# reconectar ndiout1 <- test_switch
for conn in nd.inputConnectors:
    try:
        conn.disconnect()
    except Exception:
        pass
nd.inputConnectors[0].connect(sw)

# ---------- 4. Window COMP: abre el test en el monitor elegido ----------
pw = p1.op('perform_test') or p1.create(windowCOMP, 'perform_test')
pw.tags.add(TAG)
pw.nodeX, pw.nodeY = sw.nodeX, sw.nodeY + 180
pw.par.winop = sw
pw.par.monitor.expr = "op('/project2/show').par.Monitor.menuIndex"
pw.par.borders.expr = "0 if op('/project2/show').par.Pantallacompleta.eval() else 1"
pw.par.size = 'custom'
if hasattr(pw.par, 'winw'):
    pw.par.winw.expr = "op('/project2/show').par.W"
if hasattr(pw.par, 'winh'):
    pw.par.winh.expr = "op('/project2/show').par.H"
# abre/cierra segun el toggle Pantallas (parameterexecute dispara el pulse correcto)
_watcher = p1.op('perform_test_watch') or p1.create(parameterexecuteDAT, 'perform_test_watch')
_watcher.tags.add(TAG)
_watcher.nodeX, _watcher.nodeY = pw.nodeX + 220, pw.nodeY
_watcher.par.ops = '/project2/show'
_watcher.par.pars = 'Pantallas'
_watcher.par.valuechange = True
_watcher.text = '''# abre/cierra /project1/perform_test segun /project2/show.Pantallas
def onValueChange(par, prev):
    pw = op('/project1/perform_test')
    if pw is None:
        return
    if par.eval():
        pw.par.winopen.pulse()
    else:
        pw.par.winclose.pulse()
'''

print('[OK] Test pantallas listo:')
print('     Pestaña "Pantallas" en /project2/show (Prendido + Patron + Monitor + Pantalla completa)')
print('     Switch en /project1/test_switch (color_final | test_in) -> ndiout1')
print('     Ventana /project1/perform_test (se abre en el monitor elegido al prender Pantallas)')
print('     Boton Companion: regenerar con python control/gen_companion.py')
