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
#   /td/pantallas <0|1>  -> prende (1) / apaga (0) el test pattern (reemplaza la salida master por el patron de /project2/show)
#   /td/inc/pantallas    -> alterna (toggle) el estado del test pattern

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

def _show():
	return op('/project2/show')

def showSet(name, v):
	s = _show()
	p = getattr(s.par, name, None) if s is not None else None
	if p is None:
		return
	if p.isMenu:
		if isinstance(v, str):
			if v in p.menuNames: p.val = v
			elif v in p.menuLabels: p.menuIndex = p.menuLabels.index(v)
		else:
			p.menuIndex = int(v)
	elif p.isPulse:
		p.pulse()
	elif p.isToggle:
		p.val = bool(v)
	else:
		p.val = v

def showInc(name, delta):
	s = _show()
	p = getattr(s.par, name, None) if s is not None else None
	if p is None:
		return
	if p.isMenu:
		n = len(p.menuNames)
		if n:
			p.menuIndex = (p.menuIndex + int(delta)) % n
	elif p.isToggle:
		p.val = not p.eval()
	else:
		p.val = p.eval() + float(delta)

def setFx(i):
	if FX_SWITCH is not None and 0 <= int(i) < len(FX_SWITCH.inputs):
		FX_SWITCH.par.index = int(i)

def setVisual(n):
	# switch2 = los 16 visuales directo (entrada n-1 = baseN). Si aun existe el esquema viejo
	# (switch1 = 1-8, switch3 = 9-16), se usa ese.
	n = int(n)
	if n < 1 or VIS_MAIN is None:          # mas de 16: shows con bancos grandes (ui_bancos.py)
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

def ui(on):
	"""Abre o cierra /perform (ventana UI). Botón del Companion es toggle."""
	on = bool(on)
	pw = op('/perform')
	if pw is None:
		return
	if on:
		pw.par.winopen.pulse()
	else:
		pw.par.winclose.pulse()
	TARGET.store('ui_on', on)
	co = TARGET.op('companion_out')
	if co is not None:
		try:
			co.sendOSC('/custom-variable/ui/value', ['ON' if on else ''])
		except Exception:
			pass


def pantallas(on):
	"""Prende o apaga el test pattern: /project2/show.Pantallas = bool(on).
	Al prender desde Companion siempre fuerza el monitor 2 (botón de prueba rápida)."""
	on = bool(on)
	s = op('/project2/show')
	if s is None or not hasattr(s.par, 'Pantallas'):
		return
	if on and hasattr(s.par, 'Monitor'):
		# botón rápido: siempre a la segunda pantalla, nunca al primario
		s.par.Monitor.val = 'monitor2'
	s.par.Pantallas.val = on
	# sincroniza el latch del Companion
	co = TARGET.op('companion_out')
	if co is not None:
		try:
			co.sendOSC('/custom-variable/pantallas/value', ['ON' if on else ''])
		except Exception:
			pass


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
	if len(parts) >= 3 and parts[1] == 'xl':   # --- XL (control/instalar_xl_osc.py) ---
		_xl(parts[2], args)
		return
	# MODO SHOW (candado, show.Modoshow): el Stream Deck no dispara thumbs, demo ni test de pantallas
	_c = getattr(op('/project2/show').par, 'Modoshow', None)
	if _c is not None and _c.eval():
		if parts[-1] in ('thumbs', 'pantallas', 'Demo', 'Democada', 'Recsel') or (len(parts) > 1 and parts[1] == 'show'):
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
		ui(int(args[0]) if args else 1)
	elif len(parts) == 3 and parts[1] == 'inc' and parts[2] == 'ui':
		ui(not TARGET.fetch('ui_on', False, search=False))
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
	elif len(parts) == 2 and parts[1] == 'pantallas':
		pantallas(int(args[0]) if args else 1)
	elif len(parts) == 3 and parts[1] == 'inc' and parts[2] == 'pantallas':
		s = op('/project2/show')
		pantallas(not (s.par.Pantallas.eval() if s and hasattr(s.par, 'Pantallas') else False))
	elif len(parts) == 2:
		setPar(parts[1], args[0] if args else 1)
	elif len(parts) == 3 and parts[1] == 'show':
		showSet(parts[2], args[0] if args else 1)
	elif len(parts) == 4 and parts[1] == 'show' and parts[2] == 'inc':
		showInc(parts[3], args[0] if args else 1)
	elif len(parts) == 3 and parts[1] == 'inc':
		incPar(parts[2], args[0] if args else 1)
	return


