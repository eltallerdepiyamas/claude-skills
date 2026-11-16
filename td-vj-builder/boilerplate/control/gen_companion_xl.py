# gen_companion_xl.py — arma control/streamdeck_xl.companionconfig para el Stream Deck + XL
# (9 x 4 teclas, tira tactil de 6 pantallitas, 6 perillas) a partir de control/show.json.
# Show de solo visuales (sin escena_modular): una pagina por canal del Beatstep, igual que la UI de perform.
#
#   filas 1-2 (col 1-8)  los 16 pads del canal, mismo orden y numero que los thumbs y el Beatstep (8 x 2)
#   fila 3               COLOR A · COLOR B · AUDIO · SENS - · SENS · SENS + · RESET · RESET FEEDBACK
#   fila 4               BLACKOUT · MODO SHOW · ABRIR UI · THUMBS · BEATSTEP · DEMO · REC · AL AIRE
#   columna 9            pestanas: CH9 · CH10 · CH11 (la de la pagina en la que estas, encendida) · FUENTE
#   pantallitas 1-5      nombre y % de los 5 parametros del visual al aire (tocar = ese va con el audio)
#   perillas 1-5         mueven esos 5 parametros (2 % por clic) · apretar = valor de fabrica
#   perilla 6            Reaccion global del audio (hub) · apretar = 100 %
# Las filas 3-4 y las perillas son iguales en las tres paginas: memoria muscular.
#
# TD: correr UNA vez control/instalar_xl_osc.py con APPLY = True (perillas, blackout, modo show, reaccion
# y la marca streamdeck_xl, que evita que TD "presione" una tecla al cambiar de visual desde el Beatstep).
# Basado en gen_companion_xl.py de LJ Metropolitan (formato de perillas y tira del + XL leido de Companion 5.1).
#
# Uso (fuera de TD, desde la carpeta del show):
#   python control/gen_companion_xl.py                       -> control/streamdeck_xl.companionconfig
#   python control/gen_companion_xl.py streamdeck:XXXXXXXX   -> fuerza el ID (si hay varios Stream Deck)
import gzip, json, copy, os, random, string, sys, glob
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'companion_base_export.companionconfig')
SHOW = os.path.join(HERE, 'show.json')
BANCOS = os.path.join(HERE, 'bancos.json')
DST = os.path.join(HERE, 'streamdeck_xl.companionconfig')

visuales = []
for f in (BANCOS, SHOW):
    if os.path.exists(f):
        with open(f, encoding='utf-8') as h:
            d = json.load(h)
        visuales = d if isinstance(d, list) else d.get('visuales', [])
        if visuales:
            break
if not visuales:
    sys.exit('No hay visuales: corre builders/herramientas/ui_bancos.py en TD (escribe control/bancos.json).')

cfg = json.loads(gzip.open(SRC).read().decode('utf-8'))
page1 = cfg['pages']['1']
template = page1['controls']['0']['1']
OSC = template['steps']['0']['action_sets']['down'][0]['connectionId']
TD_PORT = 7010                       # OSC In de TD; 7000 lo ocupa Resolume Arena
cfg['instances'][OSC]['config']['targetPort'] = TD_PORT
cfg['surfaces'] = {}                 # la base trae el Stream Deck chico; el XL lo detecta Companion al conectarlo

GRID_COLS, GRID_ROWS = 9, 6          # + XL en Companion: 9 x 4 teclas · fila 4 = tira (6) · fila 5 = perillas (6)
FILA_LCD, FILA_PERILLA = 4, 5
PERILLA_COLS = [0, 2, 3, 5, 6, 8]    # columnas con pantallita / perilla fisica
COL_TABS = 8

FONT_SIZE, LABEL_SIZE, VALUE_SIZE = 18, 15, 18
LABEL_GRIS, BLANCO = 0xC8C8C8, 0xFFFFFF

# (apagado, encendido) — mismos colores que el de 15 y que la UI
MORADO = (0x2E1433, 0xA23BC4)        # visuales
VERDE = (0x10301E, 0x22B35A)         # audio
GRIS = (0x262626, 0x262626)
ROJO = (0x3A0C0C, 0xE02424)
TURQUESA = (0x0E8C8C, 0x14B8B8)      # navegacion
ROSA = (0x3A0E2A, 0xE63C8A)
AZUL = (0x14243A, 0x2F7DE1)
NEGRO = (0x000000, 0x000000)
COLOR_A = (0x5A0F18, 0xE01F3D)       # botones de paleta (solo el boton; los colores reales salen del hub)
COLOR_B = (0x0E3A2E, 0x6DC49A)


