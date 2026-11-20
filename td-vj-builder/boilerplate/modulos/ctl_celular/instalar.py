# ctl_celular — CONTROL DESDE EL CELULAR: una pagina web que sirve TD (Web Server DAT) para operar y vigilar el show
# desde el cel, en la misma red. Idempotente: reinstalar = actualizar (conserva tema de avisos y ajustes).
# Origen: Casa Bacardi x Corona Capital (2026-11-19 / 20). Ver LEEME.md.
#
# Arma /project2/show/celular:
#   web (Web Server DAT, puerto proyecto.json -> "celular" -> "puerto", default 9990; el 9980 es del MCP)
#   pagina (pagina.html de este modulo) · web_callbacks · monitor_lib (ESTADO + AVISOS ntfy) · monitor_exec
# y en /project2 la PAUSA: <lo que entra a level1> -> pausa_sw (0 en vivo · 1 congelado) -> level1, con pausa_cache.
# Todo lo que ensena sale de lo que exista en el show (si no hay piloto, slices, patron, etc., ese bloque no sale):
#   CANAL (todos o uno) + ANTERIOR / SIGUIENTE dentro de el + rejilla de sus pads para elegir uno · nombre y canal al aire
#   sliders de tamano (Logotamano / Circulotamano + base.Tamano) segun el grupo del canal (GRUPOS de ui_bancos.py)
#   MANUAL / AUTO + AJUSTES DEL PILOTO (paginas Piloto / Repertorio / Vigia, con sus secciones)   [auto_piloto]
#   PAUSA / PLAY · PATRON DE PRUEBA (show.Patronprueba) · SALIDA DESDE TD (SLICES)                  [led_slices]
#   EFECTOS Y MASCARA: que sale, mascara redonda, capa automatica y cada efecto (paginas de /project1/slices) [ledfx_*]
#   GUARDAR (el de la UI) · FUENTE DE AUDIO (show.Audiofuente / Audiodevice) · ESTADO y AVISOS (ntfy)
# En el cel: http://<ip de la lap>:<puerto> (al instalar se imprime la direccion).
import json, os, socket, secrets

S = op('/project2/show')
AQUI = project.folder + '/modulos/ctl_celular'
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())


def config():
    ruta = project.folder + '/proyecto.json'
    try:
        return json.load(open(ruta, encoding='utf-8')).get('celular', {}) if os.path.exists(ruta) else {}
    except Exception:
        return {}


PUERTO = int(config().get('puerto', 9990))

