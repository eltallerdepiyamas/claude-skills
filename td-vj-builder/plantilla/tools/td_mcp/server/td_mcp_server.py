#!/usr/bin/env python3
# =============================================================
# td_mcp_server.py — servidor MCP (stdio) para controlar TouchDesigner.
# Sin dependencias: habla JSON-RPC/MCP a mano y reenvia por HTTP a
# /project2/td_mcp (Web Server DAT en 127.0.0.1). Ver ../README.md
# =============================================================
import base64, json, os, sys, urllib.request, urllib.error

AQUI = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(AQUI, '..', '.token')
HOST = os.environ.get('TD_MCP_HOST', '127.0.0.1')
MAX_IMG = 4 * 1024 * 1024
PROTO = '2025-06-18'


def _cfg():
    try:
        lineas = open(TOKEN_FILE, encoding='utf-8').read().split()
        return lineas[0], int(os.environ.get('TD_MCP_PORT') or lineas[1])
    except Exception:
        raise RuntimeError('No encuentro tools/td_mcp/.token: corre setup_td_mcp.py en el Textport de TD.')


def td(cmd, args=None, timeout=120):
    token, port = _cfg()
    req = urllib.request.Request('http://%s:%d/api' % (HOST, port),
                                 data=json.dumps({'cmd': cmd, 'args': args or {}}).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'X-TD-MCP-Token': token},
                                 method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
    except urllib.error.URLError as e:
        raise RuntimeError('TouchDesigner no responde en %s:%d (%s). ¿Esta abierto el .toe y td_mcp Activo?' % (HOST, port, e.reason))
    d = json.loads(body)
    if not d.get('ok'):
        raise RuntimeError(d.get('error', 'error') + ('\n' + d['traceback'] if d.get('traceback') else ''))
    return d['resultado']


def S(props, req=()):
    return {'type': 'object', 'properties': props, 'required': list(req)}


TOOLS = [
    ('estado', 'Ping a TouchDesigner: proyecto, carpeta, version, fps, modo solo-lectura.', S({})),
    ('correr_script', 'Ejecuta un .py que este dentro de project.folder (ruta relativa a esa carpeta, ej. control/diag_todo.py) y devuelve lo que imprime.',
     S({'ruta': {'type': 'string'}}, ['ruta'])),
    ('errores', 'Errores, warnings y script errors recursivos (incluye GLSL TOPs) bajo ruta_op (default /project2).',
     S({'ruta_op': {'type': 'string'}})),
    ('ver_salida', 'Guarda un TOP como imagen en %TEMP%/td_mcp, devuelve la ruta y la imagen.',
     S({'ruta_top': {'type': 'string'}, 'formato': {'type': 'string', 'enum': ['png', 'jpg']}}, ['ruta_top'])),
    ('leer_parametros', 'Parametros de un operador (valor, modo, expresion, bind, menu).',
     S({'ruta': {'type': 'string'}, 'solo_custom': {'type': 'boolean'}, 'filtro': {'type': 'string'}}, ['ruta'])),
    ('cambiar_parametro', 'Cambia un parametro. Menus aceptan nombre o label. Si tiene expresion pide forzar=true.',
     S({'ruta': {'type': 'string'}, 'par': {'type': 'string'}, 'valor': {}, 'forzar': {'type': 'boolean'}}, ['ruta', 'par', 'valor'])),
    ('listar_nodos', 'Lista hijos de un COMP hasta cierta profundidad (default 1).',
     S({'ruta': {'type': 'string'}, 'profundidad': {'type': 'integer'}})),
]


def call_tool(name, args):
    res = td(name, args, timeout=600 if name == 'correr_script' else 60)
    if name == 'correr_script':
        txt = res['salida'] or '(sin salida)'
        if not res['ok']:
            txt += '\n--- ERROR ---\n' + res['error']
        txt += '\n[%s, %ss]' % (res['ruta'], res['segundos'])
        return [{'type': 'text', 'text': txt}], not res['ok']
    content = [{'type': 'text', 'text': json.dumps(res, ensure_ascii=False, indent=1)}]
    if name == 'ver_salida':
        nota = None
        for cand in [res.get('ruta'), res.get('preview')]:
            if not cand:
                continue
            try:
                raw = open(cand, 'rb').read()
            except Exception as e:
                nota = 'No se pudo leer %s: %s' % (cand, e)
                continue
            if len(raw) <= MAX_IMG:
                mime = 'image/png' if cand.endswith('.png') else 'image/jpeg'
                content.append({'type': 'image', 'data': base64.b64encode(raw).decode(), 'mimeType': mime})
                nota = None
                break
            nota = 'Imagen de %.1f MB > limite %.0f MB: %s' % (len(raw) / 1048576.0, MAX_IMG / 1048576.0, cand)
        if nota:
            content.append({'type': 'text', 'text': nota})
    return content, False


def handle(msg):
    m, mid = msg.get('method'), msg.get('id')
    if mid is None:
        return None  # notificacion
    if m == 'initialize':
        r = {'protocolVersion': (msg.get('params') or {}).get('protocolVersion', PROTO),
             'capabilities': {'tools': {}}, 'serverInfo': {'name': 'touchdesigner', 'version': '1.0'}}
    elif m == 'ping':
        r = {}
    elif m == 'tools/list':
        r = {'tools': [{'name': n, 'description': d, 'inputSchema': s} for n, d, s in TOOLS]}
    elif m == 'tools/call':
        p = msg.get('params') or {}
        try:
            content, err = call_tool(p.get('name'), p.get('arguments') or {})
        except Exception as e:
            content, err = [{'type': 'text', 'text': str(e)}], True
        r = {'content': content, 'isError': err}
    else:
        return {'jsonrpc': '2.0', 'id': mid, 'error': {'code': -32601, 'message': 'metodo no soportado: %s' % m}}
    return {'jsonrpc': '2.0', 'id': mid, 'result': r}


def main():
    out = sys.stdout.buffer
    for line in sys.stdin.buffer:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line.decode('utf-8')))
        except Exception as e:
            resp = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': str(e)}}
        if resp is not None:
            out.write(json.dumps(resp, ensure_ascii=False).encode('utf-8') + b'\n')
            out.flush()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'probar':   # python td_mcp_server.py probar
        print(json.dumps(td('estado'), indent=1))
    else:
        main()