def nid(n=21):
    return ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(n))


def V(v):
    return {'value': v, 'isExpression': False}


def osc(path, kind, value):
    defs = {'s': ('send_string', 'string'), 'i': ('send_int', 'int'), 'f': ('send_float', 'float')}
    d, k = defs[kind]
    return {'id': nid(), 'definitionId': d, 'connectionId': OSC,
            'options': {'path': V(path), k: V(value)}, 'upgradeIndex': 3, 'type': 'action'}


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
    """text solo = un texto · con value = dos niveles (CATEGORIA: gris arriba, VALOR grande abajo)."""
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
        larga = max(len(p) for p in (text or ' ').replace('\n', ' ').split(' '))
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


def goto(page, surface='self'):
    """'Surface: Set to page'. page = nombre de pagina; al final se cambia por su NUMERO."""
    return {'id': nid(), 'definitionId': 'set_page', 'connectionId': 'internal',
            'options': {'surfaceId': V(surface), 'page': V(page)}, 'type': 'action'}


def perilla(izq, der, apretar):
    b = button('', NEGRO, apretar)
    b['options']['rotaryActions'] = True
    b['steps']['0']['action_sets']['rotate_left'] = izq
    b['steps']['0']['action_sets']['rotate_right'] = der
    return b


def _streamdeck_id():
    """ID del + XL en el Companion de esta compu (la carpeta v* mas nueva de Companion; prefiere el que diga XL)."""
    for a in sys.argv[1:]:
        if a.startswith('streamdeck:'):
            return a
    try:
        import sqlite3, shutil, tempfile
        dbs = glob.glob(os.path.join(os.environ.get('APPDATA', ''), 'companion', 'v*', 'db.sqlite'))
        dbs.sort(key=lambda p: [int(x) for x in os.path.basename(os.path.dirname(p))[1:].split('.') if x.isdigit()])
        db = dbs[-1] if dbs else ''
        tmp = tempfile.mkdtemp()
        for s in ('', '-wal', '-shm'):
            if os.path.exists(db + s):
                shutil.copy(db + s, os.path.join(tmp, 'db.sqlite' + s))
        c = sqlite3.connect(os.path.join(tmp, 'db.sqlite'))
        filas = [(r[0], str(r[1])) for r in c.execute('select id, value from surfaces')]
        c.close()
        decks = [(i, v) for i, v in filas if i.startswith('streamdeck:')]
        xl = [i for i, v in decks if 'XL' in v.upper()]
        if xl:
            return xl[0]
        if decks:
            print('[aviso] ningun Stream Deck dice XL en Companion; uso', decks[0][0])
            return decks[0][0]
    except Exception as e:
        print('[aviso] no pude leer los Stream Deck de Companion:', e)
    return 'self'


STREAMDECK = _streamdeck_id()

# ---------------------------------------------------------------- paginas por canal
GRUPOS = []                              # en el orden de bancos.json: OTROS (CH9), CIRCULARES (CH10), LOGOS (CH11)
for v in visuales:
    if v.get('grupo') and v['grupo'] not in GRUPOS:
        GRUPOS.append(v['grupo'])
CANAL = {g: next((v['canal'] for v in visuales if v.get('grupo') == g and v.get('canal')), 9 + k) for k, g in enumerate(GRUPOS)}
PAG = {g: 'CH%d %s' % (CANAL[g], g) for g in GRUPOS}


def visual(v):
    return button(v['nombre'].upper().replace(' ', '\n'), MORADO,
                  [osc('/td/visual', 'i', v['base']), setvar('visual', v['base'])],
                  latch=('visual', v['base']))


def tab(g, aqui):
    """Pestana de canal: la de la pagina en la que estas, encendida (y con barra)."""
    c = TURQUESA[1] if g == aqui else 0x10302E
    return button('CH%d' % CANAL[g], (c, c), [goto(PAG[g])], value=g, bar=0xFFFFFF if g == aqui else None)