CALLBACKS = r'''# Callbacks del Web Server del celular (los escribe modulos/ctl_celular/instalar.py; no editar aqui)
import ast, json, re, time

R = op('/project2')
S = op('/project2/show')
C = me.parent()


def pil():
    o = op('/project2/show/piloto/piloto_lib')          # modulo auto_piloto (opcional)
    return o.module if o is not None else None


def log(txt):
    try:
        with open(project.folder + '/control/piloto_log.txt', 'a', encoding='utf-8') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S  ') + txt + chr(10))
    except Exception:
        pass


def _ui_bancos(nombre):
    """BANCOS / GRUPOS de builders/herramientas/ui_bancos.py (si existe)."""
    ruta = project.folder + '/builders/herramientas/ui_bancos.py'
    try:
        body = ast.parse(open(ruta, encoding='utf-8').read()).body
        n = next(n for n in body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == nombre)
        return eval(compile(ast.Expression(n.value), 'ui_bancos', 'eval'), {'__builtins__': {}})   # admite [None] * 16
    except Exception:
        return None


def grupos():
    G = C.fetch('grupos', None, search=False)
    if G is None:
        G = _ui_bancos('GRUPOS') or {}
        C.store('grupos', G)
    return G


def lista():
    """[(canal, pad, nombre, entrada de switch2)] en orden."""
    p = pil()
    if p is not None:
        return p.bancos()
    L = C.fetch('bancos', None, search=False)
    if L is None:
        B = _ui_bancos('BANCOS')
        if B:
            L = [(canal, i + 1, x[0], x[1]) for canal, pads in sorted(B.items()) for i, x in enumerate(pads) if x]
        else:
            sw = R.op('switch2')
            L = [(0, i + 1, o.name, i) for i, o in enumerate(sw.inputs)] if sw is not None else []
        C.store('bancos', L)
    return L


def base_de(k):
    p = pil()
    if p is not None:
        return p.base_de(k)
    sw = R.op('switch2')
    o = sw.inputs[k] if sw is not None and 0 <= k < len(sw.inputs) else None
    for _ in range(4):
        if o is None:
            return None
        if o.parent() != R:
            return o.parent()
        if re.match(r'base\d+$', o.name):
            return o
        nul = next((i for i in o.inputs if i.OPType == 'nullTOP'), None) if o.OPType == 'switchTOP' else None
        o = nul if nul is not None else (o.inputs[0] if o.inputs else None)
    return None


def al_aire():
    k = int(R.op('switch2').par.index.eval())
    return next((x for x in lista() if x[3] == k), None), k


def rango(p):
    return (p.normMin, p.normMax) if p.normMax > p.normMin else (p.min, p.max)


def pars(c, k):
    """[(id, titulo, Par)] de lo que se puede ajustar en el visual al aire."""
    if c is None:
        return []
    g = grupos().get(c[0], '')
    out = []
    if 'LOGO' in g and getattr(S.par, 'Logotamano', None) is not None:
        out.append(('logo', 'TAMAÑO LOGO · TODOS', S.par.Logotamano))
    elif 'CIRCULAR' in g and getattr(S.par, 'Circulotamano', None) is not None:
        out.append(('circulo', 'TAMAÑO CÍRCULOS · TODOS', S.par.Circulotamano))
    if out:
        b = base_de(k)
        p = getattr(b.par, 'Tamano', None) if b is not None else None
        if p is not None:
            out.append(('ajuste', 'AJUSTE DE ESTE VISUAL', p))
    return out


def estado():
    c, k = al_aire()
    sl = []
    for i, t, p in pars(c, k):
        lo, hi = rango(p)
        sl.append({'id': i, 'titulo': t, 'v': round(float(p.eval()), 4), 'min': lo, 'max': hi, 'pct': True})
    p = pil()
    return {'canales': canales(), 'canal_sel': canal_sel(), 'pads': pads_canal(),
            'k': k, 'canal': ('CH%d %s · %d' % (c[0], grupos().get(c[0], ''), c[1])) if c and c[0] else '',
            'nombre': c[2] if c else 'entrada %d' % k, 'sliders': sl,
            'auto': bool(getattr(S.par, 'Pilotoauto', None) is not None and S.par.Pilotoauto.eval()),
            'hay_piloto': p is not None,
            'auto_txt': p.estado_txt() if p is not None else '',
            'color_txt': p.color_txt() if p is not None and hasattr(p, 'color_txt') else '',
            'audio': audio_info(),
            'guardar': guardar_info(),
            'patron': bool(getattr(S.par, 'Patronprueba', None) is not None and S.par.Patronprueba.eval()),
            'hay_patron': getattr(S.par, 'Patronprueba', None) is not None,
            'pausa': pausa_k() is not None,
            'hay_pausa': R.op('pausa_sw') is not None,
            'slices': slices_info(),
            'piloto': piloto_pars(),
            'efectos': efectos_pars(),
            'monitor': C.op('monitor_lib').module.estado() if C.op('monitor_lib') else None}


# ---- SALIDA DESDE TD (modulo led_slices): estado, prueba y abrir / cerrar la ventana /salida_slices
def slices_info():
    L = op('/project1/slices')
    m = L.op('slices_ventana') if L is not None else None
    if m is None:
        return None
    txt, n = m.module.estado()
    return {'txt': txt, 'n': n, 'armada': bool(L.par.Slicesarmada.eval()), 'prueba': L.par.Prueba.eval(),
            'pruebas': [[a, b] for a, b in zip(L.par.Prueba.menuNames, L.par.Prueba.menuLabels)],
            'led': bool(m.module.led_armada())}


def slices_poner(q):
    L = op('/project1/slices')
    m = L.op('slices_ventana') if L is not None else None
    if m is None:
        return
    a = q.get('accion', '')
    if a == 'abrir':
        m.module.log('ABRIR desde el celular')
        m.module.abrir()
    elif a == 'cerrar':
        m.module.log('CERRAR desde el celular')
        m.module.cerrar()
    elif a == 'prueba' and q.get('v') in L.par.Prueba.menuNames:
        L.par.Prueba = q.get('v')


# ---- ajustes del piloto: todo lo de las paginas Piloto / Repertorio / Vigia del hub, con sus secciones (Header)
PAGS_PILOTO = ('Piloto', 'Repertorio', 'Vigia')
NO_CEL = ('Pilotoauto',)            # ya esta en MANUAL / AUTO


def secciones_de(comp, paginas, no=(), c='show'):
    """[{'t': titulo, 'pars': [...]}] de las paginas dadas de comp, con sus secciones (Header)."""
    secs = []
    for pn in paginas:
        g = next((x for x in comp.customPages if x.name == pn), None)
        if g is None:
            continue
        for p in g.pars:
            if p.style == 'Header':
                secs.append({'t': p.label.strip().upper(), 'pars': []})
                continue
            if p.name in no or p.style not in ('Toggle', 'Float', 'Int', 'Menu', 'Str', 'Pulse'):
                continue
            if not secs:
                secs.append({'t': pn.upper(), 'pars': []})
            d = {'n': p.name, 'l': p.label.strip(), 's': p.style, 'c': c}
            if p.readOnly:
                d['ro'] = True
            if p.style == 'Toggle':
                d['v'] = bool(p.eval())
            elif p.style in ('Float', 'Int'):
                lo, hi = rango(p)
                d.update(v=round(float(p.eval()), 4), min=lo, max=hi)
            elif p.style == 'Menu':
                d.update(v=p.eval(), op=[[a, b] for a, b in zip(p.menuNames, p.menuLabels)])
            elif p.style == 'Str':
                d['v'] = p.eval()
            secs[-1]['pars'].append(d)
    return [x for x in secs if x['pars']]


def piloto_pars():
    return secciones_de(S, PAGS_PILOTO, NO_CEL, 'show')


# ---- EFECTOS Y MASCARA (led_slices + ledfx_* + auto_capa): una sub-pagina por pagina de /project1/slices
EFECTOS_PAGS = (('Efectos', 'QUE SALE Y MASCARA'), ('Capa', 'CAPA AUTOMATICA'), ('Chaser', 'CHASER'),
                ('Barrido', 'BARRIDO'), ('EQ', 'EQ DE BOCINAS'), ('Onda', 'ONDA DE KICK'), ('Cascada', 'CASCADA'),
                ('Giro', 'GIRO'), ('Respira', 'RESPIRACION'))


def efectos_pars():
    L = op('/project1/slices')
    if L is None:
        return []
    out = []
    for pn, titulo in EFECTOS_PAGS:
        g = next((x for x in L.customPages if x.name == pn), None)
        if g is None:
            continue
        on = next((p for p in g.pars if p.style == 'Toggle' and (p.name.endswith('on') or p.name == 'Capaauto')), None)
        out.append({'pg': pn, 't': titulo, 'on': bool(on.eval()) if on is not None else None,
                    'on_n': on.name if on is not None else None,
                    'secs': secciones_de(L, [pn], (), 'slices')})
    return out


def par_poner(n, v, c='show'):
    if c == 'slices':
        comp, pags, no = op('/project1/slices'), [x[0] for x in EFECTOS_PAGS], ()
    else:
        comp, pags, no = S, PAGS_PILOTO, NO_CEL
    p = getattr(comp.par, n, None) if comp is not None else None
    if p is None or n in no or p.page.name not in pags or p.readOnly:
        return
    if p.style == 'Pulse':
        p.pulse()
    elif p.style == 'Toggle':
        p.val = str(v) in ('1', 'true', 'True')
    elif p.style in ('Float', 'Int'):
        lo, hi = rango(p)
        x = min(max(float(v), lo), hi)
        p.val = int(round(x)) if p.style == 'Int' else x
    elif p.style == 'Menu':
        if v in p.menuNames:
            p.val = v
    elif p.style == 'Str':
        p.val = str(v)


# ---- PAUSA / PLAY: congela la IMAGEN antes de level1 (pausa_cache guarda el ultimo cuadro, pausa_sw lo manda).
# La base sigue corriendo detras (apagarle el cook la manda a NEGRO); Master / BLACKOUT siguen funcionando.
# Mientras: el piloto no cambia (Pilotoquedarse) y el vigia se apaga (leia la imagen quieta como falla y saltaba el
# visual); al dar PLAY ambos regresan como estaban. PLAY solo si cambia el visual al aire o TD arranca.
def cadena_pausa():
    """<lo que entra a level1> -> pausa_sw -> level1. Se rehace sola si otro script reconecto level1."""
    lv, sw, ca = R.op('level1'), R.op('pausa_sw'), R.op('pausa_cache')
    if lv is None or sw is None or ca is None or not lv.inputs:
        return False
    src = lv.inputs[0]
    if src == sw:
        return True
    sw.inputConnectors[0].connect(src)
    sw.inputConnectors[1].connect(ca)
    ca.inputConnectors[0].connect(src)
    lv.inputConnectors[0].connect(sw)
    log('PAUSA: cadena rehecha (%s -> pausa_sw -> level1)' % src.name)
    return True


def pausa_k():
    return C.fetch('pausa', None, search=False)     # entrada de switch2 congelada, o None


def pausa_base():          # compatibilidad: piloto_lib / pruebas preguntan si hay pausa
    return R.op('pausa_cache') if pausa_k() is not None else None


def _congelar():
    ca = R.op('pausa_cache')
    if ca is not None:
        ca.par.active = False                       # deja de grabar: se queda el ultimo cuadro


def pausar(on):
    ca, sw = R.op('pausa_cache'), R.op('pausa_sw')
    if ca is None or sw is None:
        return
    if on:
        if pausa_k() is not None or not cadena_pausa():
            return
        c, k = al_aire()
        guardado = {}
        for n, v in (('Pilotoquedarse', True), ('Vigia', False)):
            p = getattr(S.par, n, None)
            if p is not None:
                guardado[n] = bool(p.eval())
                p.val = v
        C.store('pausa_guardado', guardado)
        ca.par.active = True
        sw.par.index = 1
        run("op('%s').module._congelar()" % me.path, delayFrames=3)     # graba unos cuadros y congela
        C.store('pausa', k)
        log('PAUSA (cel) -> %s' % (c[2] if c else 'entrada %d' % k))
    else:
        sw.par.index = 0
        ca.par.active = False
        if pausa_k() is not None:
            log('PLAY (cel)')
            for n, v in C.fetch('pausa_guardado', {}, search=False).items():
                p = getattr(S.par, n, None)
                if p is not None:
                    p.val = v
        C.unstore('pausa')
        C.unstore('pausa_guardado')


def pausa_vigilar(arranque=False):
    """monitor_exec lo llama: si cambio el visual al aire (o TD arranco), PLAY solo; y cuida la cadena."""
    cadena_pausa()
    k = pausa_k()
    if arranque or (k is not None and al_aire()[1] != k):
        pausar(False)


def audio_info():
    p = getattr(S.par, 'Audiofuente', None)
    d = getattr(S.par, 'Audiodevice', None)
    if p is None:
        return None
    lab = lambda n: (n.split('||')[1] if '||' in n else n).replace('_', ' ')
    return {'fuente': p.eval(), 'dev': d.eval() if d is not None else '',
            'devs': [[n, lab(n)] for n in (d.menuNames if d is not None else [])]}


def audio_poner(q):
    if 'fuente' in q and getattr(S.par, 'Audiofuente', None) is not None and q['fuente'] in S.par.Audiofuente.menuNames:
        S.par.Audiofuente = q['fuente']
    if 'dev' in q and getattr(S.par, 'Audiodevice', None) is not None and q['dev'] in S.par.Audiodevice.menuNames:
        S.par.Audiodevice = q['dev']


def guardar_info():
    g = op('/project2/ui_perform/uimod_guardar')
    if g is None:
        return {'txt': 'GUARDAR', 'reciente': False}
    return {'txt': g.module.texto(), 'reciente': bool(g.module.reciente())}


def guardar():
    g = op('/project2/ui_perform/uimod_guardar')
    if g is not None:
        g.module.guardar()          # el mismo GUARDAR de la UI (siguiente version)
    else:
        project.save()


# ---- CANAL elegido en el cel: ANTERIOR / SIGUIENTE recorre solo ese canal y la rejilla ensena sus pads
def canal_sel():
    return int(C.fetch('canal_sel', 0, search=False) or 0)       # 0 = todos


def canales():
    G = grupos()
    return [[c, G.get(c, '')] for c in sorted({x[0] for x in lista() if x[0]})]


def pads_canal():
    c = canal_sel()
    return [{'n': x[2], 'k': x[3], 'pad': x[1]} for x in lista() if c and x[0] == c]


def pad(k):
    k = int(k)
    if any(x[3] == k for x in lista()):                         # solo pads de BANCOS
        R.op('switch2').par.index = k


def ir(d):
    c = canal_sel()
    L = [x for x in lista() if not c or x[0] == c]
    if not L:
        return
    _, k = al_aire()
    pos = next((i for i, x in enumerate(L) if x[3] == k), None)
    nuevo = L[0] if pos is None else L[(pos + d) % len(L)]
    R.op('switch2').par.index = nuevo[3]


def poner(i, v, k=None):
    # k = entrada del visual que mostraba la pagina al mover el slider: si el piloto cambio de visual a medio
    # arrastre, el valor va a ESE visual y no al nuevo
    c, kk = al_aire()
    if k not in (None, ''):
        k = int(k)
        c = next((x for x in lista() if x[3] == k), None)
    else:
        k = kk
    for pid, t, p in pars(c, k):
        if pid == i:
            lo, hi = rango(p)
            p.val = min(max(float(v), lo), hi)


def onHTTPRequest(webServerDAT, request, response):
    uri = request.get('uri', '/').split('?')[0]
    q = request.get('pars', {}) or {}
    response['statusCode'] = 200
    response['statusReason'] = 'OK'
    try:
        if uri == '/':
            response['content-type'] = 'text/html; charset=utf-8'
            response['data'] = C.op('pagina').text
            return response
        if uri == '/ir':
            pausar(False)
            ir(1 if int(q.get('dir', 1)) > 0 else -1)
        elif uri == '/canal':
            C.store('canal_sel', int(q.get('c', 0) or 0))
        elif uri == '/pad':
            pausar(False)
            pad(q.get('k', -1))
        elif uri == '/slices':
            slices_poner(q)
        elif uri == '/pausa':
            pausar(str(q.get('on', '0')) == '1')
        elif uri == '/par':
            par_poner(q.get('n', ''), q.get('v', ''), q.get('c', 'show'))
        elif uri == '/patron':
            if getattr(S.par, 'Patronprueba', None) is not None:
                S.par.Patronprueba = str(q.get('on', '0')) == '1'
        elif uri == '/guardar':
            guardar()
        elif uri == '/audio':
            audio_poner(q)
        elif uri == '/prueba':
            C.op('monitor_lib').module.prueba()
        elif uri == '/auto':
            if getattr(S.par, 'Pilotoauto', None) is not None:
                S.par.Pilotoauto = str(q.get('on', '0')) == '1'
        elif uri == '/set':
            poner(q.get('id', ''), q.get('v', 0), q.get('k'))
        elif uri != '/estado':
            response['statusCode'] = 404
            response['statusReason'] = 'Not Found'
            response['data'] = 'no'
            return response
        response['content-type'] = 'application/json'
        response['Cache-Control'] = 'no-store'
        response['data'] = json.dumps(estado())
    except Exception as e:
        response['statusCode'] = 500
        response['statusReason'] = 'Error'
        response['content-type'] = 'application/json'
        response['data'] = json.dumps({'error': str(e)})
        debug('celular: ' + str(e))
    return response


def onWebSocketOpen(webServerDAT, client, uri):
    return
def onWebSocketClose(webServerDAT, client):
    return
def onWebSocketReceiveText(webServerDAT, client, data):
    return
def onWebSocketReceiveBinary(webServerDAT, client, data):
    return
def onWebSocketReceivePing(webServerDAT, client, data):
    webServerDAT.webSocketSendPong(client, data=data)
    return
def onWebSocketReceivePong(webServerDAT, client, data):
    return
def onServerStart(webServerDAT):
    return
def onServerStop(webServerDAT):
    return
'''


