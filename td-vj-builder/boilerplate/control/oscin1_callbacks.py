# Callbacks del OSC In DAT `oscin1` (puerto 7010; el 7000 lo usa Resolume Arena) en escena_modular.
# Copiar el contenido completo a oscin1_callbacks.
#   /td/<Par> valor      -> setea un parametro custom de escena_modular
#   /td/inc/<Par> delta  -> suma delta a un parametro
#   /td/fx indice        -> elige la entrada de FX_SWITCH (0 = base17 sin FX)

TARGET    = op('/project2/base17/escena_modular')
FX_SWITCH = op('/project2/switch23')

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
	if p is not None:
		p.val = p.eval() + delta

def setFx(i):
	if FX_SWITCH is not None and 0 <= int(i) < len(FX_SWITCH.inputs):
		FX_SWITCH.par.index = int(i)

def onReceiveOSC(dat, rowIndex, message, byteData, timeStamp, address, args, peer):
	parts = address.strip('/').split('/')
	if parts[0] != 'td':
		return
	if len(parts) == 2 and parts[1] == 'fx':
		setFx(args[0] if args else 0)
	elif len(parts) == 2:
		setPar(parts[1], args[0] if args else 1)
	elif len(parts) == 3 and parts[1] == 'inc':
		incPar(parts[2], args[0] if args else 1)
	return
