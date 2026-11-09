# gen_companion.py — arma control/streamdeck.companionconfig a partir de control/show.json.
#
# show.json lo escribe TD (control/actualizar_companion.py) con lo que tiene ESTE show:
# layouts (menu Modoescena), visuales y FX con contrato, y los slots de camara.
# Paginas: MULTIVIEW · SINGLE CAM (layouts de 1 camara + Cam 1-6) · VISUALES · FX · CAMARAS (lugares 1-5)
#          · MIX (los 5 parametros de lo activo con su %).
# 12 botones por pagina; una seccion vacia no saca pagina.
#
# Uso (fuera de TD, desde la carpeta del show):
#   python control/gen_companion.py      -> importar control/streamdeck.companionconfig en Companion
import gzip, json, copy, os, random, string, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(errors='replace')   # la consola de Windows no imprime las flechas

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'companion_base_export.companionconfig')
SHOW = os.path.join(HERE, 'show.json')
DST = os.path.join(HERE, 'streamdeck.companionconfig')

if not os.path.exists(SHOW):
    sys.exit('No existe control/show.json: corre primero control/actualizar_companion.py en TouchDesigner.')
with open(SHOW, encoding='utf-8') as f:
    show = json.load(f)
# el Stream Deck se acomoda al proyecto: sin escena_modular no hay paginas de camaras ni escenas
_cfg = os.path.join(HERE, '..', 'proyecto.json')
SOLO_VISUALES = os.path.exists(_cfg) and not json.load(open(_cfg, encoding='utf-8')).get('modulos', {}).get('escena_modular', True)

cfg = json.loads(gzip.open(SRC).read().decode('utf-8'))
page1 = cfg['pages']['1']
template = page1['controls']['0']['1']
OSC = template['steps']['0']['action_sets']['down'][0]['connectionId']

# puerto del OSC In de TD; 7000 lo ocupa Resolume Arena
TD_PORT = 7010
cfg['instances'][OSC]['config']['targetPort'] = TD_PORT
nav = {'0': {'0': {'type': 'pageup'}}, '1': {'0': {'type': 'pagenum'}}, '2': {'0': {'type': 'pagedown'}}}

FONT_SIZE = 18   # % de la altura del botón; igual en todos (se probó 100 = "lo más grande que quepa" y no gustó)
# jerarquía (2026-11-04): botones con CATEGORÍA: (chica, gris) arriba y VALOR (grande, "negritas") abajo
LABEL_SIZE = 15  # % de la altura del botón
VALUE_SIZE = 18
LABEL_GRIS = 0xC8C8C8
# Companion 5 no dibuja negritas (el campo "weight" existe pero se ignora): un contorno del mismo color
# que el texto lo engrosa = "negritas falsas"
BLANCO = 0xFFFFFF

# Flechas propias que se saltan MIX (a MIX solo se entra eligiendo un layout / visual / FX).
# Usan la accion "Set page" (ya en formato Companion 5). Con False quedan las flechas normales de Companion.
NAV_SIN_MIX = True
PER_PAGE = 12    # 3 filas x 4 columnas (la columna 0 es navegacion)

def nid(n=21):
    return ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(n))

def V(v):
    return {'value': v, 'isExpression': False}

# (apagado, encendido)
AZUL    = (0x14243A, 0x2F7DE1)
MORADO  = (0x2E1433, 0xA23BC4)
VERDE   = (0x10301E, 0x22B35A)
GRIS    = (0x262626, 0x262626)
NARANJA = (0x3A1E08, 0xE8741C)
AMARILLO = (0x3A3008, 0xD9A400)   # SINGLE CAM (azul = MULTIVIEW)
ROJO     = (0x3A0C0C, 0xE02424)   # grabando
TURQUESA = (0x0E8C8C, 0x14B8B8)   # navegacion: 'que estoy viendo' (titulo de AJUSTES y su acceso)

