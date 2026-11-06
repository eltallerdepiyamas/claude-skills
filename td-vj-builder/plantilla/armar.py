# armar.py — aplica proyecto.json a la COPIA de un show y reconstruye todo. Idempotente.
# No corre en BOILERPLATE_TD (candado: ES_BOILERPLATE).
#   Textport:  exec(open(project.folder + '/armar.py', encoding='utf-8').read())
import json, os, traceback

F = project.folder
if os.path.exists(F + '/ES_BOILERPLATE'):
    raise SystemExit('[alto] esto es la plantilla: copia la carpeta y borra ES_BOILERPLATE')
cfg = json.load(open(F + '/proyecto.json', encoding='utf-8'))
R = op('/project2')
S = R.op('show')
E = R.op('base17/escena_modular')


def paso(nombre, ruta):
    try:
        p = F + '/' + ruta
        exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), dict(globals(), __file__=p, __name__='__armar__'))
        print('  [ok]', nombre)
    except BaseException:
        print('  [X]', nombre)
        traceback.print_exc()


print('==== armar: %s ====' % (cfg.get('nombre') or project.name))
S.par.W, S.par.H = cfg['resolucion']['w'], cfg['resolucion']['h']
if cfg.get('camaras', {}).get('en_multicam') and cfg.get('modulos', {}).get('escena_modular', True):
    E.par.Int = cfg['camaras']['en_multicam']
S.par.Master = 1
a = S.par.Audioarchivo          # audio por default: la rola de ejemplo de TD; si pones otra, se respeta
if a.mode == ParMode.CONSTANT and (not a.val or 'silencio' in a.val):
    a.expr = "app.samplesFolder + '/Audio/JeremyCaulfield_www.dumb-unit.com.mp3'"
    a.mode = ParMode.EXPRESSION
print('  [ok] resolucion', S.par.W.eval(), S.par.H.eval(), '· camaras', E.par.Int.eval())
mods = cfg.get('modulos', {})
if not mods.get('escena_modular', True):
    paso('solo visuales', 'builders/herramientas/solo_visuales.py')
paso('visuales, FX, escenas y UI', 'builders/build_all.py')
if mods.get('escena_modular', True):
    paso('menu de escenas', 'builders/herramientas/registrar_layouts.py')
    paso('entradas con la paleta', 'builders/herramientas/setup_entradas.py')
if not mods.get('escena_modular', True):
    paso('paleta en show', 'builders/herramientas/paleta_show.py')
paso('UI', 'builders/herramientas/setup_ui.py')
paso('Stream Deck', 'control/actualizar_companion.py')
if cfg.get('modulos', {}).get('escena_modular', True):
    paso('diagnostico', 'control/diag_todo.py')
print('==== listo. Fuera de TD: python control/gen_companion.py e importar en Companion ====')
