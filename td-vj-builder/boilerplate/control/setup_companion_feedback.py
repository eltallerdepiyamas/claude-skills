# =============================================================
# setup_companion_feedback.py
# TD -> Companion: cada vez que cambia un parametro de escena_modular,
# actualiza la custom variable de Companion correspondiente.
#   Int        -> custom:cams   (contador de la pagina CAMARAS)
#   Modoescena -> custom:escena (enciende el boton de la escena activa)
#   Menu2      -> custom:cam
#   Index      -> custom:hero
# Asi el Stream Deck queda sincronizado aunque cambies algo con el
# mouse, el MIDI o el Beatstep.
#
# Requiere: Companion con el servicio OSC activo (puerto 12320).
# Uso (Textport):
#   exec(open(project.folder + '/control/setup_companion_feedback.py').read())
# Se puede volver a correr: recrea solo sus propios operadores.
# =============================================================

SCENE_PATH     = '/project2/base17/escena_modular'
COMPANION_HOST = '127.0.0.1'
COMPANION_PORT = 12320

PAREXEC = '''# par de escena_modular -> custom variable de Companion
VARS = {'Int': 'cams', 'Modoescena': 'escena', 'Menu2': 'cam', 'Index': 'hero'}

def value_for(par):
	if par.name == 'Modoescena':
		return par.menuLabels[par.menuIndex]
	if par.isMenu:
		return str(par.menuIndex)
	return str(int(par.eval()))

def send(par):
	name = VARS.get(par.name)
	if name:
		op('companion_out').sendOSC('/custom-variable/%s/value' % name, [value_for(par)])

def send_all():
	for n in VARS:
		p = getattr(parent().par, n, None)
		if p is not None:
			send(p)

def onValueChange(par, prev):
	send(par)
	return
'''


def _replace(parent, optype, name, x, y):
    old = parent.op(name)
    if old is not None:
        old.destroy()
    o = parent.create(optype, name)
    o.nodeX, o.nodeY = x, y
    return o


def run():
    scene = op(SCENE_PATH)
    if scene is None:
        print('[error] no encuentro', SCENE_PATH)
        return

    x, y = -1200, -1200
    out = _replace(scene, oscoutDAT, 'companion_out', x, y)
    # el nombre del parametro de direccion cambia entre versiones de TD
    addr = next((p for p in out.pars() if 'address' in p.label.lower() and not p.isMenu), None)
    port = next((p for p in out.pars() if p.label.lower() in ('network port', 'port')), None)
    if addr is None or port is None:
        print('[error] no encontre direccion/puerto en el OSC Out DAT:', [(p.name, p.label) for p in out.pars()][:20])
        return
    addr.val = COMPANION_HOST
    port.val = COMPANION_PORT

    pe = _replace(scene, parameterexecuteDAT, 'companion_feedback', x + 200, y)
    pe.text = PAREXEC
    pe.par.op = scene.path
    pe.par.pars = 'Int Modoescena Menu2 Index'
    if hasattr(pe.par, 'onpulse'):
        pe.par.onpulse = False
    pe.par.valuechange = True

    pe.module.send_all()
    print('[ok] TD -> Companion en %s:%d. Estado actual enviado.' % (COMPANION_HOST, COMPANION_PORT))


run()
