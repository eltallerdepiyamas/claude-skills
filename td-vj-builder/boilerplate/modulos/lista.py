# lista.py — catalogo de modulos: que hay y que esta instalado en este .toe.
exec(open(project.folder + '/modulos/modulos.py', encoding='utf-8').read(), dict(globals(), ACCION='lista'))