def ips():
    out = set()
    try:
        for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            out.add(i[4][0])
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))       # no manda nada: solo elige la interfaz de salida
        out.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    return sorted(x for x in out if not x.startswith('127.'))


if S is None:
    print('[fallo] ctl_celular: falta /project2/show (el hub del rig)')
else:
    C = S.op('celular') or S.create(baseCOMP, 'celular')
    P = S.op('piloto')
    C.nodeX, C.nodeY = (P.nodeX + 200, P.nodeY) if P is not None else (C.nodeX, C.nodeY)
    C.comment = 'Control desde el celular (modulos/ctl_celular)'
    pag = C.op('pagina') or C.create(textDAT, 'pagina')
    pag.text = open(AQUI + '/pagina.html', encoding='utf-8').read().lstrip('﻿')
    pag.nodeX, pag.nodeY = 0, 0
    cb = C.op('web_callbacks') or C.create(textDAT, 'web_callbacks')
    cb.text = CALLBACKS
    cb.nodeX, cb.nodeY = 0, -150
    ws = C.op('web') or C.create(webserverDAT, 'web')
    ws.par.port = PUERTO
    ws.par.callbacks = cb
    ws.par.active = True
    ws.nodeX, ws.nodeY = 200, -150
    C.unstore('grupos')
    C.unstore('bancos')

    # ---- monitor + avisos (monitor_lib.py) · pagina Avisos del hub
    pg = next((g for g in S.customPages if g.name == 'Avisos'), None) or S.appendCustomPage('Avisos')

    def _tog(n, label, v):
        if not hasattr(S.par, n):
            p = pg.appendToggle(n, label=label)[0]
            p.default = v
            p.val = v
    if not hasattr(S.par, 'Avisostema'):
        pg.appendStr('Avisostema', label='Tema de ntfy (suscribirse en el cel)')
        S.par.Avisostema = 'td-show-' + secrets.token_hex(5)       # nombre dificil de adivinar; nada del proyecto
    _tog('Avisos', 'Mandar avisos al celular', True)
    if not hasattr(S.par, 'Avisoprueba'):
        pg.appendPulse('Avisoprueba', label='Mandar aviso de prueba')
    _tog('Avisosalida', 'Salida (Spout / NDI)', True)
    _tog('Avisovigia', 'Vigia (reinicia / salta un visual)', True)
    _tog('Avisofps', 'FPS bajos (menos del 60 %)', True)
    _tog('Avisoaudio', 'Sin audio', True)
    if not hasattr(S.par, 'Avisoaudioseg'):
        p = pg.appendFloat('Avisoaudioseg', label='Sin audio: avisar despues de (s)')[0]
        p.normMin, p.normMax, p.default, p.val = 5, 300, 30, 30
    if not hasattr(S.par, 'Avisoresumen'):
        p = pg.appendInt('Avisoresumen', label='Resumen "todo bien" cada (min, 0 = no)')[0]
        p.normMin, p.normMax, p.default, p.val = 0, 120, 0, 0
    secciones(S, 'Avisos', [
        ('Havisos', 'AVISOS AL CELULAR (NTFY)', ['Avisos', 'Avisoprueba', 'Avisostema']),
        ('Havisosque', 'QUE AVISA', ['Avisosalida', 'Avisovigia', 'Avisofps', 'Avisoaudio']),
        ('Havisosaj', 'AJUSTES', ['Avisoaudioseg', 'Avisoresumen']),
    ])
    ml = C.op('monitor_lib') or C.create(textDAT, 'monitor_lib')
    ml.text = open(AQUI + '/monitor_lib.py', encoding='utf-8').read().lstrip('﻿')
    ml.nodeX, ml.nodeY = 0, -300
    mx = C.op('monitor_exec') or C.create(executeDAT, 'monitor_exec')
    mx.text = '\n'.join(['# monitor del show: estado + avisos (monitor_lib) · PAUSA: PLAY solo y cadena (web_callbacks)',
                         'def onStart():',
                         "    op('web_callbacks').module.pausa_vigilar(arranque=True)",
                         "    op('monitor_lib').module.arranque()", '    return', '',
                         'def onFrameEnd(frame):', '    if frame % 15 == 0:',
                         "        op('monitor_lib').module.tick()",
                         "        op('web_callbacks').module.pausa_vigilar()", '    return', ''])
    mx.par.start = True
    mx.par.frameend = True
    mx.par.active = True
    mx.nodeX, mx.nodeY = 200, -300
    pe = C.op('avisos_pulso') or C.create(parameterexecuteDAT, 'avisos_pulso')
    pe.par.op = S.path
    pe.par.pars = 'Avisoprueba'
    pe.par.onpulse = True
    pe.text = '\n'.join(['def onPulse(par):', "    op('monitor_lib').module.prueba()", '    return', ''])
    pe.nodeX, pe.nodeY = 400, -300
    C.unstore('mon')

    # ---- PAUSA: <lo que entra a level1> -> pausa_sw (0 en vivo, 1 = pausa_cache congelado) -> level1
    R = op('/project2')
    lv = R.op('level1')
    if lv is not None and lv.inputs:
        ca = R.op('pausa_cache') or R.create(cacheTOP, 'pausa_cache')
        psw = R.op('pausa_sw') or R.create(switchTOP, 'pausa_sw')
        ca.par.cachesize = 1
        ca.par.active = False
        psw.par.index = 0
        ca.comment = 'PAUSA del cel: guarda el ultimo cuadro (modulos/ctl_celular)'
        psw.comment = 'PAUSA del cel: 0 en vivo · 1 congelado'
        cb.module.cadena_pausa()
        src = psw.inputs[0] if psw.inputs else None
        if src is not None:
            ca.nodeX, ca.nodeY = src.nodeX + 150, src.nodeY - 120
            psw.nodeX, psw.nodeY = src.nodeX + 300, src.nodeY
        print('[ok] pausa:', src.name if src else '?', '-> pausa_sw -> level1')
    else:
        print('[--] sin level1 en /project2: la PAUSA no se instalo')
    cb.module.pausar(False)               # reinstalar en pausa: PLAY y regresa piloto / vigia como estaban
    ws.par.active = False                # reinicia el servidor para que tome los callbacks nuevos
    ws.par.active = True

    print('[ok] ctl_celular en', C.path, '· puerto', PUERTO)
    print('[ok] avisos ntfy: tema', S.par.Avisostema.eval(), '· en el cel: app ntfy -> suscribirse a ese tema')
    for ip in ips():
        print('     en el celular (misma red):  http://%s:%d' % (ip, PUERTO))
