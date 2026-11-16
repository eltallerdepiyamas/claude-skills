# gen_companion_xl_camaras.py — VARIANTE PARA SHOWS CON CAMARAS (de LJ Metropolitan, 2026-11-14).
# El default de la plantilla es control/gen_companion_xl.py (solo visuales, pagina por canal del Beatstep).
# Esta usa familias MULTIVIEW / SPLITSCREEN / SINGLE SHOT, titulos y setlist si el show los tiene.
# (original: gen_companion_xl.py) — arma control/streamdeck_xl.companionconfig (Stream Deck XL, 8 x 4) a partir de
# control/show.json. NO toca gen_companion.py ni streamdeck.companionconfig (el de 15 botones): son dos
# configuraciones aparte; en Companion se importa una u otra.
#
# Diferencias con el de 15 botones:
#   - Una pagina por familia: MULTIVIEW (14), SPLITSCREEN (8) y SINGLE SHOT (6) caben enteras.
#   - FILA DE EMERGENCIA FIJA (fila de abajo, igual en TODAS las paginas):
#       MENU · AJUSTES · BLACKOUT · 1 CAM FULL · PALETA AUDIO · ENTRADA SPLIT · CANCION (12/26 + nombre) · TITULO AL AIRE
#   - Paginas nuevas: TITULOS (preparar cancion / creditos / titulos de control/titulos.txt) y SETLIST.
#   - Sin columna de flechas: se navega desde MENU (abajo a la izquierda en todas las paginas).
#
# BLACKOUT, 1 CAM FULL, TITULOS, SETLIST y MODO SHOW usan direcciones OSC nuevas (/td/xl/...): hay que
# correr UNA vez control/instalar_xl_osc.py en TouchDesigner (agrega esas direcciones al oscin1 y el
# feedback a Companion). Sin eso, todo lo demas del XL funciona igual que el de 15.
#
# Uso (fuera de TD, desde la carpeta del show):
#   python control/gen_companion_xl.py                       -> control/streamdeck_xl.companionconfig
#   python control/gen_companion_xl.py streamdeck:XXXXXXXX   -> fuerza el ID del XL (si hay varios Stream Deck)
import gzip, json, copy, os, random, string, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'companion_base_export.companionconfig')
SHOW = os.path.join(HERE, 'show.json')
DST = os.path.join(HERE, 'streamdeck_xl.companionconfig')
TITULOS_TXT = os.path.join(HERE, 'titulos.txt')
CREDITOS_TXT = os.path.join(HERE, 'creditos.txt')
SETLIST_TXT = os.path.join(HERE, 'setlist.txt')

if not os.path.exists(SHOW):
    sys.exit('No existe control/show.json: corre primero control/actualizar_companion.py en TouchDesigner.')
with open(SHOW, encoding='utf-8') as f:
    show = json.load(f)

cfg = json.loads(gzip.open(SRC).read().decode('utf-8'))
page1 = cfg['pages']['1']
template = page1['controls']['0']['1']
OSC = template['steps']['0']['action_sets']['down'][0]['connectionId']

TD_PORT = 7010                       # OSC In de TD; 7000 lo ocupa Resolume Arena
cfg['instances'][OSC]['config']['targetPort'] = TD_PORT
# la exportacion base trae el Stream Deck chico (5 x 3): el XL lo detecta Companion solo al conectarlo
cfg['surfaces'] = {}

COLS, ROWS = 8, 4                    # teclas de contenido + fila fija (columnas 0-7)
FILA_FIJA = ROWS - 1                 # fila de emergencia (la de abajo)
CONTENIDO = COLS * FILA_FIJA         # 24 botones de contenido por pagina
# Stream Deck + XL (asi lo ve Companion): 9 x 4 teclas · fila 4 = tira tactil (6 pantallitas) · fila 5 = 6 perillas.
# Las perillas y su pantallita van en estas columnas (huecos = sin control fisico).
GRID_COLS, GRID_ROWS = 9, 6
COL_NAV = 8                          # columna derecha: ▲ / ▼ / RESET / AUDIO
FILA_LCD, FILA_PERILLA = 4, 5
PERILLA_COLS = [0, 2, 3, 5, 6, 8]

FONT_SIZE = 18
LABEL_SIZE = 15
VALUE_SIZE = 18
LABEL_GRIS = 0xC8C8C8
BLANCO = 0xFFFFFF

def nid(n=21):
    return ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(n))

def V(v):
    return {'value': v, 'isExpression': False}

# (apagado, encendido) — mismos colores que el de 15
AZUL = (0x14243A, 0x2F7DE1)
MORADO = (0x2E1433, 0xA23BC4)
VERDE = (0x10301E, 0x22B35A)
GRIS = (0x262626, 0x262626)
NARANJA = (0x3A1E08, 0xE8741C)
AMARILLO = (0x3A3008, 0xD9A400)
SPLIT = (0x3A1A06, 0xE8731C)
ROJO = (0x3A0C0C, 0xE02424)
TURQUESA = (0x0E8C8C, 0x14B8B8)
ROSA = (0x3A0E2A, 0xE63C8A)
CREMA = (0x3A372E, 0xEDE8DB)         # titulos
NEGRO = (0x000000, 0x000000)

MIX_LABEL = 'AJUSTES'
# este show no lleva visuales ni FX (SIN_VISUALES en setup_ui.py): sin sus paginas, sin sus focos en AJUSTES
# y la perilla 6 es la Reaccion global del audio en vez del foco ESCENA / VISUAL / FX. False = como antes.
SIN_VISUALES = True

def osc(path, kind, value):
    if kind == 's':
        return {'id': nid(), 'definitionId': 'send_string', 'connectionId': OSC,
                'options': {'path': V(path), 'string': V(value)}, 'upgradeIndex': 3, 'type': 'action'}
    if kind == 'f':
        return {'id': nid(), 'definitionId': 'send_float', 'connectionId': OSC,
                'options': {'path': V(path), 'float': V(value)}, 'upgradeIndex': 3, 'type': 'action'}
    return {'id': nid(), 'definitionId': 'send_int', 'connectionId': OSC,
            'options': {'path': V(path), 'int': V(value)}, 'upgradeIndex': 3, 'type': 'action'}

