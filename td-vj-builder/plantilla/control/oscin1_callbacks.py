# Callbacks del OSC In DAT `oscin1` (puerto 7010; el 7000 lo usa Resolume Arena) en escena_modular.
# control/actualizar_companion.py copia este archivo al DAT de callbacks de oscin1.
#   /td/<Par> valor      -> setea un parametro custom de escena_modular (menus: por nombre, etiqueta o indice)
#   /td/inc/<Par> delta  -> suma delta a un parametro (en menus recorre las opciones en ciclo, p. ej. Slot1..5;
#                           en on/off lo invierte, p. ej. Rotar)
#   /td/ui 1             -> abre la UI de perform como ventana aparte
#   /td/fx indice        -> elige la entrada de FX_SWITCH (0 = base17 sin FX)
#   /td/visual base      -> elige el visual baseN (switch2: entrada N-1 = baseN)
#   /td/foco tipo        -> pagina MIX: muestra los 5 parametros del layout / visual / fx activo
#                           ('next' = el siguiente: LAYOUT -> VISUAL -> FX)
#   /td/audio N          -> pagina MIX: el parametro N (1-5) del enfocado empuja el audio (otra vez = apagar)
#                           · N = 0 prende / apaga el audio del enfocado
#   /td/audiomult d      -> pagina MIX: sensibilidad del audio del enfocado (+/- 0.1 por paso)
#   /td/rotarajuste d    -> pagina CAMARAS: +1 / -1 segun el modo de rotacion (tiempo: mas rapido / lento ·
#                           audio: mas / menos sensibilidad)

TARGET    = op('/project2/base17/escena_modular')
FX_SWITCH = op('/project2/switch23')
VIS_MAIN  = op('/project2/switch2')
VIS_A     = op('/project2/switch1')     # base1-8
VIS_B     = op('/project2/switch3')     # base9-16

def setPar(name, v):
	p = getattr(TARGET.par, name, None)
	if p is None:
		debug('OSC: no existe el parametro', name)
		return
	if p.isMenu:
		if isinstance(v, str):
			if v in p.menuNames:
				p.val = v
			elif v in p.menuLabels:
				p.menuIndex = p.menuLabels.index(v)
		else:
			p.menuIndex = int(v)
	elif p.isPulse:
		p.pulse()
	elif p.isToggle:
		p.val = bool(v)
	else:
		p.val = v

def incPar(name, delta):
	p = getattr(TARGET.par, name, None)
	if p is None:
		return
	if p.isMenu:
		n = len(p.menuNames)
		if n:
			p.menuIndex = (p.menuIndex + int(delta)) % n
	elif p.isToggle:
		p.val = not p.eval()
	else:
		p.val = p.eval() + delta

def setFx(i):
	if FX_SWITCH is not None and 0 <= int(i) < len(FX_SWITCH.inputs):
		FX_SWITCH.par.index = int(i)

def setVisual(n):
	# switch2 = los 16 visuales directo (entrada n-1 = baseN). Si aun existe el esquema viejo
	# (switch1 = 1-8, switch3 = 9-16), se usa ese.
	n = int(n)
	if n < 1 or VIS_MAIN is None:
		return
	if VIS_A is not None and VIS_B is not None and len(VIS_MAIN.inputs) == 2:
		if n <= 8:
			VIS_A.par.index = n - 1
			VIS_MAIN.par.index = 0
		else:
			VIS_B.par.index = n - 9
			VIS_MAIN.par.index = 1
	elif n - 1 < len(VIS_MAIN.inputs):
		VIS_MAIN.par.index = n - 1

def resetActivo(aplicar=True, escena=False, videos=True):
	# Lo enfocado en AJUSTES (o la escena activa): sliders a su default, reloj y feedback a cero, videos al inicio.
	c = None if escena else focused()
	c = c or TARGET.op(TARGET.par.Modoescena.eval())
	if c is None:
		return []
	lista = []
	for pg in c.customPages:
		if pg.name not in ('Layout', 'Visual', 'Filter'):
			continue
		for p in pg.pars:
			if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA') and p.mode == ParMode.CONSTANT:
				lista.append((p.name, p.eval(), p.default))
				if aplicar:
					p.val = p.default
	if aplicar:
		fase = c.op('tdvj_fase')
		if fase is not None:
			fase.par.resetpulse.pulse()
		redes = [c, op('/project1')]
		for r in redes:
			for f in r.findChildren(type=feedbackTOP):
				f.par.resetpulse.pulse()
		if videos:
			for m in TARGET.findChildren(type=moviefileinTOP, depth=1):
				m.par.cuepulse.pulse()
	return lista