fila3 = lambda: [
    button('COLOR\nA', COLOR_A, [osc('/td/rampa', 'i', 0)]),
    button('COLOR\nB', COLOR_B, [osc('/td/rampa', 'i', 1)]),
    button('AUDIO', VERDE, [osc('/td/audio', 'i', 0)], latch=('mix_audioon', 'ON'), value='$(custom:mix_audioon)'),
    button('SENS\n-', GRIS, [osc('/td/audiomult', 'i', -1)]),
    button('SENS', NEGRO, [], value='$(custom:mix_audiomult)'),
    button('SENS\n+', GRIS, [osc('/td/audiomult', 'i', 1)]),
    button('RESET', ROJO, [osc('/td/reset', 'i', 1)], value='$(custom:mix_foconombre)'),
    button('RESET\nFEEDBACK', ROJO, [osc('/td/resetfb', 'i', 1)]),
]
fila4 = lambda: [
    # BLACKOUT: fundido de 0.8 s a negro y de regreso (el de la UI; el candado no lo bloquea)
    button('BLACKOUT', ROJO, [osc('/td/xl/blackout', 'i', 1)], latch=('blackout', 'ON')),
    button('MODO\nSHOW', (0x1A1A1A, ROJO[1]), [osc('/td/xl/modoshow', 'i', 1)], latch=('modoshow', 'ON'),
           value='$(custom:modoshow)'),
    button('ABRIR\nUI', ROSA, [osc('/td/ui', 'i', 1)]),
    button('ACTUALIZAR\nTHUMBS', GRIS, [osc('/td/thumbs', 'i', 1)]),
    button('BEATSTEP', NEGRO, [], value='$(custom:bs_canal)'),
    button('DEMO', AZUL, [osc('/td/inc/Demo', 'i', 1)], latch=('demo', 'ON'), value='$(custom:demo)'),
    button('REC', ROJO, [osc('/td/inc/Rec', 'i', 1)], latch=('rec', 'ON'), value='$(custom:rec)'),
    button('AL AIRE', NEGRO, [], value='$(custom:mix_foconombre)'),
]


def tira_y_perillas(grupo=''):
    lcd, per = [], []
    for i in range(1, 6):
        b = button('$(custom:mix_p%dn)' % i, MORADO, [osc('/td/audio', 'i', i)], value='$(custom:mix_p%dv)' % i)
        b['feedbacks'] = [lit('mix_audio', i, VERDE[1])]          # verde = ese parametro va con el audio
        lcd.append(b)
        per.append(perilla([osc('/td/xl/dial%d' % i, 'i', -1)], [osc('/td/xl/dial%d' % i, 'i', 1)],
                           [osc('/td/xl/reset%d' % i, 'i', 1)]))
    if 'LOGOS' in grupo:      # en las paginas de logos la perilla 6 es el TAMANO LOGO estandar (show.Logotamano)
        lcd.append(button('TAMANO\nLOGO', ROJO, [osc('/td/xl/logotam', 'i', 0)], value='$(custom:logotam)'))
        per.append(perilla([osc('/td/xl/logotam', 'i', -1)], [osc('/td/xl/logotam', 'i', 1)],
                           [osc('/td/xl/logotam', 'i', 0)]))
        return lcd, per
    lcd.append(button('REACCION', VERDE, [osc('/td/xl/reaccion', 'i', 0)], value='$(custom:reaccion)'))
    per.append(perilla([osc('/td/xl/reaccion', 'i', -1)], [osc('/td/xl/reaccion', 'i', 1)],
                       [osc('/td/xl/reaccion', 'i', 0)]))
    return lcd, per


