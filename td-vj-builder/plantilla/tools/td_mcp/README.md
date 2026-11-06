# td_mcp — Claude Code controla TouchDesigner

```
Claude Code ──stdio──> server/td_mcp_server.py ──HTTP 127.0.0.1:9980──> /project2/td_mcp (Web Server DAT)
```

- Sin dependencias (Python 3.8+ de Windows, nada de `pip install`).
- Solo localhost: TD rechaza IPs que no sean 127.0.0.1/::1, peticiones con `Origin` (navegadores) y sin token.
- El token se regenera en cada setup y queda en `tools/td_mcp/.token` (no compartirlo).
- Único "código arbitrario": `correr_script`, y solo `.py` dentro de `project.folder`.
- Solo lectura: `/project2/td_mcp` → pestaña MCP → **Solo lectura** bloquea `correr_script` y `cambiar_parametro`.
- Apagar todo: **Activo** en off (o `op('/project2/td_mcp').destroy()`).

## 1. En TouchDesigner (Textport)

```python
exec(open(project.folder + '/tools/td_mcp/td_side/setup_td_mcp.py', encoding='utf-8').read())
```

Debe imprimir `td_mcp listo: /project2/td_mcp -> http://127.0.0.1:9980/api`. Se puede correr las veces que quieras.
Al abrir el `.toe` se vuelve a correr solo (Execute DAT `al_arrancar`), así el token siempre coincide. Si Windows pregunta por el firewall, **Cancelar** está bien (solo usamos localhost).

## 2. Probar sin Claude (PowerShell, en esta carpeta)

```bash
python server/td_mcp_server.py probar
```

Debe imprimir el nombre del proyecto y la versión de TD.

## 3. Registrar en Claude Code

Desde `01. EDITABLES` (queda en `.mcp.json` del proyecto):

```bash
claude mcp add touchdesigner --scope project -- python "tools/td_mcp/server/td_mcp_server.py"
```

O a mano, `.mcp.json` en `01. EDITABLES`:

```json
{
  "mcpServers": {
    "touchdesigner": {
      "command": "python",
      "args": ["tools/td_mcp/server/td_mcp_server.py"]
    }
  }
}
```

Reiniciar la sesión de Claude Code y revisar con `/mcp` (o `claude mcp list`) que diga *connected*.

## Herramientas

| Tool | Qué hace |
|---|---|
| `estado` | ping: proyecto, carpeta, versión, fps, solo-lectura |
| `correr_script(ruta)` | corre un `.py` del proyecto (ej. `control/diag_todo.py`) y devuelve lo que imprime + traceback |
| `errores(ruta_op)` | errores/warnings/script errors recursivos (default `/project2`) |
| `ver_salida(ruta_top, formato)` | guarda el TOP en `%TEMP%\td_mcp\` y devuelve ruta + imagen |
| `leer_parametros(ruta, solo_custom, filtro)` | valores, modo, expresión, bind, opciones de menú |
| `cambiar_parametro(ruta, par, valor, forzar)` | cambia un par (menú por nombre o label); con expresión pide `forzar` |
| `listar_nodos(ruta, profundidad)` | hijos de un COMP |

Prueba de aceptación: pedirle a Claude *"corre control/diag_todo.py"* y *"ver_salida de /project2/base17/escena_modular/blend_switch"*.

## Notas

- `ver_salida` acepta un TOP o un COMP con Out TOP (ej. `blend_switch` → su `out1`). Con PNG también guarda un `_preview.jpg` y manda ese si el PNG pasa de 4 MB (un 1080p pesa ~4.5 MB).
- Cambiar los callbacks: **cambiar el texto de `callbacks` cuelga el Web Server DAT** (pasó 2 veces el 2026-11-04, una con la recarga diferida). Hacerlo desde el **Textport**: el setup del paso 1, o `recargar_callbacks.py` (cambia el texto y reinicia el web server con **Activo** off → on, sin regenerar token). Si el MCP deja de responder: apagar y prender **Activo** en `/project2/td_mcp`.
- `leer_parametros` ya no truena con menús vacíos (`menuNames` = None).
- Cambios en `server/td_mcp_server.py` piden reiniciar el MCP en Claude Code (`/mcp` → reconnect, o reiniciar la sesión).

- Los scripts corren en el hilo principal de TD: un script largo congela el output mientras corre (igual que en el Textport). No usar en pleno show.
- Puerto: cambiar `PORT` en `setup_td_mcp.py` y volver a correrlo (el server lo lee del `.token`).
- Para el boilerplate: copiar `tools/td_mcp/` completo; no depende de nada del show.
