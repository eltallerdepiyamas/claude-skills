# =============================================================
# setup_td_mcp.py — crea /project2/td_mcp (Web Server DAT 127.0.0.1:PORT + callbacks).
# Idempotente: si ya existe, solo actualiza callbacks/puerto y conserva Readonly.
# No toca nada mas del show.
#   Textport:  exec(open(project.folder + '/tools/td_mcp/td_side/setup_td_mcp.py', encoding='utf-8').read())
# Quitarlo:   op('/project2/td_mcp').destroy()
# =============================================================
import os, secrets

PORT = 9980                      # libres: 7000 Resolume, 7010 OSC, 12320/12321 Companion
PARENT = '/project2'
NAME = 'td_mcp'
BASE = project.folder + '/tools/td_mcp'

padre = op(PARENT)
comp = padre.op(NAME)
if comp is None:
    comp = padre.create(baseCOMP, NAME)
    comp.nodeX, comp.nodeY = -1200, 1200
    comp.color = (0.25, 0.25, 0.25)
    comp.comment = 'Puente Claude Code (MCP). Ver tools/td_mcp/README.md'

# --- parametros propios ---
if not hasattr(comp.par, 'Readonly'):
    pg = comp.appendCustomPage('MCP')
    pg.appendToggle('Readonly', label='Solo lectura')
    pg.appendToggle('Activo', label='Activo')
    comp.par.Activo = True
    pg.appendInt('Puerto', label='Puerto')
comp.par.Puerto = PORT

# --- callbacks ---
cb = comp.op('callbacks') or comp.create(textDAT, 'callbacks')
cb.text = open(BASE + '/td_side/td_mcp_callbacks.py', encoding='utf-8').read()
cb.nodeX, cb.nodeY = 0, 0

# --- web server ---
ws = comp.op('webserver') or comp.create(webserverDAT, 'webserver')
ws.nodeX, ws.nodeY = 200, 0
ws.par.callbacks = cb
ws.par.port.expr = "parent().par.Puerto"
ws.par.active.expr = "parent().par.Activo"

# --- token (el server MCP lo lee de tools/td_mcp/.token) ---
tok = secrets.token_hex(16)
comp.store('td_mcp_token', tok)
with open(BASE + '/.token', 'w', encoding='utf-8') as f:
    f.write('%s\n%d\n' % (tok, PORT))

# el token vive en storage: hay que volver a correr el setup despues de abrir el .toe
# (o dejar que lo haga este Execute DAT al arrancar)
ex = comp.op('al_arrancar') or comp.create(executeDAT, 'al_arrancar')
ex.nodeX, ex.nodeY = 0, -150
ex.text = (
    "def onStart():\n"
    "    exec(open(project.folder + '/tools/td_mcp/td_side/setup_td_mcp.py', encoding='utf-8').read())\n"
    "    return\n")
ex.par.start = True

print('td_mcp listo: %s  ->  http://127.0.0.1:%d/api  (Readonly=%s, Activo=%s)' % (
    comp.path, PORT, comp.par.Readonly.eval(), comp.par.Activo.eval()))
print('token escrito en', BASE + '/.token')