todas = []
for g in GRUPOS:
    pads = [visual(v) for v in visuales if v.get('grupo') == g][:16]
    pads += [None] * (16 - len(pads))
    celdas = {}
    for k, b in enumerate(pads + fila3() + fila4()):
        celdas[(k // 8, k % 8)] = b
    if len(GRUPOS) <= 3:
        for r, g2 in enumerate(GRUPOS[:3]):
            celdas[(r, COL_TABS)] = tab(g2, g)
        celdas[(3, COL_TABS)] = button('REC\nFUENTE', GRIS, [osc('/td/inc/Recsel', 'i', 1)], value='$(custom:recfuente)')
    else:
        # mas de 3 canales: filas 0-2 = canales de visuales, fila 3 = LOGOS (en una pagina de logos lleva al otro)
        vis = [x for x in GRUPOS if 'LOGO' not in x][:3]
        logos = [x for x in GRUPOS if 'LOGO' in x]
        for r, g2 in enumerate(vis):
            celdas[(r, COL_TABS)] = tab(g2, g)
        if logos:
            destino = logos[(logos.index(g) + 1) % len(logos)] if g in logos else logos[0]
            b = tab(destino, g)
            if g in logos:          # estas en logos: la tecla se ve encendida y lleva al otro canal de logos
                c = TURQUESA[1]
                b = button('CH%d\n>' % CANAL[destino], (c, c), [goto(PAG[destino])], value=g, bar=0xFFFFFF)
            celdas[(3, COL_TABS)] = b
    lcd, per = tira_y_perillas(g)
    for c, x, y in zip(PERILLA_COLS, lcd, per):
        celdas[(FILA_LCD, c)], celdas[(FILA_PERILLA, c)] = x, y
    todas.append((PAG[g], celdas))

page_id = {name: (page1['id'] if i == 1 else nid()) for i, (name, _c) in enumerate(todas, start=1)}
page_no = {name: i for i, (name, _c) in enumerate(todas, start=1)}
for _n, celdas in todas:
    for b in celdas.values():
        for lista in (b['steps']['0']['action_sets'].values() if b else []):
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
    p['name'] = name
    p['gridSize'] = {'minRow': 0, 'maxRow': GRID_ROWS - 1, 'minColumn': 0, 'maxColumn': GRID_COLS - 1}
    p['controls'] = controls
    out_pages[str(i)] = p
cfg['pages'] = out_pages

# ---------------------------------------------------------------- variables (las manda TD)
VARS = [('visual', 'Visual activo (base)', '')]
VARS += [('mix_foco', 'AJUSTES: que se muestra', '-'), ('mix_foconombre', 'AJUSTES: nombre de lo activo', '-')]
VARS += [('mix_p%dn' % i, 'Nombre del parametro %d del visual activo' % i, '-') for i in range(1, 6)]
VARS += [('mix_p%dv' % i, 'Valor del parametro %d (%%)' % i, '') for i in range(1, 6)]
VARS += [('mix_ir', 'Sube cuando cambia el visual', '0'),
         ('mix_audio', 'Parametro que va con el audio (1-5, 0 = apagado)', '0'),
         ('mix_audioon', 'Audio ON / OFF del visual activo', '-'), ('mix_audiomult', 'Sensibilidad del audio', '-')]
VARS += [('bs_canal', 'Canal-pad del ultimo pad del Beatstep', '-')]
VARS += [('demo', 'DEMO automatico ON/OFF', 'OFF'), ('rec', 'Grabando ON/OFF', 'OFF'), ('recfuente', 'Que se graba', '-')]
VARS += [('blackout', 'BLACKOUT ON/vacio (xl_feedback)', ''), ('modoshow', 'MODO SHOW ON/vacio (xl_feedback)', ''),
         ('reaccion', 'Reaccion global del audio en % (xl_feedback)', '100%'),
         ('logotam', 'Tamano estandar del logo en % del alto (xl_feedback)', '75%')]
cfg['custom_variables'] = {
    n: {'description': d, 'defaultValue': dv,
        'persistCurrentValue': not n.startswith(('mix_', 'demo', 'rec', 'blackout')),
        'sortOrder': k}
    for k, (n, d, dv) in enumerate(VARS)}

with gzip.open(DST, 'wb') as f:
    f.write(json.dumps(cfg, separators=(',', ':')).encode('utf-8'))

chk = json.loads(gzip.open(DST).read())
for k, p in chk['pages'].items():
    print('%s %s' % (k, p['name']))
    for r in range(GRID_ROWS):
        fila = []
        for c in range(GRID_COLS):
            b = p['controls'].get(str(r), {}).get(str(c))
            t = [l['text']['value'].replace('\n', ' ') for l in b['style']['layers'] if l['type'] == 'text'] if b else []
            fila.append((t[0].rstrip(':') if t and t[0] else ('(perilla)' if b else '.')))
        print('   ' + ' | '.join('%-11s' % x[:11] for x in fila))
print('Stream Deck:', STREAMDECK)
print('ok ->', DST)
