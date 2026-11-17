# instalar_proyecto.py — instala los modulos que proyecto.json -> "modulos" tenga en true (armar.py lo corre).
exec(open(project.folder + '/modulos/modulos.py', encoding='utf-8').read(), dict(globals(), ACCION='proyecto'))