def setvar(name, value):
    return {'id': nid(), 'definitionId': 'custom_variable_set_value', 'connectionId': 'internal',
            'options': {'name': V(name), 'create': V(False), 'value': V(str(value))}, 'type': 'action'}

def lit(var, value, color, op='eq'):
    return {'id': nid(), 'type': 'feedback', 'definitionId': 'variable_value', 'connectionId': 'internal',
            'options': {'variable': V('custom:' + var), 'op': V(op), 'value': V(str(value))},
            'isInverted': V(False),
            'styleOverrides': [{'overrideId': nid(), 'elementId': 'box0', 'elementProperty': 'color',
                                'override': V(color)}]}

def _text_layer(l, text, size_pct, y, h, valign, color, bold=False):
    l['text'] = V(text)
    l['x'], l['width'] = V(0), V(100)
    l['y'], l['height'] = V(y), V(h)
    l['fontsize'] = V(round(size_pct * 100.0 / h, 1))
    l['fontsizeAllowShrink'] = V(True)
    l['halign'] = V('center')
    l['valign'] = V(valign)
    l['color'] = V(color)
    l['outlineColor'] = V(color if bold else 0xFF000000)

def button(text, colors, actions, latch=None, value=None, bar=None):
    b = copy.deepcopy(template)
    layers = b['style']['layers']
    layers[0]['decoration'] = V('none')
    txt = None
    for l in layers:
        if l['type'] == 'box':
            l['color'] = V(colors[0])
        if l['type'] == 'text' and txt is None:
            txt = l
    if value is None:
        larga = max(len(p) for p in text.replace('\n', ' ').split(' '))
        _text_layer(txt, text, min(FONT_SIZE, FONT_SIZE * 8.0 / max(larga, 1)), 0, 100, 'center', BLANCO)
    else:
        val = copy.deepcopy(txt)
        val['id'], val['name'] = 'text1', 'Valor'
        _text_layer(txt, text + ':', LABEL_SIZE, 4, 40, 'bottom', LABEL_GRIS)
        _text_layer(val, value, VALUE_SIZE, 46, 50, 'top', BLANCO, bold=True)
        layers.append(val)
    if bar is not None:
        box = copy.deepcopy(next(l for l in layers if l['type'] == 'box'))
        box['id'], box['name'] = 'bar0', 'Barra'
        box['y'], box['height'] = V(88), V(12)
        box['color'] = V(bar)
        layers.insert(layers.index(txt), box)
    b['steps']['0']['action_sets']['down'] = actions
    b['feedbacks'] = [lit(latch[0], latch[1], colors[1])] if latch else []
    return b

def label(text):
    return text.upper().replace(' ', '\n')

def _streamdeck_id():
    """ID del Stream Deck XL en el Companion de esta compu. Prioridad: argumento -> el que diga XL en la base
    de datos de Companion -> el primer Stream Deck (avisa)."""
    for a in sys.argv[1:]:
        if a.startswith('streamdeck:'):
            return a
    try:
        import sqlite3, shutil, tempfile
        # la carpeta de la version mas nueva de Companion (v5.0, v5.1, ...): al actualizarse cambia de carpeta
        import glob
        dbs = glob.glob(os.path.join(os.environ.get('APPDATA', ''), 'companion', 'v*', 'db.sqlite'))
        dbs.sort(key=lambda p: [int(x) for x in os.path.basename(os.path.dirname(p))[1:].split('.') if x.isdigit()])
        db = dbs[-1] if dbs else ''
        tmp = tempfile.mkdtemp()
        for s in ('', '-wal', '-shm'):
            if os.path.exists(db + s):
                shutil.copy(db + s, os.path.join(tmp, 'db.sqlite' + s))
        c = sqlite3.connect(os.path.join(tmp, 'db.sqlite'))
        try:
            filas = [(r[0], str(r[1])) for r in c.execute('select id, value from surfaces')]
        except Exception:
            filas = [(r[0], '') for r in c.execute('select id from surfaces')]
        c.close()
        decks = [(i, v) for i, v in filas if i.startswith('streamdeck:')]
        xl = [i for i, v in decks if 'XL' in v.upper()]
        if xl:
            return xl[0]
        if decks:
            print('[aviso] no encontre un Stream Deck que diga XL en Companion; uso', decks[0][0],
                  '- si no es el XL: python control/gen_companion_xl.py <ID del XL>')
            return decks[0][0]
    except Exception as e:
        print('[aviso] no pude leer los Stream Deck de Companion:', e)
    return 'streamdeck:A00TA5372ITBKW'

STREAMDECK = _streamdeck_id()

def goto(page, surface='self'):
    """'Surface: Set to page'. page = nombre de pagina del generador; al final se cambia por su NUMERO."""
    return {'id': nid(), 'definitionId': 'set_page', 'connectionId': 'internal',
            'options': {'surfaceId': V(surface), 'page': V(page)}, 'type': 'action'}

def goto_expr(expr, surface='self'):
    return {'id': nid(), 'definitionId': 'set_page', 'connectionId': 'internal',
            'options': {'surfaceId': V(surface), 'page': {'value': expr, 'isExpression': True}},
            'type': 'action'}

# ---------------------------------------------------------------- botones (mismos que el de 15)
def escena(lbl, familia='multiview'):
    colors = {'singlecam': AMARILLO, 'splitscreen': SPLIT}.get(familia, AZUL)
    return button(label(lbl), colors, [goto('MIX'), osc('/td/Modoescena', 's', lbl), setvar('escena', lbl)],
                  latch=('escena', lbl))