# nombre que se ve de la pagina de los 5 parametros (internamente sigue siendo 'MIX')
MIX_LABEL = 'AJUSTES'

def osc(path, kind, value):
    if kind == 's':
        return {'id': nid(), 'definitionId': 'send_string', 'connectionId': OSC,
                'options': {'path': V(path), 'string': V(value)}, 'upgradeIndex': 3, 'type': 'action'}
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
    """size_pct = % de la altura del BOTON (Companion lo mide contra la capa: se reescala)."""
    l['text'] = V(text)
    l['x'], l['width'] = V(0), V(100)
    l['y'], l['height'] = V(y), V(h)
    l['fontsize'] = V(round(size_pct * 100.0 / h, 1))
    l['fontsizeAllowShrink'] = V(True)
    l['halign'] = V('center')
    l['valign'] = V(valign)
    l['color'] = V(color)
    l['outlineColor'] = V(color if bold else 0xFF000000)    # 0xFF...... = contorno transparente


def button(text, colors, actions, latch=None, value=None, bar=None):
    """text solo = un texto al 18 %.  Con value = dos niveles: 'TEXT:' (15 %, gris) / VALUE (18 %, negritas).
    bar = color de una barra abajo ("estas aqui" en la etiqueta de cada pagina)."""
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
        larga = max(len(p) for p in text.replace('\n', ' ').split(' '))    # palabra entera: nunca partirla
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
        layers.insert(layers.index(txt), box)       # debajo de los textos
    b['steps']['0']['action_sets']['down'] = actions
    b['feedbacks'] = [lit(latch[0], latch[1], colors[1])] if latch else []
    return b

def label(text):
    return text.upper().replace(' ', '\n')

def _streamdeck_id():
    """ID del Stream Deck en el Companion de esta compu (lo lee de su base de datos, de una copia)."""
    try:
        import sqlite3, shutil, tempfile
        db = os.path.join(os.environ.get('APPDATA', ''), 'companion', 'v5.0', 'db.sqlite')
        tmp = tempfile.mkdtemp()
        for s in ('', '-wal', '-shm'):
            if os.path.exists(db + s):
                shutil.copy(db + s, os.path.join(tmp, 'db.sqlite' + s))
        c = sqlite3.connect(os.path.join(tmp, 'db.sqlite'))
        ids = [r[0] for r in c.execute("select id from surfaces") if r[0].startswith('streamdeck:')]
        c.close()
        if ids:
            return ids[0]
    except Exception as e:
        print('[aviso] no pude leer el Stream Deck de Companion:', e)
    return 'streamdeck:A00TA5372ITBKW'

STREAMDECK = _streamdeck_id()

def goto(page, surface='self'):
    """Accion interna de Companion 5 "Surface: Set to page".
    Companion 5 solo lee dos opciones: surfaceId y page. page = NUMERO de pagina (o 'back' / 'forward');
    un nombre como 'MIX' no lo entiende y el boton no hace nada (por eso no saltaba).
    Aqui page puede ser el nombre de una pagina del generador: al final se cambia por su numero."""
    return {'id': nid(), 'definitionId': 'set_page', 'connectionId': 'internal',
            'options': {'surfaceId': V(surface), 'page': V(page)},
            'type': 'action'}

def _por_numero(a, numero):
    a['options']['page'] = V(numero)

# al elegir un layout / visual / FX el Stream Deck salta a MIX (sus 5 parametros); VOLVER regresa
# el salto a AJUSTES va primero: el Stream Deck cambia de pagina al instante
def escena(lbl, familia='multiview'):
    # manda la ETIQUETA: reordenar el menu en TD no rompe el boton
    colors = AMARILLO if familia == 'singlecam' else AZUL
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
    # cada toque pasa a la siguiente camara; el texto muestra la actual (feedback de TD)
    return button('LUGAR %d' % i, VERDE, [osc('/td/inc/' + s['par'], 'i', 1)], value='$(custom:slot%d)' % i)

