# recargar_callbacks.py — vuelve a copiar td_mcp_callbacks.py al Text DAT 'callbacks'
# de /project2/td_mcp SIN regenerar el token (a diferencia de setup_td_mcp.py).
# OJO (2026-11-04): cambiar el texto de los callbacks deja colgado el Web Server DAT, aun diferido.
# Por eso, despues de cambiarlo, apaga y vuelve a prender el web server (Activo off -> on).
# Correrlo desde el Textport es lo mas seguro:
#   exec(open(project.folder + '/tools/td_mcp/td_side/recargar_callbacks.py', encoding='utf-8').read())
src = project.folder + '/tools/td_mcp/td_side/td_mcp_callbacks.py'
run("c = op('/project2/td_mcp'); c.op('callbacks').text = open(args[0], encoding='utf-8').read(); c.par.Activo = False",
    src, delayFrames=2)
run("op('/project2/td_mcp').par.Activo = True", delayFrames=20)
print('callbacks se recargan en 2 frames (y el web server se reinicia) desde', src)
