# =============================================================
# setup_companion_feedback.py
# TD -> Companion: cada vez que cambia un parametro de escena_modular,
# actualiza la custom variable de Companion correspondiente.
#   Int        -> custom:cams   (contador de la pagina CAMARAS)
#   Modoescena -> custom:escena (enciende el boton de la escena activa)
#   Menu2      -> custom:cam    (Camara unica: enciende su boton)
#   Slot1..5   -> custom:slot1..5 (camara de cada lugar, se ve en el boton)
#   Rotar / Rotarcada -> custom:rotar (ON/OFF) / custom:rotarcada ("4 s")
#   Rotar*     -> custom:rotarinfo ("POR TIEMPO - 4 S" / "CON EL AUDIO - SENS 1.5") y los textos de los
#                 botones -/+ (custom:rotar_menos / rotar_mas: MAS LENTO / MAS RAPIDO o MENOS SENS / MAS SENS)
# mix_feedback (setup_mix_feedback.py) llama send_all() cada ~2 s: si Companion se reinicia, se pone al dia.
# Asi el Stream Deck queda sincronizado aunque cambies algo con el
# mouse, el MIDI o el Beatstep.
#
# Requiere: Companion con el servicio OSC activo (puerto 12321, el de fabrica).
# Uso (Textport):
#   exec(open(project.folder + '/control/setup_companion_feedback.py').read())
# Se puede volver a correr: recrea solo sus propios operadores.
# =============================================================

SCENE_PATH     = '/project2/base17/escena_modular'
COMPANION_HOST = '127.0.0.1'
COMPANION_PORT = 12321   # el de fabrica de Companion (su asistente de configuracion lo regresa a este)

PAREXEC = '''# par de escena_modular -> custom variable de Companion
VARS = {'Int': 'cams', 'Modoescena': 'escena', 'Menu2': 'cam',
        'Slot1': 'slot1', 'Slot2': 'slot2', 'Slot3': 'slot3', 'Slot4': 'slot4', 'Slot5': 'slot5',
        'Rotar': 'rotar', 'Rotarcada': 'rotarcada', 'Rotarmodo': 'rotarmodo',
        'Rec': 'rec', 'Demo': 'demo', 'Democada': 'democada', 'Recsel': 'recfuente'}

def value_for(par):
	if par.isMenu and not par.menuNames:
		return ''
	# Modoescena y Menu2 van tal cual: los botones comparan contra su etiqueta para encenderse
	if par.isMenu and par.name in ('Modoescena', 'Menu2'):
		return par.menuLabels[par.menuIndex]
	# lo que solo se lee en el boton, en MAYUSCULAS
	if par.isMenu and (par.name in ('Rotarmodo', 'Recsel') or par.name.startswith('Slot')):
		return par.menuLabels[par.menuIndex].upper()
	if par.isToggle:
		return 'ON' if par.eval() else 'OFF'
	if par.isFloat:
		return '%g s' % round(par.eval(), 1)
	if par.isMenu:
		return str(par.menuIndex)
	return str(int(par.eval()))

def out(name, value):
	op('companion_out').sendOSC('/custom-variable/%s/value' % name, [value])

def send_rotar():
	# pagina CAMARAS: info de la rotacion en un boton y los botones -/+ segun el modo
	s = parent().par
	if getattr(s, 'Rotarmodo', None) is None:
		return
	if s.Rotarmodo.eval() == 'audio':
		out('rotarinfo', 'CON EL AUDIO - SENS %.1f' % s.Rotarsens.eval())
		out('rotar_menos', 'MENOS SENS')
		out('rotar_mas', 'MAS SENS')
	else:
		out('rotarinfo', 'POR TIEMPO - %g S' % round(s.Rotarcada.eval(), 1))
		out('rotar_menos', 'MAS LENTO')
		out('rotar_mas', 'MAS RAPIDO')

def send(par):
	name = VARS.get(par.name)
	if name:
		out(name, value_for(par))
	if par.name.startswith('Rotar'):
		send_rotar()

def send_pantallas():
	# estado del Test Pantallas (par toggle en /project2/show.Pantallas)
	s = op('/project2/show')
	out('pantallas', 'ON' if (s is not None and hasattr(s.par, 'Pantallas') and s.par.Pantallas.eval()) else '')

def send_all():
	for n in VARS:
		p = getattr(parent().par, n, None)
		if p is not None:
			send(p)
	send_rotar()
	send_pantallas()

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
    pe.par.pars = ('Int Modoescena Menu2 Slot1 Slot2 Slot3 Slot4 Slot5 Rotar Rotarcada Rotarmodo Rotarsens '
                   'Rec Demo Democada Recsel')
    if hasattr(pe.par, 'onpulse'):
        pe.par.onpulse = False
    pe.par.valuechange = True

    pe.module.send_all()

    # feedback de los params del hub /project2/show (pagina PANTALLAS)
    show = op('/project2/show')
    if show is not None:
        pe2 = _replace(show, parameterexecuteDAT, 'companion_feedback_show', -1200, -1400)
        pe2.text = PAREXEC_SHOW
        pe2.par.op = show.path
        pe2.par.pars = ('Pantallas Patron Monitor Pantallacompleta Ndi Glowon Glowforma Glowvel')
        if hasattr(pe2.par, 'onpulse'):
            pe2.par.onpulse = False
        pe2.par.valuechange = True
        pe2.module.send_all()
    print('[ok] TD -> Companion en %s:%d. Estado actual enviado.' % (COMPANION_HOST, COMPANION_PORT))


PAREXEC_SHOW = '''# params de /project2/show -> custom variables de Companion
VARS = {'Pantallas': 'pantallas', 'Patron': 'patron', 'Monitor': 'monitor',
        'Pantallacompleta': 'fullscreen', 'Ndi': 'ndi',
        'Glowon': 'glowon', 'Glowforma': 'glowforma', 'Glowvel': 'glowvel'}

def value_for(par):
	if par.isToggle:
		return 'ON' if par.eval() else ''
	if par.isMenu and par.menuNames:
		return par.menuLabels[par.menuIndex].upper()
	if par.isFloat:
		return '%.1f' % par.eval()
	return str(int(par.eval()))

def out(name, value):
	op('/project2/base17/escena_modular/companion_out').sendOSC('/custom-variable/%s/value' % name, [value])

def send(par):
	name = VARS.get(par.name)
	if name:
		out(name, value_for(par))

def send_all():
	for n in VARS:
		p = getattr(parent().par, n, None)
		if p is not None:
			send(p)

def onValueChange(par, prev):
	send(par)
'''


run()