# --- XL (control/instalar_xl_osc.py) ---
def _xl(cmd, args):
    """Botones del Stream Deck XL (gen_companion_xl.py). No pasa por el candado, igual que la UI."""
    s = op('/project2/show')
    ui = op('/project2/ui_perform/ui_lib')
    a = args[0] if args else None
    try:
        me.time.play = True    # el fundido del BLACKOUT y los titulos se congelan con la linea de tiempo en pausa
    except Exception:
        pass
    if cmd == 'blackout':
        if ui is not None:
            ui.module.elegir('BLACKOUT', '')
    elif cmd == 'camfull':
        if ui is not None:
            ui.module.elegir('LIMPIO', '')
        elif TARGET.op('layout_sc_limpio') is not None:
            TARGET.par.Modoescena = 'layout_sc_limpio'
    elif cmd == 'tituloaire':
        s.par.Tituloaire = not s.par.Tituloaire.eval()
    elif cmd == 'titulo' and a is not None:
        clave = str(a)
        if clave in s.par.Titulo.menuNames:
            if s.par.Titulo.eval() == clave and clave in ('cancion', 'creditos'):
                getattr(s.par, 'Titulo' + clave).pulse()     # vuelve a preparar (p. ej. cambio la cancion)
            else:
                s.par.Titulo = clave
    elif cmd == 'cancion':
        op('/project2/show/setlist_lib').module.mover(int(a) if a is not None else 1)
    elif cmd == 'ircancion' and a is not None:
        op('/project2/show/setlist_lib').module.ir(int(a))
    elif cmd == 'modoshow':
        if ui is not None:
            ui.module.elegir('MODOSHOW', '')
        else:
            s.par.Modoshow = not s.par.Modoshow.eval()
    elif cmd.startswith(('dial', 'reset')) and cmd[-1:].isdigit():
        _xl_perilla(cmd, a)
        return
    elif cmd == 'foco':
        _xl_foco(int(a) if a is not None else 1)
        return
    elif cmd == 'reaccion':
        # perilla 6: Reaccion global del audio (hub, pestana Audio) · +1 / -1 = 5 % · 0 = de fabrica (1.0)
        p = getattr(s.par, 'Reaccion', None)
        if p is not None:
            d = float(a) if a is not None else 0.0
            p.val = p.default if d == 0 else min(max(p.eval() + 0.05 * d, p.normMin), p.normMax)
    fb = s.op('xl_feedback') if s is not None else None
    if fb is not None:
        try:
            fb.module.enviar()
        except Exception as e:
            debug('xl_feedback:', e)

# --- perillas del Stream Deck + XL: mueven los 5 sliders de lo enfocado en AJUSTES (mix_feedback -> mix_comp)
XL_CINCO = ['Mezcla', 'Tiempo', 'Distorsion', 'Color', 'Firma']
XL_PASO = 0.02      # 2 % del rango por cada clic de la perilla

def _xl_cinco(c):
    """Los mismos 5 que muestra la pagina AJUSTES (misma regla que five() de mix_feedback)."""
    if c is None:
        return []
    if all(getattr(c.par, n, None) is not None for n in XL_CINCO):
        return [getattr(c.par, n) for n in XL_CINCO]
    pg = next((g for g in c.customPages if g.name in ('Layout', 'Visual', 'Filter')), None)
    if pg is None:
        return []
    return [p for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')][:5]

def _xl_perilla(cmd, a):
    """dialN <+1|-1> = sube / baja el slider N · resetN = lo regresa a su valor de fabrica."""
    path = TARGET.fetch('mix_comp', '', search=False, storeDefault=False)
    pars = _xl_cinco(op(path) if path else None)
    i = int(cmd[-1]) - 1
    if not 0 <= i < len(pars):
        return
    p = pars[i]
    if cmd.startswith('reset'):
        p.val = p.default
        return
    lo, hi = p.normMin, p.normMax
    if hi == lo:
        lo, hi = p.min, p.max
    d = float(a) if a is not None else 1.0
    if p.isInt:
        v = p.eval() + (1 if d > 0 else -1)
    else:
        v = p.eval() + d * XL_PASO * (hi - lo)
    p.val = min(max(v, lo), hi)

def _xl_foco(d):
    """Perilla 6: ESCENA -> VISUAL -> FX (o al reves). Lo aplica mix_feedback en su siguiente envio."""
    orden = ('layout', 'visual', 'fx')
    fb = TARGET.op('mix_feedback')
    cur = fb.fetch('mix_foco', 'layout', storeDefault=False) if fb is not None else 'layout'
    k = orden.index(cur) if cur in orden else 0
    TARGET.store('mix_foco_manual', orden[(k + (1 if d >= 0 else -1)) % 3])
