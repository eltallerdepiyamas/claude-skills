# =============================================================
# td_mcp_callbacks.py — callbacks del Web Server DAT de /project2/td_mcp
# Lo copia setup_td_mcp.py al Text DAT 'callbacks'. Editar aqui y volver a correr el setup.
# Protocolo: POST /api  {"cmd": "...", "args": {...}}  header X-TD-MCP-Token
# Solo acepta 127.0.0.1 / ::1. Sin eval: solo correr_script (dentro de project.folder).
# =============================================================
import json, os, io, sys, traceback, contextlib, tempfile, time

MAX_ITEMS = 400


def _token():
    return parent().fetch('td_mcp_token', '')


def _readonly():
    try:
        return bool(parent().par.Readonly.eval())
    except Exception:
        return False


def _jsonable(v):
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    try:
        return v.path  # OPs
    except Exception:
        return str(v)


def _op(ruta):
    o = op(ruta) if ruta else None
    if o is None:
        raise ValueError('No existe el operador: %s' % ruta)
    return o


# ---------------- comandos ----------------

def cmd_estado(a):
    return {'proyecto': project.name, 'carpeta': project.folder, 'readonly': _readonly(),
            'td': app.version + '.' + str(app.build), 'fps': round(project.cookRate, 2),
            'frame': absTime.frame}


def cmd_correr_script(a):
    if _readonly():
        raise PermissionError('Modo solo-lectura activo (td_mcp Readonly).')
    raiz = os.path.realpath(project.folder)
    ruta = a.get('ruta', '')
    full = os.path.realpath(ruta if os.path.isabs(ruta) else os.path.join(raiz, ruta))
    if os.path.commonpath([raiz, full]) != raiz:
        raise PermissionError('Solo se corren scripts dentro de project.folder (%s)' % raiz)
    if not full.lower().endswith('.py') or not os.path.isfile(full):
        raise ValueError('No es un .py existente: %s' % full)
    code = open(full, encoding='utf-8').read()
    import td
    g = {k: getattr(td, k) for k in dir(td) if not k.startswith('_')}
    g.update({'__name__': '__main__', '__file__': full, 'me': me})
    buf = io.StringIO()
    ok, err = True, ''
    t0 = time.time()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            exec(compile(code, full, 'exec'), g)
        except SystemExit:
            pass
        except Exception:
            ok, err = False, traceback.format_exc()
    return {'ok': ok, 'salida': buf.getvalue(), 'error': err,
            'segundos': round(time.time() - t0, 3), 'ruta': full}


def cmd_errores(a):
    raiz = _op(a.get('ruta_op') or '/project2')
    ops = [raiz] + (raiz.findChildren() if raiz.isCOMP else [])
    res, total = [], 0
    for o in ops:
        try:
            e, w = o.errors(), o.warnings()
            s = o.scriptErrors() if hasattr(o, 'scriptErrors') else ''
        except Exception:
            continue
        if e or w or s:
            total += 1
            if len(res) < MAX_ITEMS:
                d = {'op': o.path, 'tipo': o.OPType}
                if e: d['errores'] = e
                if w: d['warnings'] = w
                if s: d['script'] = s
                res.append(d)
    return {'revisados': len(ops), 'con_problemas': total, 'items': res,
            'recortado': total > len(res)}


def cmd_ver_salida(a):
    t = _op(a.get('ruta_top'))
    if t.isCOMP:
        # COMP con salida TOP (ej. blend_switch): usar su primer Out TOP
        outs = [o for o in t.findChildren(type=outTOP, depth=1)]
        outs.sort(key=lambda o: (o.par.index.eval() if hasattr(o.par, 'index') else 0, o.name))
        if not outs:
            raise ValueError('%s es un COMP sin Out TOP' % t.path)
        t = outs[0]
    if not t.isTOP:
        raise ValueError('%s no es un TOP (ni COMP con Out TOP)' % t.path)
    fmt = (a.get('formato') or 'png').lower().strip('.')
    if fmt not in ('png', 'jpg'):
        fmt = 'png'
    carpeta = os.path.join(tempfile.gettempdir(), 'td_mcp')
    os.makedirs(carpeta, exist_ok=True)
    nombre = t.path.strip('/').replace('/', '__') + '_' + str(int(time.time())) + '.' + fmt
    ruta = os.path.join(carpeta, nombre)
    t.cook(force=True)
    t.save(ruta)
    res = {'ruta': ruta, 'ancho': t.width, 'alto': t.height}
    # preview JPG (un PNG 1080p pesa ~4-5 MB y no cabe en la respuesta del MCP)
    if fmt == 'png':
        prev = ruta[:-4] + '_preview.jpg'
        try:
            t.save(prev)
            res['preview'] = prev
        except Exception:
            pass
    return res