def visual(v):
    return button(label(v['nombre']), MORADO,
                  [goto('MIX'), osc('/td/visual', 'i', v['base']), setvar('visual', v['base'])],
                  latch=('visual', v['base']))

def fx(f):
    return button(label(f['nombre']), NARANJA,
                  [goto('MIX'), osc('/td/fx', 'i', f['index']), setvar('fx', f['index'])],
                  latch=('fx', f['index']))

def step(text, par, delta):
    return button(text, GRIS, [osc('/td/inc/' + par, 'i', delta)])

def slot(s, i):
    return button('LUGAR %d' % i, VERDE, [osc('/td/inc/' + s['par'], 'i', 1)], value='$(custom:slot%d)' % i)

def unica(cam_label):
    return button(label(cam_label), VERDE, [osc('/td/Menu2', 's', cam_label), setvar('cam', cam_label)],
                  latch=('cam', cam_label))

def fila(xs, n=COLS):
    """Completa una fila de 8 (o recorta)."""
    xs = list(xs)[:n]
    return xs + [None] * (n - len(xs))

layouts = show.get('layouts', [])
slots = show.get('slots', [])
unicas = [unica(o) for o in (show.get('unica') or {}).get('opciones', [])]
lugares = [slot(s, i) for i, s in enumerate(slots, start=1)]
# CELDAS recorre el selector (2 fijas / 2 + Emilio / 3 todas) y SPLIT CAM cambia con cual
# de las fijas se parte Emilio. Sustituyen a CAMS -/+, que movian `Int` crudo y se
# desincronizaban del selector; el numero sigue saliendo en CAMS y la camara del split se
# ve en LUGAR 1 (Splitb = Slot1).
cams_menos = button('CELDAS', VERDE, [osc('/td/inc/Celdas', 'i', 1)])
cams_mas = button('SPLIT\nCAM', SPLIT, [osc('/td/inc/Splitb', 'i', 1)])
cams_info = button('CAMS', NEGRO, [], value='$(custom:cams)')
rotar = button('ROTAR', VERDE, [osc('/td/inc/Rotar', 'i', 1)], latch=('rotar', 'ON'), value='$(custom:rotar)')
split_entrada = lambda: button('ENTRADA\nSPLIT', SPLIT, [osc('/td/inc/splitabre', 'i', 1)],
                               latch=('splitabre', 'ON'), value='$(custom:splitabre_txt)')

PAGES = []   # (nombre, lista de botones de contenido: hasta 24, fila por fila)