def focused():
	"""Lo que esta enfocado en la pagina MIX (layout / visual / FX); lo guarda mix_feedback."""
	path = TARGET.fetch('mix_comp', '', search=False, storeDefault=False)
	return op(path) if path else None

def setAudio(i):
	# i = 1..5: ese parametro empuja el audio (si ya lo hacia, se apaga) · i = 0: audio on/off
	c = focused()
	on = getattr(c.par, 'Audioreact', None) if c is not None else None
	if on is None:
		return
	if i <= 0:
		on.val = not on.eval()
		return
	tgt = getattr(c.par, 'Audiotarget', None)
	if tgt is None or i > len(tgt.menuNames):
		return
	if on.eval() and tgt.menuIndex == i - 1:
		on.val = False
	else:
		tgt.menuIndex = i - 1
		on.val = True

def incAudiomult(delta):
	c = focused()
	m = getattr(c.par, 'Audiomult', None) if c is not None else None
	if m is not None:
		m.val = max(0.0, m.eval() + delta)

def rotarAjuste(d):
	# CAMARAS: el boton - / + ajusta lo que importa en el modo de rotacion actual
	#   Por tiempo:   +1 = MAS RAPIDO (cambia mas seguido, -0.5 s) · -1 = MAS LENTO
	#   Con el audio: +1 = MAS SENS (+0.25)                         · -1 = MENOS SENS
	p = TARGET.par
	if getattr(p, 'Rotarmodo', None) is None:
		return
	if p.Rotarmodo.eval() == 'audio':
		p.Rotarsens.val = max(0.5, min(6.0, p.Rotarsens.eval() + 0.25 * d))
	else:
		p.Rotarcada.val = max(0.5, min(30.0, p.Rotarcada.eval() - 0.5 * d))

def onReceiveOSC(dat, rowIndex, message, byteData, timeStamp, address, args, peer):
	parts = address.strip('/').split('/')
	if parts[0] != 'td':
		return
	if len(parts) == 2 and parts[1] in ('Modoescena', 'visual', 'fx'):
		# el cambio viene del Stream Deck (que ya salta solo a MIX): mix_feedback no lo vuelve a mandar
		TARGET.store('deck_t', absTime.seconds)
		# y AJUSTES muestra lo que tocaste, aunque ya estuviera activo
		TARGET.store('mix_foco_manual', {'Modoescena': 'layout'}.get(parts[1], parts[1]))
	if len(parts) == 2 and parts[1] == 'fx':
		setFx(args[0] if args else 0)
	elif len(parts) == 2 and parts[1] == 'visual':
		setVisual(args[0] if args else 1)
	elif len(parts) == 2 and parts[1] == 'foco':
		# pagina MIX: que parametros mostrar (layout / visual / fx); lo lee mix_feedback
		TARGET.store('mix_foco_manual', str(args[0]).lower() if args else 'layout')
	elif len(parts) == 2 and parts[1] == 'resetfb':
		op('/project2/ui_perform/ui_lib').module.elegir('RESETFB', '')
	elif len(parts) == 2 and parts[1] == 'ui':
		op('/perform').par.winopen.pulse()
	elif len(parts) == 2 and parts[1] == 'thumbs':
		op('/project2/ui_perform/ui_lib').module.elegir('THUMBS', '')
	elif len(parts) == 2 and parts[1] == 'rampa':
		op('/project2/show').par.Rampa = float(args[0]) if args else 0
	elif len(parts) == 2 and parts[1] == 'reset':
		resetActivo()
	elif len(parts) == 2 and parts[1] == 'audio':
		setAudio(int(args[0]) if args else 0)
	elif len(parts) == 2 and parts[1] == 'audiomult':
		incAudiomult(float(args[0]) * 0.1 if args else 0.1)
	elif len(parts) == 2 and parts[1] == 'rotarajuste':
		rotarAjuste(int(args[0]) if args else 1)
	elif len(parts) == 2:
		setPar(parts[1], args[0] if args else 1)
	elif len(parts) == 3 and parts[1] == 'inc':
		incPar(parts[2], args[0] if args else 1)
	return