def unica(cam_label):
    # elige la camara que se ve en los layouts SINGLE CAM (no cambia de escena)
    return button(label(cam_label), VERDE, [osc('/td/Menu2', 's', cam_label), setvar('cam', cam_label)],
                  latch=('cam', cam_label))

def row(buttons):
    """Completa la fila de 4 para que lo siguiente empiece en fila nueva."""
    return buttons + [None] * ((4 - len(buttons) % 4) % 4)

def display(text):
    # solo muestra; TD actualiza la variable (setup_companion_feedback.py)
    return button(text, (0x000000, 0x000000), [])

def chunks(name, buttons):
    """Una seccion -> paginas de 12: 'LAYOUTS', 'LAYOUTS 2'..."""
    out = []
    for k in range(0, len(buttons), PER_PAGE):
        out.append((name if k == 0 else '%s %d' % (name, k // PER_PAGE + 1), buttons[k:k + PER_PAGE]))
    return out

layouts = show.get('layouts', [])
PAGES = []
if SOLO_VISUALES:
    vistos = show.get('visuales', [])
    grupos = [g for g in ('VISUALES', 'LOGOS') if any(v.get('grupo') == g for v in vistos)]
    for g in grupos:             # el show define sus paginas (control/bancos.json)
        PAGES += chunks(g, [visual(v) for v in vistos if v.get('grupo') == g])
    if not grupos:               # bases 1-8 = con logo · 9-16 = generativos
        PAGES += chunks('LOGOS', [visual(v) for v in vistos if v['base'] <= 8])
        PAGES += chunks('GENERATIVOS', [visual(v) for v in vistos if v['base'] > 8])
else:
    # MULTIVIEW: layouts de varias camaras
    PAGES += chunks('MULTIVIEW', [escena(l['label']) for l in layouts if l.get('familia', 'multiview') == 'multiview'])
    # SINGLE CAM: arriba los layouts de una camara, abajo que camara se ve en ellos (Cam 1-6)
    single = row([escena(l['label'], 'singlecam') for l in layouts if l.get('familia') == 'singlecam'])
    single += [unica(o) for o in (show.get('unica') or {}).get('opciones', [])]
    PAGES += chunks('SINGLE CAM', single)
    PAGES += chunks('VISUALES', [visual(v) for v in show.get('visuales', [])])
    if len(show.get('fx', [])) > 1:                      # solo "Sin FX" = no hay FX todavia
        PAGES += chunks('FX', [fx(f) for f in show['fx']])
    # CAMARAS (3 filas):  LUGAR 1-4  ·  LUGAR 5 + camaras en multicam (- / + / cuantas)  ·  rotacion
    cam_buttons = [slot(s, i) for i, s in enumerate(show.get('slots', []), start=1)]
    cam_buttons += [step('CAMS\n-', 'Int', -1), step('CAMS\n+', 'Int', 1), button('CAMS', (0x000000, 0x000000), [], value='$(custom:cams)')]
    cam_buttons = row(cam_buttons)
    # rotacion: -/+ ajustan segun el modo (tiempo: lento / rapido · audio: sensibilidad); los textos los manda TD
    cam_buttons += [button('ROTAR', VERDE, [osc('/td/inc/Rotar', 'i', 1)], latch=('rotar', 'ON'), value='$(custom:rotar)'),
                    button('$(custom:rotar_menos)', GRIS, [osc('/td/rotarajuste', 'i', -1)]),
                    button('$(custom:rotar_mas)', GRIS, [osc('/td/rotarajuste', 'i', 1)]),
                    # info siempre visible; tocarlo cambia de modo (Por tiempo / Con el audio)
                    button('ROTACION', GRIS, [osc('/td/inc/Rotarmodo', 'i', 1)], value='$(custom:rotarinfo)')]
    PAGES += chunks('CAMARAS', cam_buttons)

# MIX: pagina completa de 5 x 3 (sin columna de navegacion)
#   fila 1  P1 P2 P3 P4 P5       color de su tipo; verde = el que va con el audio (tocar = audio a ese / apagar)
#   fila 2  TITULO  ESCENA  VISUAL  FX  VOLVER
#           (TITULO turquesa = lo que ves; tocarlo recorre ESCENA -> VISUAL -> FX. ESCENA / VISUAL / FX cambian
#            lo que se ajusta SIN salir de AJUSTES; para elegir otra escena / visual / FX: VOLVER AL MENU)
#   fila 3  AUDIO  SENS-  SENS+  SENS  CAMARAS
# Los valores los manda TD (setup_mix_feedback.py); se enfoca solo lo ultimo que cambiaste.
TIPO_COLOR = {'MULTIVIEW': AZUL[1], 'SINGLE CAM': AMARILLO[1], 'VISUAL': MORADO[1], 'FX': NARANJA[1]}

def por_tipo(b, extra=()):
    """Pinta el boton con el color del tipo enfocado; extra = feedbacks que mandan encima (van despues)."""
    b['feedbacks'] = [lit('mix_foco', t, c) for t, c in TIPO_COLOR.items()] + list(extra)
    return b

def param(i):
    b = button('$(custom:mix_p%dn)' % i, GRIS, [osc('/td/audio', 'i', i)], value='$(custom:mix_p%dv)' % i)
    return por_tipo(b, [lit('mix_audio', i, VERDE[1])])

def titulo():
    # tocarlo pasa al siguiente: LAYOUT -> VISUAL -> FX
    # color propio (turquesa = navegacion): no se confunde con los grupos (azul, amarillo, morado, naranja, verde)
    return button('$(custom:mix_foco)', TURQUESA, [osc('/td/foco', 's', 'next')], value='$(custom:mix_foconombre)')

def ir(nombre):
    """Acceso directo a otra pagina del Stream Deck (vacio si esa pagina no existe en este show)."""
    if not any(n == nombre for n, _b in PAGES):
        return None
    return button(label(nombre), (0x1A1A1A, 0x1A1A1A), [goto(nombre)])

def foco(nombre, tipo, value, base_fb, lit_fb):
    """AJUSTES: cambia QUE se ajusta sin salir de la pagina (/td/foco). Muestra lo activo de ese grupo;
    tenue con el color de su grupo y encendido cuando es el que estas viendo."""
    b = button(nombre, GRIS, [osc('/td/foco', 's', tipo)], value=value)
    b['feedbacks'] = [lit(v, '', c, op='ne') for v, c in base_fb] + [lit('mix_foco', t, c) for t, c in lit_fb]
    return b

# fila 2: ESCENA (azul multiview / amarillo single cam: solo hay una escena activa) · VISUAL · FX (si hay)
FOCO_ESCENA = None if SOLO_VISUALES else foco('ESCENA', 'layout', '$(custom:menu_mv)$(custom:menu_sc)',
                   [('menu_mv', AZUL[0]), ('menu_sc', AMARILLO[0])],
                   [('MULTIVIEW', AZUL[1]), ('SINGLE CAM', AMARILLO[1])])
FOCO_VISUAL = foco('VISUAL', 'visual', '$(custom:menu_vis)', [('menu_vis', MORADO[0])], [('VISUAL', MORADO[1])])
FOCO_FX = (foco('FX', 'fx', '$(custom:menu_fx)', [('menu_fx', NARANJA[0])], [('FX', NARANJA[1])])
           if any(n == 'FX' for n, _b in PAGES) else None)

MIX_GRID = [param(1), param(2), param(3), param(4), param(5),
            titulo(), FOCO_ESCENA, FOCO_VISUAL, FOCO_FX, button('VOLVER\nAL MENU', GRIS, [goto('MENU')]),
            button('AUDIO', VERDE, [osc('/td/audio', 'i', 0)], latch=('mix_audioon', 'ON'), value='$(custom:mix_audioon)'),
            button('SENS\n-', GRIS, [osc('/td/audiomult', 'i', -1)]),
            button('SENS\n+', GRIS, [osc('/td/audiomult', 'i', 1)]),
            button('SENS', (0x000000, 0x000000), [], value='$(custom:mix_audiomult)'), ir('CAMARAS')]
PAGES.append(('MIX', MIX_GRID))

# MENU (pagina 1, la de arranque): un boton por pagina con lo que esta activo ahi (lo manda TD,
# setup_mix_feedback.py). Se enciende la pagina donde esta lo activo. VOLVER y la etiqueta de cada
# pagina regresan aqui. El boton MIX va FIJO en fila 2 / col 1: TD lo "presiona" (/location/1/1/0/press)
# cuando cambias algo desde el Beatstep o el mouse -> por eso usa el ID del Stream Deck y no 'self'.
MENU_INFO = {'MULTIVIEW': (AZUL, 'menu_mv'), 'SINGLE CAM': (AMARILLO, 'menu_sc'),
             'VISUALES': (MORADO, 'menu_vis'), 'FX': (NARANJA, 'menu_fx')}

def menu_btn(nombre):
    base = nombre.rsplit(' ', 1)[0] if nombre.rsplit(' ', 1)[-1].isdigit() else nombre   # 'MULTIVIEW 2'
    if base == 'CAMARAS':
        return button('CAMARAS', VERDE, [goto(nombre)], latch=('rotar', 'ON'),
                      value='$(custom:cams) CAMS\nROTAR $(custom:rotar)')
    colors, var = MENU_INFO.get(base, (GRIS, None))
    if var is None:
        return button(label(nombre), GRIS, [goto(nombre)])
    b = button(nombre, colors, [goto(nombre)], value='$(custom:%s)' % var)
    b['feedbacks'] = [lit(var, '', colors[1], op='ne')]
    return b

def mix_btn_new():
    return button(MIX_LABEL, TURQUESA, [goto('MIX', STREAMDECK)], value='$(custom:mix_foconombre)')

mix_btn = mix_btn_new()
MENU_GRID = [menu_btn(n) for n, _b in PAGES if n != 'MIX']
fila = lambda xs: xs + [None] * (5 - len(xs))
# ENSAYO (para armar el show, no para el vivo): DEMO (recorre las escenas moviendo sus parametros;
# setup_demo.py) · segundos - / + · FUENTE (que se graba) · REC (rojo = grabando). Se entra desde el MENU
# (fila 3, col 5), que se pone ROJO mientras graba para que no se quede grabando por accidente.
ENSAYO_GRID = [button('DEMO', AZUL, [osc('/td/inc/Demo', 'i', 1)], latch=('demo', 'ON'),
                      value='$(custom:demo)\n$(custom:democada)'),
               button('DEMO\n-1 S', GRIS, [osc('/td/inc/Democada', 'i', -1)]),
               button('DEMO\n+1 S', GRIS, [osc('/td/inc/Democada', 'i', 1)]),
               button('FUENTE', GRIS, [osc('/td/inc/Recsel', 'i', 1)], value='$(custom:recfuente)'),
               button('REC', ROJO, [osc('/td/inc/Rec', 'i', 1)], latch=('rec', 'ON'), value='$(custom:rec)')]
ENSAYO_GRID = ENSAYO_GRID + fila([]) + fila([mix_btn_new()])[:4] + [button('VOLVER\nAL MENU', GRIS, [goto('MENU')])]
ensayo_btn = button('ENSAYO', (0x1A1A1A, ROJO[1]), [goto('ENSAYO')], latch=('rec', 'ON'), value='REC $(custom:rec)')
reset_btn = button('RESET', ROJO, [osc('/td/reset', 'i', 1)], value='$(custom:mix_foconombre)')   # sliders + movimiento + feedback + videos
ui_btn = button('ABRIR\nUI', GRIS, [osc('/td/ui', 'i', 1)])   # /perform como ventana aparte
beatstep_btn = button('BEATSTEP', GRIS, [], value='$(custom:bs_canal)')   # ultimo pad: canal-pad + que controla (solo informa)
if SOLO_VISUALES:
    # navegacion primero: fila 2 / col 1 sigue siendo AJUSTES (TD la presiona)
    MENU_GRID = (fila(MENU_GRID[:3] + [button('COLOR A', ROJO, [osc('/td/rampa', 'i', 0)]),
                                       button('COLOR B', TURQUESA, [osc('/td/rampa', 'i', 1)])])
                 + [mix_btn, reset_btn, button('RESET\nFEEDBACK', ROJO, [osc('/td/resetfb', 'i', 1)]),
                    button('ACTUALIZAR\nTHUMBS', GRIS, [osc('/td/thumbs', 'i', 1)]), beatstep_btn]
                 + fila([ui_btn])[:4] + [ensayo_btn])
else:
    MENU_GRID = fila(MENU_GRID[:5]) + fila([mix_btn] + MENU_GRID[5:9]) + [reset_btn, beatstep_btn, ui_btn, None] + [ensayo_btn]
PAGES.insert(0, ('MENU', MENU_GRID))
PAGES.append(('ENSAYO', ENSAYO_GRID))

# cada pagina lleva su ID (la primera conserva el de la exportacion base); las acciones goto('NOMBRE')
# saltan por NUMERO de pagina (expresion), que es lo que sobrevive al importar
page_id = {name: (page1['id'] if i == 1 else nid()) for i, (name, _b) in enumerate(PAGES, start=1)}
page_no = {name: i for i, (name, _b) in enumerate(PAGES, start=1)}
for _name, buttons in PAGES:
    for b in buttons:
        for a in (b['steps']['0']['action_sets']['down'] if b else []):
            if a.get('definitionId') == 'set_page' and a['options']['page']['value'] in page_no:
                _por_numero(a, page_no[a['options']['page']['value']])

PAGE_BAR = {'MULTIVIEW': AZUL[1], 'SINGLE CAM': AMARILLO[1], 'VISUALES': MORADO[1], 'FX': NARANJA[1],
            'CAMARAS': VERDE[1]}
out_pages = {}
for i, (name, buttons) in enumerate(PAGES, start=1):
    if name in ('MIX', 'MENU', 'ENSAYO'):
        # pagina completa 5 x 3: sin navegacion (MIX: VOLVER esta en la fila 2)
        controls = {'0': {}, '1': {}, '2': {}}
        places = [(r, c) for r in range(3) for c in range(5)]
    else:
        controls = copy.deepcopy(nav)
        # etiqueta de página: ESTAS EN: <PAGINA> con la barra de su color; tocarla = volver al MENU
        a = goto('back')
        _por_numero(a, page_no['MENU'])
        fam = name.rsplit(' ', 1)[0] if name[-1].isdigit() else name          # 'MULTIVIEW 2' -> MULTIVIEW
        controls['1']['0'] = button('ESTAS EN', (0x000000, 0x000000), [a], value=name.replace(' ', '\n'),
                                    bar=PAGE_BAR.get(fam, GRIS[1]))
        if NAV_SIN_MIX:
            # flechas que recorren solo las paginas de contenido (MENU y MIX no estan en el ciclo)
            menu = [n for n, _b in PAGES if n not in ('MIX', 'MENU', 'ENSAYO')]
            k = menu.index(name)
            for r, paso in (('0', -1), ('2', 1)):
                a = goto('back')
                _por_numero(a, page_no[menu[(k + paso) % len(menu)]])
                # fila 1: flecha arriba (pagina anterior) · fila 3: flecha abajo (la siguiente)
                controls[r]['0'] = button('▲' if paso < 0 else '▼', GRIS, [a])
        places = [(r, c) for r in range(3) for c in range(1, 5)]
    for (r, c), b in zip(places, buttons):
        if b is not None:
            controls[str(r)][str(c)] = b
    p = copy.deepcopy(page1)
    p['id'] = page_id[name]
    p['name'] = MIX_LABEL if name == 'MIX' else name
    p['controls'] = controls
    out_pages[str(i)] = p

cfg['pages'] = out_pages
VARS = [('escena', 'Escena activa', ''), ('visual', 'Visual activo', ''), ('fx', 'FX activo (switch23)', ''),
        ('cams', 'Camaras en multicam (lo manda TD)', '-'), ('cam', 'Camara unica (lo manda TD)', '')]
VARS += [('slot%d' % i, 'Camara del lugar %d (lo manda TD)' % i, '-') for i in range(1, 6)]
VARS += [('rotar', 'Rotar camaras ON/OFF (lo manda TD)', 'OFF'), ('rotarcada', 'Segundos por cambio (lo manda TD)', '-'),
         ('rotarmodo', 'Modo de rotacion: Por tiempo / Con el audio (lo manda TD)', '-'),
         ('rotarinfo', 'Rotacion: modo y valor (lo manda TD)', '-'),
         ('rotar_menos', 'Texto del boton - de rotacion (lo manda TD)', 'MAS LENTO'),
         ('rotar_mas', 'Texto del boton + de rotacion (lo manda TD)', 'MAS RAPIDO')]
# pagina MIX (setup_mix_feedback.py)
VARS += [('mix_foco', 'MIX: que se muestra (LAYOUT / VISUAL / FX)', '-'), ('mix_foconombre', 'MIX: nombre', '-')]
VARS += [('mix_p%dn' % i, 'MIX: nombre del parametro %d' % i, '-') for i in range(1, 6)]
VARS += [('mix_p%dv' % i, 'MIX: valor del parametro %d (%%)' % i, '') for i in range(1, 6)]
VARS += [('mix_ir', 'MIX: sube cuando cambia escena/visual/FX (Trigger -> ir a la pagina MIX)', '0'),
         ('mix_audio', 'MIX: parametro que va con el audio (1-5, 0 = apagado)', '0'),
         ('mix_audioon', 'MIX: audio ON / OFF', '-'), ('mix_audiomult', 'MIX: sensibilidad del audio', '-')]
# pagina MENU: lo activo de cada pagina (lo manda TD; vacio = nada activo ahi)
VARS += [('bs_canal', 'MENU: canal-pad del ultimo pad del Beatstep', '-')]
VARS += [('menu_mv', 'MENU: layout multiview activo', ''), ('menu_sc', 'MENU: layout single cam activo', ''),
         ('menu_vis', 'MENU: visual activo', ''), ('menu_fx', 'MENU: FX activo', '')]
VARS += [('demo', 'DEMO automatico ON/OFF (lo manda TD)', 'OFF'), ('democada', 'DEMO: segundos por escena', '-'),
         ('rec', 'Grabando ON/OFF (lo manda TD)', 'OFF'), ('recfuente', 'Que se graba (lo manda TD)', '-')]
cfg['custom_variables'] = {
    n: {'description': d, 'defaultValue': dv,
        'persistCurrentValue': not n.startswith(('cams', 'slot', 'rotar', 'mix_', 'demo', 'rec')),
        'sortOrder': k}
    for k, (n, d, dv) in enumerate(VARS)}

with gzip.open(DST, 'wb') as f:
    f.write(json.dumps(cfg, separators=(',', ':')).encode('utf-8'))

chk = json.loads(gzip.open(DST).read())
for k, p in chk['pages'].items():
    txt = [' / '.join(l['text']['value'].replace('\n', ' ') for l in b['style']['layers'] if l['type'] == 'text')
           for row in p['controls'].values() for b in row.values() if b['type'] == 'button-layered']
    print(k, p['name'], len(txt), txt)
print('ok ->', DST)