def paginas(nombre, botones):
    """Una seccion -> paginas de 24 ('NOMBRE', 'NOMBRE 2'...). Con 26 escenas nunca pasa, pero por si acaso."""
    out = []
    for k in range(0, max(len(botones), 1), CONTENIDO):
        out.append((nombre if k == 0 else '%s %d' % (nombre, k // CONTENIDO + 1), botones[k:k + CONTENIDO]))
    return out

# MULTIVIEW: escenas en las filas 1-2 · fila 3 = lugares 1-5 + cams - / + + rotar
mv = [escena(l['label']) for l in layouts if l.get('familia', 'multiview') == 'multiview']
if mv:
    if len(mv) <= 16:
        PAGES.append(('MULTIVIEW', fila(mv, 16) + fila(lugares + [cams_menos, cams_mas, rotar])))
    else:
        PAGES += paginas('MULTIVIEW', mv)

# SPLITSCREEN: escenas · fila 2 = que camara es A (la de Emilio) · fila 3 = lugares B C D (ENTRADA va en la fila fija)
sp = [escena(l['label'], 'splitscreen') for l in layouts if l.get('familia') == 'splitscreen']
if sp:
    PAGES.append(('SPLITSCREEN', fila(sp) + fila(unicas) + fila(lugares[:3])))

# SINGLE SHOT: escenas · fila 2 = que camara se ve (Cam 1-6)
sc = [escena(l['label'], 'singlecam') for l in layouts if l.get('familia') == 'singlecam']
if sc:
    PAGES.append(('SINGLE SHOT', fila(sc) + fila(unicas)))

# CAMARAS: lugares + cams · rotacion · camara unica
cam_rows = fila(lugares + [cams_menos, cams_mas, cams_info])
cam_rows += fila([copy.deepcopy(rotar),
                  button('$(custom:rotar_menos)', GRIS, [osc('/td/rotarajuste', 'i', -1)]),
                  button('$(custom:rotar_mas)', GRIS, [osc('/td/rotarajuste', 'i', 1)]),
                  button('ROTACION', GRIS, [osc('/td/inc/Rotarmodo', 'i', 1)], value='$(custom:rotarinfo)')])
cam_rows += fila([copy.deepcopy(u) for u in unicas])
PAGES.append(('CAMARAS', cam_rows))

if not SIN_VISUALES:
    PAGES += paginas('VISUALES', [visual(v) for v in show.get('visuales', [])])
if not SIN_VISUALES and len(show.get('fx', [])) > 1:
    PAGES += paginas('FX', [fx(f) for f in show['fx']])

# ---------------------------------------------------------------- TITULOS y SETLIST (leen los .txt del show)
def _lineas(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8-sig') as f:
        return [l.rstrip('\n') for l in f]

def _corto(texto, n=18):
    texto = texto.strip()
    return texto if len(texto) <= n else texto[:n - 1].rstrip() + '.'

titulos = [l.split('|')[0].strip() for l in _lineas(TITULOS_TXT) if l.strip() and not l.strip().startswith('#')]
cartas, actual = [], []
for l in _lineas(CREDITOS_TXT) + ['']:
    if l.strip().startswith('#'):
        continue
    if l.strip():
        actual.append(l.split('|')[0].strip())
    elif actual:
        cartas.append(actual)
        actual = []
canciones = []
for l in _lineas(SETLIST_TXT):
    if l.strip() and not l.strip().startswith('#'):
        nombre, _, bloque = l.partition('|')
        canciones.append((nombre.strip(), bloque.strip().lower()))

def prep(texto, clave, colors=CREMA, value=None):
    """PREPARA un titulo (se ve en el preview de la UI, no sale). Sale con TITULO AL AIRE."""
    return button(texto, colors, [osc('/td/xl/titulo', 's', clave)], latch=('tituloclave', clave), value=value)

al_aire = lambda: button('TITULO\nAL AIRE', ROJO, [osc('/td/xl/tituloaire', 'i', 1)],
                         latch=('tituloaire', 'ON'), value='$(custom:tituloprep)')
tit = [prep('CANCION\nACTUAL', 'cancion', value='$(custom:cancion)'), prep('CREDITOS', 'creditos'),
       None, None, None, None, None, None]   # TITULO AL AIRE esta en la fila fija
tit += fila([prep('TITULO %d' % i, 't%d' % i, value=_corto(t, 12)) for i, t in enumerate(titulos[:8], start=1)])
tit += fila([prep('CARTA %d' % i, 'c%d' % i, value=_corto(c[-1] if len(c) > 1 else c[0], 12))
             for i, c in enumerate(cartas[:8], start=1)])
PAGES.append(('TITULOS', tit))

BLOQUE_COLOR = {'single': AMARILLO, 'multi': AZUL, 'split': SPLIT, 'circulo': AMARILLO}
BLOQUE_NOMBRE = {'single': 'PLANO\nSECUENCIA', 'multi': 'MULTIVIEW', 'split': 'SPLIT', 'circulo': 'CIRCULO'}
inicios = []
for n, (_nombre, bloque) in enumerate(canciones, start=1):
    if bloque and (not inicios or inicios[-1][1] != bloque):
        inicios.append((n, bloque))
setl = fila([button('< ANTERIOR', GRIS, [osc('/td/xl/cancion', 'i', -1)]),
             button('CANCION', NEGRO, [], value='$(custom:cancion)'),
             button('SIGUIENTE >', VERDE, [osc('/td/xl/cancion', 'i', 1)]),
             button('SIGUE', NEGRO, [], value='$(custom:cancionsig)'),
             None, None, None, prep('TITULO\nCANCION', 'cancion', value='$(custom:cancion)')])
# fila 2: saltar al inicio de cada bloque del setlist (1-10 single · 11-15 multi · 16-20 split · 21-26 circulo)
setl += fila([button(BLOQUE_NOMBRE.get(b, b.upper()), BLOQUE_COLOR.get(b, GRIS),
                     [osc('/td/xl/ircancion', 'i', n)], value='DESDE %d' % n) for n, b in inicios])
setl += fila([button('IR A\n1', GRIS, [osc('/td/xl/ircancion', 'i', 1)])])
PAGES.append(('SETLIST', setl))

# ---------------------------------------------------------------- AJUSTES (MIX)
TIPO_COLOR = {'MULTIVIEW': AZUL[1], 'SPLITSCREEN': SPLIT[1], 'SINGLE SHOT': AMARILLO[1], 'VISUAL': MORADO[1], 'FX': NARANJA[1]}

def por_tipo(b, extra=()):
    b['feedbacks'] = [lit('mix_foco', t, c) for t, c in TIPO_COLOR.items()] + list(extra)
    return b

def param(i):
    b = button('$(custom:mix_p%dn)' % i, GRIS, [osc('/td/audio', 'i', i)], value='$(custom:mix_p%dv)' % i)
    return por_tipo(b, [lit('mix_audio', i, VERDE[1])])

def foco(nombre, tipo, value, base_fb, lit_fb):
    b = button(nombre, GRIS, [osc('/td/foco', 's', tipo)], value=value)
    b['feedbacks'] = [lit(v, '', c, op='ne') for v, c in base_fb] + [lit('mix_foco', t, c) for t, c in lit_fb]
    return b

def ir(nombre):
    if not any(n == nombre for n, _b in PAGES):
        return None
    return button(label(nombre), (0x1A1A1A, 0x1A1A1A), [goto(nombre)])

FOCO_ESCENA = foco('ESCENA', 'layout', '$(custom:menu_mv)$(custom:menu_sp)$(custom:menu_sc)',
                   [('menu_mv', AZUL[0]), ('menu_sp', SPLIT[0]), ('menu_sc', AMARILLO[0])],
                   [('MULTIVIEW', AZUL[1]), ('SPLITSCREEN', SPLIT[1]), ('SINGLE SHOT', AMARILLO[1])])
FOCO_VISUAL = None if SIN_VISUALES else foco('VISUAL', 'visual', '$(custom:menu_vis)', [('menu_vis', MORADO[0])], [('VISUAL', MORADO[1])])
FOCO_FX = (foco('FX', 'fx', '$(custom:menu_fx)', [('menu_fx', NARANJA[0])], [('FX', NARANJA[1])])
           if any(n == 'FX' for n, _b in PAGES) else None)

reset_btn = lambda: button('RESET', ROJO, [osc('/td/reset', 'i', 1)], value='$(custom:mix_foconombre)')
MIX_GRID = fila([param(1), param(2), param(3), param(4), param(5),
                 button('SENS\n-', GRIS, [osc('/td/audiomult', 'i', -1)]),
                 button('SENS', NEGRO, [], value='$(custom:mix_audiomult)'),
                 button('SENS\n+', GRIS, [osc('/td/audiomult', 'i', 1)])])
MIX_GRID += fila([button('$(custom:mix_foco)', TURQUESA, [osc('/td/foco', 's', 'layout' if SIN_VISUALES else 'next')], value='$(custom:mix_foconombre)'),
                  FOCO_ESCENA, FOCO_VISUAL, FOCO_FX,
                  button('AUDIO', VERDE, [osc('/td/audio', 'i', 0)], latch=('mix_audioon', 'ON'), value='$(custom:mix_audioon)'),
                  reset_btn(), ir('CAMARAS'), button('VOLVER\nAL MENU', GRIS, [goto('MENU')])])
PAGES.append(('MIX', MIX_GRID))

# ---------------------------------------------------------------- ENSAYO y PANTALLAS (mismos botones)
ENSAYO_GRID = fila([button('DEMO', AZUL, [osc('/td/inc/Demo', 'i', 1)], latch=('demo', 'ON'),
                           value='$(custom:demo)\n$(custom:democada)'),
                    button('DEMO\n-1 S', GRIS, [osc('/td/inc/Democada', 'i', -1)]),
                    button('DEMO\n+1 S', GRIS, [osc('/td/inc/Democada', 'i', 1)]),
                    button('FUENTE', GRIS, [osc('/td/inc/Recsel', 'i', 1)], value='$(custom:recfuente)'),
                    button('REC', ROJO, [osc('/td/inc/Rec', 'i', 1)], latch=('rec', 'ON'), value='$(custom:rec)')])
PAGES.append(('ENSAYO', ENSAYO_GRID))
PANTALLAS_GRID = fila([button('SALIDA\nLED', VERDE, [osc('/td/show/inc/Salidaled', 'i', 1)], latch=('salidaled', 'ON'), value='$(custom:salidaled)'),
                       button('TEST\nPATTERN', ROJO, [osc('/td/show/inc/Pantallas', 'i', 1)], latch=('pantallas', 'ON'), value='$(custom:pantallas)'),
                       button('PATRON', GRIS, [osc('/td/show/inc/Patron', 'i', 1)], value='$(custom:patron)'),
                       button('MONITOR', GRIS, [osc('/td/show/inc/Monitor', 'i', 1)], value='$(custom:monitor)'),
                       button('FULL\nSCREEN', GRIS, [osc('/td/show/inc/Pantallacompleta', 'i', 1)], latch=('fullscreen', 'ON'), value='$(custom:fullscreen)'),
                       button('NDI', VERDE, [osc('/td/show/inc/Ndi', 'i', 1)], latch=('ndi', 'ON'), value='$(custom:ndi)')])
PANTALLAS_GRID += fila([button('GLOW', TURQUESA, [osc('/td/show/inc/Glowon', 'i', 1)], latch=('glowon', 'ON'), value='$(custom:glowon)'),
                        button('GLOW\nFORMA', GRIS, [osc('/td/show/inc/Glowforma', 'i', 1)], value='$(custom:glowforma)'),
                        button('GLOW\nVEL -', GRIS, [osc('/td/show/inc/Glowvel', 'f', -0.25)]),
                        button('GLOW\nVEL', NEGRO, [], value='$(custom:glowvel)'),
                        button('GLOW\nVEL +', GRIS, [osc('/td/show/inc/Glowvel', 'f', 0.25)])])
PAGES.append(('PANTALLAS', PANTALLAS_GRID))

# ---------------------------------------------------------------- MENU (pagina 1)
# AJUSTES va FIJO en fila 2 / col 1 (location 1/1/0): TD lo "presiona" (setup_mix_feedback.py,
# /location/1/1/0/press) cuando cambias algo desde el Beatstep o el mouse -> usa el ID del XL, no 'self'.
MENU_INFO = {'MULTIVIEW': (AZUL, 'menu_mv'), 'SPLITSCREEN': (SPLIT, 'menu_sp'), 'SINGLE SHOT': (AMARILLO, 'menu_sc'),
             'VISUALES': (MORADO, 'menu_vis'), 'FX': (NARANJA, 'menu_fx')}

def menu_btn(nombre):
    if nombre == 'CAMARAS':
        return button('CAMARAS', VERDE, [goto(nombre)], latch=('rotar', 'ON'),
                      value='$(custom:cams) CAMS\nROTAR $(custom:rotar)')
    if nombre == 'TITULOS':
        return button('TITULOS', CREMA, [goto(nombre)], latch=('tituloaire', 'ON'), value='$(custom:tituloprep)')
    if nombre == 'SETLIST':
        return button('SETLIST', (0x1A1A1A, 0x1A1A1A), [goto(nombre)], value='$(custom:cancion)')
    colors, var = MENU_INFO.get(nombre, (GRIS, None))
    if var is None:
        return button(label(nombre), GRIS, [goto(nombre)])
    return button(nombre, (colors[1], colors[1]), [goto(nombre)], value='$(custom:%s)' % var)

def mix_btn():
    return button(MIX_LABEL, TURQUESA, [goto('MIX', STREAMDECK)], value='$(custom:mix_foconombre)')

ORDEN_MENU = ['SINGLE SHOT', 'MULTIVIEW', 'SPLITSCREEN', 'CAMARAS', 'CIRCUIT B.', 'TITULOS', 'SETLIST', 'VISUALES', 'FX']
existentes = [n for n, _b in PAGES]
MENU_GRID = fila([menu_btn(n) for n in ORDEN_MENU if n in existentes])
MENU_GRID += fila([mix_btn(), reset_btn(),
                   button('ABRIR\nUI', ROSA, [osc('/td/inc/ui', 'i', 1)], latch=('ui', 'ON'), value='$(custom:ui)'),
                   button('PANTALLAS', (0x1A1A1A, ROJO[1]), [goto('PANTALLAS')], latch=('pantallas', 'ON'), value='$(custom:pantallas)'),
                   button('ENSAYO', (0x1A1A1A, ROJO[1]), [goto('ENSAYO')], latch=('rec', 'ON'), value='REC $(custom:rec)'),
                   button('MODO\nSHOW', (0x1A1A1A, ROJO[1]), [osc('/td/xl/modoshow', 'i', 1)], latch=('modoshow', 'ON'), value='$(custom:modoshow)'),
                   button('RESET\nFEEDBACK', ROJO, [osc('/td/resetfb', 'i', 1)]),
                   button('SALIDA\nLED', VERDE, [osc('/td/show/inc/Salidaled', 'i', 1)], latch=('salidaled', 'ON'),
                          value='$(custom:salidaled)')])
# orden de las paginas = orden del show (las flechas ▲ ▼ las recorren asi):
# plano secuencia (1-10) · multiview (11-15) · split (16-20) · camaras · titulos · setlist · ajustes · lo demas
ORDEN_PAGINAS = ['SINGLE SHOT', 'MULTIVIEW', 'SPLITSCREEN', 'CAMARAS', 'TITULOS', 'SETLIST', 'MIX',
                 'VISUALES', 'FX', 'ENSAYO', 'PANTALLAS']
def _familia(n):
    return n.rsplit(' ', 1)[0] if n[-1].isdigit() else n
PAGES.sort(key=lambda nb: ORDEN_PAGINAS.index(_familia(nb[0])) if _familia(nb[0]) in ORDEN_PAGINAS else 99)
PAGES.insert(0, ('MENU', MENU_GRID))

# ---------------------------------------------------------------- numeros de pagina
# CIRCUIT BENDING: pagina propia. POWER y los dos grupos de FX; los valores, en las perillas.
PAGES.append(('CIRCUIT B.', fila([
    button('POWER', NARANJA, [osc('/td/cb/power', 'i', 1)], latch=('cbpower', 'ON'),
           value='$(custom:cbpower)'),
    button('FX 2-3', NARANJA, [osc('/td/cb/fx2', 'i', 1)], latch=('cbfx2', 'ON'),
           value='$(custom:cbfx2)'),
    button('FX 4-5', NARANJA, [osc('/td/cb/fx4', 'i', 1)], latch=('cbfx4', 'ON'),
           value='$(custom:cbfx4)'),
])))

page_id = {name: (page1['id'] if i == 1 else nid()) for i, (name, _b) in enumerate(PAGES, start=1)}
page_no = {name: i for i, (name, _b) in enumerate(PAGES, start=1)}

def _primera_pag(prefijo):
    for n, i in page_no.items():
        if n == prefijo or n.startswith(prefijo + ' '):
            return i
    return None

def _back_escena_expr():
    mv_, sc_, sp_ = _primera_pag('MULTIVIEW'), _primera_pag('SINGLE SHOT'), _primera_pag('SPLITSCREEN')
    if mv_ and sc_ and sp_:
        return "$(custom:menu_sc) != '' ? %d : ($(custom:menu_sp) != '' ? %d : %d)" % (sc_, sp_, mv_)
    return str(mv_ or sc_ or sp_) if (mv_ or sc_ or sp_) else None

for btn, expr in ((FOCO_ESCENA, _back_escena_expr()),
                  (FOCO_VISUAL, str(_primera_pag('VISUALES')) if _primera_pag('VISUALES') else None),
                  (FOCO_FX, str(_primera_pag('FX')) if _primera_pag('FX') else None)):
    if btn is not None and expr is not None:
        btn['steps']['0']['action_sets']['down'].append(goto_expr(expr))

PAGE_BAR = {'MULTIVIEW': AZUL[1], 'SPLITSCREEN': SPLIT[1], 'SINGLE SHOT': AMARILLO[1], 'VISUALES': MORADO[1],
            'FX': NARANJA[1], 'CAMARAS': VERDE[1], 'TITULOS': CREMA[1], 'MIX': TURQUESA[1], 'MENU': GRIS[1]}

# ---------------------------------------------------------------- FILA DE EMERGENCIA (igual en todas)
def cancion_btn():
    """La cancion en la que vamos, a la vista en TODAS las paginas: '12/26' + nombre, pintada con el color
    de su bloque del setlist (amarillo plano secuencia · azul multiview · naranja split · crema circulo).
    Tocarla NO cambia de cancion (para que no se pase por accidente): lleva a SETLIST (< ANTERIOR / SIGUIENTE >)."""
    b = button('CANCION', (0x1A1A1A, 0x1A1A1A), [goto('SETLIST')], value='$(custom:cancion)')
    b['feedbacks'] = [lit('cancionbloque', k, c) for k, c in
                      (('single', AMARILLO[1]), ('multi', AZUL[1]), ('split', SPLIT[1]), ('circulo', CREMA[0]))]
    return b


def fila_fija(nombre):
    fam = nombre.rsplit(' ', 1)[0] if nombre[-1].isdigit() else nombre
    visto = MIX_LABEL if nombre == 'MIX' else nombre
    return [
        # MENU: dice en que pagina estas (barra de su color); tocarlo = volver al MENU
        button('MENU', NEGRO, [goto('MENU')], value=visto.replace(' ', '\n'), bar=PAGE_BAR.get(fam, GRIS[1])),
        mix_btn(),
        # BLACKOUT: fundido de 0.8 s a negro y de regreso (el mismo del boton de la UI; el candado no lo bloquea)
        button('BLACKOUT', ROJO, [osc('/td/xl/blackout', 'i', 1)], latch=('blackout', 'ON')),
        # 1 CAM FULL: toggle · pone layout_sc_limpio (la camara sola) · otro toque = la escena de antes
        # (el latch lo prende TD al mandar la escena: sin setvar, para que no parpadee al regresar)
        button('1 CAM\nFULL', AMARILLO, [osc('/td/xl/camfull', 'i', 1)],
               latch=('escena', 'Limpio')),
        button('PALETA\nAUDIO', TURQUESA, [osc('/td/inc/palaudio', 'i', 1)], latch=('palaudio', 'ON'),
               value='$(custom:palaudio)'),
        split_entrada(),
        cancion_btn(),
        al_aire(),
    ]

nombres = [n for n, _b in PAGES]

def visto(n):
    return (MIX_LABEL if n == 'MIX' else n).replace(' ', '\n')

def columna_nav(nombre):
    """Columna derecha, igual en todas: ▲ pagina anterior · ▼ siguiente (en el orden del show) · RESET · AUDIO."""
    k = nombres.index(nombre)
    ant = nombres[k - 1] if k > 0 else None
    sig = nombres[k + 1] if k + 1 < len(nombres) else None
    return [button('▲\n' + visto(ant), TURQUESA, [goto(ant)]) if ant else None,
            button('▼\n' + visto(sig), TURQUESA, [goto(sig)]) if sig else None,
            reset_btn(),
            button('AUDIO', VERDE, [osc('/td/audio', 'i', 0)], latch=('mix_audioon', 'ON'), value='$(custom:mix_audioon)')]

def perilla(izq, der, apretar):
    b = button('', NEGRO, apretar)
    b['options']['rotaryActions'] = True
    b['steps']['0']['action_sets']['rotate_left'] = izq
    b['steps']['0']['action_sets']['rotate_right'] = der
    return b

def tira_y_perillas():
    """Perillas 1-5 = los 5 sliders de lo enfocado en AJUSTES (girar = mover · apretar = valor de fabrica).
    Perilla 6 = foco ESCENA / VISUAL / FX (girar) · audio on / off (apretar).
    Pantallitas: nombre + valor, del color de la familia (verde = va con el audio). Tocar 1-5 = ese parametro
    con el audio on / off · tocar la 6 = siguiente foco."""
    lcd, per = [], []
    for i in range(1, 6):
        # tocar la pantallita = ese parametro va con el audio (verde); otro toque lo apaga (igual que en AJUSTES)
        b = button('$(custom:mix_p%dn)' % i, GRIS, [osc('/td/audio', 'i', i)], value='$(custom:mix_p%dv)' % i)
        lcd.append(por_tipo(b, [lit('mix_audio', i, VERDE[1])]))
        per.append(perilla([osc('/td/xl/dial%d' % i, 'i', -1)], [osc('/td/xl/dial%d' % i, 'i', 1)],
                           [osc('/td/xl/reset%d' % i, 'i', 1)]))
    if SIN_VISUALES:
        # perilla 6 = Reaccion global del audio (lo que se toca por track) · apretar = 100 % (de fabrica)
        lcd.append(button('REACCION', VERDE, [], value='$(custom:reaccion)'))
        per.append(perilla([osc('/td/xl/reaccion', 'i', -1)], [osc('/td/xl/reaccion', 'i', 1)],
                           [osc('/td/xl/reaccion', 'i', 0)]))
    else:
        b = button('$(custom:mix_foco)', TURQUESA, [osc('/td/xl/foco', 'i', 1)], value='$(custom:mix_foconombre)')
        lcd.append(por_tipo(b))
        per.append(perilla([osc('/td/xl/foco', 'i', -1)], [osc('/td/xl/foco', 'i', 1)], [osc('/td/audio', 'i', 0)]))
    return lcd, per

CB_DIALS = [('AMOUNT', 'cbamount'), ('PERIOD', 'cbperiod'), ('VAL STEP', 'cbvstep'),
            ('TX', 'cbtx'), ('TY', 'cbty')]

def tira_y_perillas_cb():
    """En la pagina CIRCUIT B. las perillas mueven SUS parametros, no los de la escena.
    Van por /td/cb/dialN, que escribe en la pagina Circuit del hub — el mismo lugar donde
    escribe el MIDImix (chopexec cb_midi), asi que los dos controladores mandan lo mismo
    y gana el ultimo que se movio. Apretar = valor de fabrica."""
    lcd, per = [], []
    for i, (nombre, var) in enumerate(CB_DIALS, start=1):
        lcd.append(button(nombre, NARANJA, [], value='$(custom:%s)' % var))
        per.append(perilla([osc('/td/cb/dial%d' % i, 'i', -1)], [osc('/td/cb/dial%d' % i, 'i', 1)],
                           [osc('/td/cb/reset%d' % i, 'i', 1)]))
    lcd.append(button('REACCION', VERDE, [], value='$(custom:reaccion)'))
    per.append(perilla([osc('/td/xl/reaccion', 'i', -1)], [osc('/td/xl/reaccion', 'i', 1)],
                       [osc('/td/xl/reaccion', 'i', 0)]))
    return lcd, per

todas = []
for n, b in PAGES:
    teclas = b + [None] * (CONTENIDO - len(b)) + fila_fija(n)
    celdas = {(k // COLS, k % COLS): x for k, x in enumerate(teclas)}
    for r, x in enumerate(columna_nav(n)):
        celdas[(r, COL_NAV)] = x
    lcd, per = tira_y_perillas_cb() if n == 'CIRCUIT B.' else tira_y_perillas()
    for c, x, y in zip(PERILLA_COLS, lcd, per):
        celdas[(FILA_LCD, c)], celdas[(FILA_PERILLA, c)] = x, y
    todas.append((n, celdas))

for _name, celdas in todas:
    for b in celdas.values():
        if not b:
            continue
        for lista in b['steps']['0']['action_sets'].values():
            for a in lista:
                if a.get('definitionId') == 'set_page' and a['options']['page']['value'] in page_no:
                    a['options']['page'] = V(page_no[a['options']['page']['value']])

out_pages = {}
for i, (name, celdas) in enumerate(todas, start=1):
    controls = {str(r): {} for r in range(GRID_ROWS)}
    for (r, c), b in celdas.items():
        if b is not None:
            controls[str(r)][str(c)] = b
    p = copy.deepcopy(page1)
    p['id'] = page_id[name]
    p['name'] = MIX_LABEL if name == 'MIX' else name
    p['gridSize'] = {'minRow': 0, 'maxRow': GRID_ROWS - 1, 'minColumn': 0, 'maxColumn': GRID_COLS - 1}
    p['controls'] = controls
    out_pages[str(i)] = p
cfg['pages'] = out_pages

# ---------------------------------------------------------------- variables (las del de 15 + las nuevas del XL)
VARS = [('escena', 'Escena activa', ''), ('visual', 'Visual activo', ''), ('fx', 'FX activo (switch23)', ''),
        ('cams', 'Camaras en multicam (lo manda TD)', '-'), ('cam', 'Camara unica (lo manda TD)', '')]
VARS += [('slot%d' % i, 'Camara del lugar %d (lo manda TD)' % i, '-') for i in range(1, 6)]
VARS += [('rotar', 'Rotar camaras ON/OFF (lo manda TD)', 'OFF'), ('rotarcada', 'Segundos por cambio (lo manda TD)', '-'),
         ('rotarmodo', 'Modo de rotacion (lo manda TD)', '-'), ('rotarinfo', 'Rotacion: modo y valor (lo manda TD)', '-'),
         ('rotar_menos', 'Texto del boton - de rotacion (lo manda TD)', 'MAS LENTO'),
         ('rotar_mas', 'Texto del boton + de rotacion (lo manda TD)', 'MAS RAPIDO')]
VARS += [('mix_foco', 'MIX: que se muestra (LAYOUT / VISUAL / FX)', '-'), ('mix_foconombre', 'MIX: nombre', '-')]
VARS += [('mix_p%dn' % i, 'MIX: nombre del parametro %d' % i, '-') for i in range(1, 6)]
VARS += [('mix_p%dv' % i, 'MIX: valor del parametro %d (%%)' % i, '') for i in range(1, 6)]
VARS += [('mix_ir', 'MIX: sube cuando cambia escena/visual/FX', '0'),
         ('mix_audio', 'MIX: parametro que va con el audio (1-5, 0 = apagado)', '0'),
         ('mix_audioon', 'MIX: audio ON / OFF', '-'), ('mix_audiomult', 'MIX: sensibilidad del audio', '-')]
VARS += [('bs_canal', 'MENU: canal-pad del ultimo pad del Beatstep', '-')]
VARS += [('menu_mv', 'MENU: layout multiview activo', ''), ('menu_sp', 'MENU: layout splitscreen activo', ''),
         ('menu_sc', 'MENU: layout single cam activo', ''), ('menu_vis', 'MENU: visual activo', ''), ('menu_fx', 'MENU: FX activo', '')]
VARS += [('demo', 'DEMO automatico ON/OFF (lo manda TD)', 'OFF'), ('democada', 'DEMO: segundos por escena', '-'),
         ('rec', 'Grabando ON/OFF (lo manda TD)', 'OFF'), ('recfuente', 'Que se graba (lo manda TD)', '-')]
VARS += [('palaudio', 'Paleta audio-reactivo ON/vacio (lo manda TD)', '')]
VARS += [('splitabre', 'SPLITSCREEN: split abierto ON/vacio (lo manda TD)', 'ON'),
         ('splitabre_txt', 'SPLITSCREEN: ABIERTO / EMILIO FULL (lo manda TD)', 'ABIERTO')]
VARS += [('pantallas', 'Test pattern ON/vacio (lo manda TD)', ''), ('ui', 'Ventana UI abierta ON/vacio (lo manda TD)', '')]
VARS += [('patron', 'PANTALLAS: patron activo', '-'), ('monitor', 'PANTALLAS: monitor elegido', '-'),
         ('fullscreen', 'PANTALLAS: full screen ON/vacio', ''), ('ndi', 'PANTALLAS: NDI ON/vacio', ''),
         ('glowon', 'PANTALLAS: Glow ON/vacio', ''), ('glowforma', 'PANTALLAS: forma del glow', '-'),
         ('glowvel', 'PANTALLAS: velocidad del glow', '-')]
# nuevas del XL (las manda /project2/show/xl_feedback, que instala control/instalar_xl_osc.py)
VARS += [('blackout', 'XL: BLACKOUT ON/vacio (lo manda TD)', ''),
         ('tituloaire', 'XL: titulo al aire ON/vacio (lo manda TD)', ''),
         ('tituloclave', 'XL: clave del titulo preparado: cancion / creditos / tN / cN (lo manda TD)', ''),
         ('tituloprep', 'XL: titulo preparado, texto corto (lo manda TD)', '-'),
         ('cancion', 'XL: cancion actual del setlist (lo manda TD)', '-'),
         ('cancionsig', 'XL: siguiente cancion del setlist (lo manda TD)', '-'),
         ('cancionbloque', 'XL: bloque de la cancion actual: single / multi / split / circulo (lo manda TD)', ''),
         ('modoshow', 'XL: MODO SHOW (candado) ON/vacio (lo manda TD)', ''),
         ('salidaled', 'XL: ventana de salida al LED abierta ON/vacio (lo manda TD)', ''),
         ('reaccion', 'XL: Reaccion global del audio en % (lo manda TD)', '100%')]
cfg['custom_variables'] = {
    n: {'description': d, 'defaultValue': dv,
        'persistCurrentValue': not n.startswith(('cams', 'slot', 'rotar', 'mix_', 'demo', 'rec', 'blackout', 'titulo', 'cancion')),
        'sortOrder': k}
    for k, (n, d, dv) in enumerate(VARS)}

with gzip.open(DST, 'wb') as f:
    f.write(json.dumps(cfg, separators=(',', ':')).encode('utf-8'))

chk = json.loads(gzip.open(DST).read())
for k, p in chk['pages'].items():
    print('%s %s' % (k, p['name']))
    for r in range(GRID_ROWS):
        celdas = []
        for c in range(GRID_COLS):
            b = p['controls'].get(str(r), {}).get(str(c))
            if b is None:
                celdas.append('.')
            else:
                t = [l['text']['value'].replace('\n', ' ') for l in b['style']['layers'] if l['type'] == 'text']
                celdas.append(t[0].rstrip(':'))
        print('   ' + ' | '.join('%-12s' % x[:12] for x in celdas))
print('Stream Deck:', STREAMDECK)
print('ok ->', DST)
