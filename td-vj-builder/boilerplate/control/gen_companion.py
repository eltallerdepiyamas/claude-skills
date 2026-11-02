import gzip, json, copy, os, random, string

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'companion_base_export.companionconfig')
DST = os.path.join(HERE, 'streamdeck.companionconfig')

cfg = json.loads(gzip.open(SRC).read().decode('utf-8'))
page1 = cfg['pages']['1']
template = page1['controls']['0']['1']
OSC = template['steps']['0']['action_sets']['down'][0]['connectionId']

# puerto del OSC In de TD; 7000 lo ocupa Resolume Arena
TD_PORT = 7010
cfg['instances'][OSC]['config']['targetPort'] = TD_PORT
nav = {'0': {'0': {'type': 'pageup'}}, '1': {'0': {'type': 'pagenum'}}, '2': {'0': {'type': 'pagedown'}}}

FONT_SIZE = 18   # % de la altura del botón; igual en todos

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

def osc(path, kind, value):
    if kind == 's':
        return {'id': nid(), 'definitionId': 'send_string', 'connectionId': OSC,
                'options': {'path': V(path), 'string': V(value)}, 'upgradeIndex': 3, 'type': 'action'}
    return {'id': nid(), 'definitionId': 'send_int', 'connectionId': OSC,
            'options': {'path': V(path), 'int': V(value)}, 'upgradeIndex': 3, 'type': 'action'}

def setvar(name, value):
    return {'id': nid(), 'definitionId': 'custom_variable_set_value', 'connectionId': 'internal',
            'options': {'name': V(name), 'create': V(False), 'value': V(str(value))}, 'type': 'action'}

def lit(var, value, color):
    return {'id': nid(), 'type': 'feedback', 'definitionId': 'variable_value', 'connectionId': 'internal',
            'options': {'variable': V('custom:' + var), 'op': V('eq'), 'value': V(str(value))},
            'isInverted': V(False),
            'styleOverrides': [{'overrideId': nid(), 'elementId': 'box0', 'elementProperty': 'color',
                                'override': V(color)}]}

def button(text, colors, actions, latch=None):
    b = copy.deepcopy(template)
    layers = b['style']['layers']
    layers[0]['decoration'] = V('none')
    for l in layers:
        if l['type'] == 'box':
            l['color'] = V(colors[0])
        if l['type'] == 'text':
            l['text'] = V(text)
            l['fontsize'] = V(FONT_SIZE)
            l['fontsizeAllowShrink'] = V(True)
    b['steps']['0']['action_sets']['down'] = actions
    b['feedbacks'] = [lit(latch[0], latch[1], colors[1])] if latch else []
    return b

def escena(label, colors):
    return button(label.upper().replace(' ', '\n'), colors,
                  [osc('/td/Modoescena', 's', label), setvar('escena', label)],
                  latch=('escena', label))

N_CAMS = 3

def hero(i):
    # pone la cámara i al centro y pasa a Hero
    return button(f'HERO\n{i + 1}', VERDE,
                  [osc('/td/Index', 'i', i), osc('/td/Modoescena', 's', 'Hero'),
                   setvar('hero', i), setvar('escena', 'Hero')],
                  latch=('hero', i))

def cam(i):
    # selecciona la cámara (por índice del menú) y pasa a Fullscreen
    return button(f'CAM\n{i + 1}', VERDE,
                  [osc('/td/Menu2', 'i', i), osc('/td/Modoescena', 's', 'Fullscreen'),
                   setvar('cam', i), setvar('escena', 'Fullscreen')],
                  latch=('cam', i))

def step(text, par, delta):
    return button(text, GRIS, [osc('/td/inc/' + par, 'i', delta)])

def display(text):
    # solo muestra; TD actualiza la variable (setup_companion_feedback.py)
    return button(text, (0x000000, 0x000000), [])

# switch de FX de /project2 (en Little Jesus: switch23): entrada i -> base. base17 = limpio (sin FX)
FX_BASES = [17, 18, 19, 20, 21, 22, 23, 24, 38, 39, 40, 41, 42, 43, 44, 45]