def cmd_leer_parametros(a):
    o = _op(a.get('ruta'))
    solo_custom = bool(a.get('solo_custom', False))
    filtro = (a.get('filtro') or '').lower()
    pars = o.customPars if solo_custom else o.pars()
    res = []
    for p in pars:
        if filtro and filtro not in p.name.lower() and filtro not in p.label.lower():
            continue
        d = {'name': p.name, 'label': p.label, 'page': p.page.name if p.page else '',
             'val': _jsonable(p.eval()), 'mode': str(p.mode).split('.')[-1], 'style': p.style}
        if p.mode == ParMode.EXPRESSION: d['expr'] = p.expr
        if p.mode == ParMode.BIND: d['bind'] = p.bindExpr
        if p.isMenu: d['menu'] = list(p.menuNames or [])
        res.append(d)
        if len(res) >= MAX_ITEMS:
            break
    return {'op': o.path, 'tipo': o.OPType, 'pars': res}


def cmd_cambiar_parametro(a):
    if _readonly():
        raise PermissionError('Modo solo-lectura activo (td_mcp Readonly).')
    o = _op(a.get('ruta'))
    nombre = a.get('par')
    p = getattr(o.par, nombre, None)
    if p is None:
        raise ValueError('%s no tiene el parametro %s' % (o.path, nombre))
    if p.mode == ParMode.EXPRESSION and not a.get('forzar'):
        raise ValueError('%s.%s tiene expresion (%s). Usa forzar=true para pisarla.' % (o.path, nombre, p.expr))
    v = a.get('valor')
    antes = _jsonable(p.eval())
    if p.isMenu and isinstance(v, str) and v not in p.menuNames and v in p.menuLabels:
        v = p.menuNames[list(p.menuLabels).index(v)]
    elif p.isToggle and isinstance(v, str):
        v = v.lower() in ('1', 'true', 'on', 'si', 'sí')
    elif (p.isFloat or p.isNumber) and isinstance(v, str):
        v = float(v)
    if p.isNumber and not p.isFloat and isinstance(v, float):
        v = int(round(v))
    if p.mode == ParMode.EXPRESSION:
        p.mode = ParMode.CONSTANT
    p.val = v
    return {'op': o.path, 'par': nombre, 'antes': antes, 'ahora': _jsonable(p.eval())}


def cmd_listar_nodos(a):
    o = _op(a.get('ruta') or '/project2')
    prof = max(1, int(a.get('profundidad') or 1))
    hijos = o.findChildren(maxDepth=prof) if o.isCOMP else []
    res = []
    for c in hijos[:MAX_ITEMS]:
        d = {'path': c.path, 'tipo': c.OPType}
        try:
            if c.isTOP or c.isCHOP or c.isSOP or c.isDAT:
                if c.inputs: d['in'] = [i.path for i in c.inputs if i]
        except Exception:
            pass
        res.append(d)
    return {'op': o.path, 'total': len(hijos), 'nodos': res, 'recortado': len(hijos) > MAX_ITEMS}


CMDS = {k[4:]: v for k, v in globals().items() if k.startswith('cmd_')}


# ---------------- Web Server DAT ----------------

def _reply(response, code, obj):
    response['statusCode'] = code
    response['statusReason'] = 'OK' if code == 200 else 'Error'
    response['Content-Type'] = 'application/json; charset=utf-8'
    response['data'] = json.dumps(obj, ensure_ascii=False)
    return response


def onHTTPRequest(webServerDAT, request, response):
    cliente = str(request.get('clientAddress', ''))
    if not (cliente.startswith('127.0.0.1') or cliente.startswith('::1') or cliente.startswith('[::1]') or cliente.startswith('localhost')):
        return _reply(response, 403, {'ok': False, 'error': 'solo localhost'})
    if request.get('Origin') or request.get('origin'):
        return _reply(response, 403, {'ok': False, 'error': 'no se aceptan navegadores'})
    tok = ''
    for k, v in request.items():
        if str(k).lower().replace('_', '-') == 'x-td-mcp-token':
            tok = str(v).strip()
    if not _token() or tok != _token():
        return _reply(response, 401, {'ok': False, 'error': 'token invalido (llego=%s, guardado=%s, claves=%s)' % (
            bool(tok), bool(_token()), sorted(str(k) for k in request.keys()))})
    if request.get('method') != 'POST':
        return _reply(response, 405, {'ok': False, 'error': 'usa POST'})
    try:
        data = request.get('data') or b'{}'
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')
        body = json.loads(data)
        fn = CMDS.get(body.get('cmd'))
        if fn is None:
            return _reply(response, 400, {'ok': False, 'error': 'comando desconocido: %s' % body.get('cmd')})
        return _reply(response, 200, {'ok': True, 'resultado': fn(body.get('args') or {})})
    except Exception as e:
        return _reply(response, 200, {'ok': False, 'error': '%s: %s' % (type(e).__name__, e),
                                      'traceback': traceback.format_exc()})


def onWebSocketOpen(webServerDAT, client, uri):
    return

def onWebSocketClose(webServerDAT, client):
    return

def onWebSocketReceiveText(webServerDAT, client, data):
    return

def onWebSocketReceiveBinary(webServerDAT, client, data):
    return

def onWebSocketReceivePing(webServerDAT, client, data):
    return

def onWebSocketReceivePong(webServerDAT, client, data):
    return

def onServerStart(webServerDAT):
    return

def onServerStop(webServerDAT):
    return