# nombre de cada FX en el Stream Deck; las bases sin nombre salen como "BASE N"
FX_NAMES = {
    17: 'Sin FX',
    18: 'Time Machine 4 Glitch',
    19: 'Slitscan',
    20: 'Feedback RGB Delay',
    21: 'Optical Flow',
    22: 'Liquid Feedback',
    23: 'Pixel Sort',
    24: 'ASCII',
}

def fx(i, base):
    text = FX_NAMES.get(base, f'Base {base}').upper().replace(' ', '\n')
    return button(text, NARANJA, [osc('/td/fx', 'i', i), setvar('fx', i)], latch=('fx', i))

PAGES = [
    ('ESCENAS', [escena(l, AZUL) for l in
                 ['Gridwall', 'Pip', 'Breathing Grid', 'Float Chaos', 'Floating Pieces', 'Gridwall Drift',
                  'Magnetic Pull', 'Orbit Dance', 'Pendulum', 'Ripple Grid', 'Swarm', 'Wave Scroll']]),
    ('RAND 1', [escena(l, MORADO) for l in
                ['Rand Bend', 'Rand Collage', 'Rand Drift', 'Rand Flow', 'Rand H', 'Rand Morph',
                 'Rand Offset', 'Rand Orbit', 'Rand Pulse', 'Rand Split', 'Rand Stair', 'Rand Swing']]),
    ('RAND 2', [escena(l, MORADO) for l in ['Rand V', 'Rand Wave', 'Split Asimetrico']]),
    # cada fila = un modo de cámaras + sus opciones
    ('CAMARAS', [escena('Fullscreen', VERDE)] + [cam(i) for i in range(N_CAMS)]
                + [escena('Hero', VERDE)] + [hero(i) for i in range(N_CAMS)]
                + [escena('Grid Dinamico', VERDE), step('CAMS\n-', 'Int', -1), step('CAMS\n+', 'Int', 1),
                   display('$(custom:cams)\nCAMS')]),
]

# páginas de FX (switch4); apagadas hasta ponerles nombre a los efectos
INCLUDE_FX = True
if INCLUDE_FX:
    PAGES += [
        ('FX 1', [fx(i, b) for i, b in enumerate(FX_BASES)][:12]),
        ('FX 2', [fx(i, b) for i, b in enumerate(FX_BASES)][12:]),
    ]

out_pages = {}
for i, (name, buttons) in enumerate(PAGES, start=1):
    controls = copy.deepcopy(nav)
    # etiqueta de página con el mismo tamaño de texto que los demás botones
    controls['1']['0'] = button(name.replace(' ', '\n'),(0x000000, 0x000000), [])
    slots = [(r, c) for r in range(3) for c in range(1, 5)]
    for (r, c), b in zip(slots, buttons):
        if b is not None:
            controls[str(r)][str(c)] = b
    p = copy.deepcopy(page1)
    p['id'] = page1['id'] if i == 1 else nid()
    p['name'] = name
    p['controls'] = controls
    out_pages[str(i)] = p

cfg['pages'] = out_pages
cfg['custom_variables'] = {
    'escena': {'description': 'Escena activa', 'defaultValue': '', 'persistCurrentValue': True, 'sortOrder': 0},
    'cam': {'description': 'Camara fullscreen', 'defaultValue': '', 'persistCurrentValue': True, 'sortOrder': 1},
    'hero': {'description': 'Camara hero', 'defaultValue': '', 'persistCurrentValue': True, 'sortOrder': 2},
    'fx': {'description': 'FX activo (switch4)', 'defaultValue': '', 'persistCurrentValue': True, 'sortOrder': 3},
    'cams': {'description': 'Camaras en multicam (lo manda TD)', 'defaultValue': '-', 'persistCurrentValue': False, 'sortOrder': 4},
}

with gzip.open(DST, 'wb') as f:
    f.write(json.dumps(cfg, separators=(',', ':')).encode('utf-8'))

chk = json.loads(gzip.open(DST).read())
for k, p in chk['pages'].items():
    txt = [b['style']['layers'][2]['text']['value'].replace('\n', ' ')
           for row in p['controls'].values() for b in row.values() if b['type'] == 'button-layered']
    print(k, p['name'], len(txt), txt)
print('ok ->', DST)
