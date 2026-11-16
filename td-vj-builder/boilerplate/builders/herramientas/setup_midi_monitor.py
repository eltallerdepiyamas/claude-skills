# setup_midi_monitor.py: pestana "MIDI" en /project2/show con monitor en vivo.
# - Ultimo MIDI movido (texto)
# - Canal y Pad activo del Beatstep (lee /project2/bs_canal)
# - Visual al aire (nombre del base activo en switch2)
# - FX al aire (nombre del base activo en switch23, si hay FX)
# - Escena al aire (nombre del layout activo en escena_modular, si esta habilitada)
# - PANIC / Reset MIDI (apaga luces y resetea switch2)
# Idempotente. Se adapta al rig del show: si falta algun switch, oculta el par.
R = op('/project2')
SHOW = R.op('show')
assert SHOW is not None, 'falta /project2/show'

# ---- Libreria interna para resolver nombre del visual/FX/escena ----
LIB_PY = '''# generado por setup_midi_monitor.py
# Devuelve el nombre legible del visual, FX o escena activos.

def _nombre_desde_switch(sw_path, lib_path):
	sw = op(sw_path)
	if sw is None: return '-'
	k = int(sw.par.index.eval())
	if k >= len(sw.inputs): return '-'
	# Casa Bacardi (con bancos): vis_nombres_tabla tiene idx -> nombre
	tbl = op('/project2/vis_nombres_tabla')
	if tbl is not None and k < tbl.numRows:
		v = tbl[k, 0].val
		if v: return v
	# Canon del boilerplate: resolver base via la libreria del rig
	lib = op(lib_path)
	if lib is not None:
		try:
			b = lib.module.resolve(sw.inputs[k])
			if b is not None:
				return b.fetch('nombre', b.name)
		except Exception:
			pass
	# Fallback: nombre del input directo
	src = sw.inputs[k]
	return src.name if src else '-'


def nombre_visual():
	return _nombre_desde_switch('/project2/switch2', '/project2/vis_knobs_lib')


def nombre_fx():
	sw = op('/project2/switch23')
	if sw is None or len(sw.inputs) == 0: return '-'
	k = int(sw.par.index.eval())
	if k == 0: return 'sin FX'
	return _nombre_desde_switch('/project2/switch23', '/project2/fx_knobs_lib')


def nombre_escena():
	esc = op('/project2/base17/escena_modular')
	if esc is None: return '-'
	try:
		mp = esc.par.Modoescena
		return mp.menuLabels[mp.menuIndex] if mp.menuIndex is not None else '-'
	except Exception:
		return '-'
'''
lib_dat = R.op('midi_monitor_lib') or R.create(textDAT, 'midi_monitor_lib')
lib_dat.text = LIB_PY
lib_dat.nodeX, lib_dat.nodeY = R.op('vis_knobs_lib').nodeX + 200, R.op('vis_knobs_lib').nodeY if R.op('vis_knobs_lib') else (0, 0)
print('[ok] midi_monitor_lib')

# ---- Quitar Sepmidi/Ultimomidi si quedo en "Correccion de color" ----
for pg in list(SHOW.customPages):
    if pg.name == 'Correccion de color':
        for p in list(pg.pars):
            if p.name in ('Sepmidi', 'Ultimomidi'):
                n = p.name
                p.destroy()
                print('[ok] movido %s fuera de "Correccion de color"' % n)

# ---- Crear pagina MIDI con los pars ----
pg = next((p for p in SHOW.customPages if p.name == 'MIDI'), None) or SHOW.appendCustomPage('MIDI')


def _upsert_str(name, label, default=''):
    p = SHOW.par[name] if hasattr(SHOW.par, name) else None
    if p is None:
        p = pg.appendStr(name, label=label)[0]
        p.default = default
        p.val = default
    return p


def _upsert_int_expr(name, label, expr):
    p = SHOW.par[name] if hasattr(SHOW.par, name) else None
    if p is None:
        p = pg.appendInt(name, label=label)[0]
    p.readOnly = True
    p.expr = expr
    p.mode = ParMode.EXPRESSION
    return p


def _upsert_str_expr(name, label, expr):
    p = SHOW.par[name] if hasattr(SHOW.par, name) else None
    if p is None:
        p = pg.appendStr(name, label=label)[0]
    p.readOnly = True
    p.expr = expr
    p.mode = ParMode.EXPRESSION
    return p


def _upsert_pulse(name, label):
    p = SHOW.par[name] if hasattr(SHOW.par, name) else None
    if p is None:
        p = pg.appendPulse(name, label=label)[0]
    return p


_upsert_str('Ultimomidi', 'Ultimo MIDI movido')
_upsert_int_expr('Canalbeatstep', 'Canal Beatstep', "int(op('/project2/bs_canal')['canal'])")
_upsert_int_expr('Padbeatstep', 'Pad activo', "int(op('/project2/bs_canal')['pad'])")
_upsert_str_expr('Visualalaire', 'Visual al aire', "op('/project2/midi_monitor_lib').module.nombre_visual()")
# Solo agregar FX/Escena si existen en el rig
if R.op('switch23') is not None:
    _upsert_str_expr('Fxalaire', 'FX al aire', "op('/project2/midi_monitor_lib').module.nombre_fx()")
if R.op('base17/escena_modular') is not None:
    _upsert_str_expr('Escenaalaire', 'Escena al aire', "op('/project2/midi_monitor_lib').module.nombre_escena()")
_upsert_pulse('Panic', 'PANIC / Reset MIDI')

print('[ok] pagina MIDI con monitores')

# ---- Callback del Panic ----
PANIC_CB = '''# generado por setup_midi_monitor.py
def onPulse(par):
\tif par.name != 'Panic':
\t\treturn
\td = op('/project2/bs_luces')
\tif d is not None:
\t\tfor c in (9, 10, 11):
\t\t\tfor n in range(37, 53):
\t\t\t\td.sendNoteOff(c, n)
\tex = op('/project2/bs_luces_exec')
\tif ex is not None:
\t\tex.unstore('prendidos')
\top('/project2/switch2').par.index = 0
\tif op('/project2/switch23') is not None:
\t\top('/project2/switch23').par.index = 0
\tprint('[PANIC] MIDI reseteado')
'''
cb = SHOW.op('midi_panic_cb') or SHOW.create(parameterexecuteDAT, 'midi_panic_cb')
cb.nodeX, cb.nodeY = 300, -100
cb.par.op = SHOW.path
cb.par.onpulse = True
cb.par.valuechange = False
cb.par.pars = 'Panic'
cb.text = PANIC_CB
print('[ok] callback PANIC en midi_panic_cb')

# ---- Agregar "MIDI" al pagescope del widget UI ----
hub = R.op('ui_perform/par_show_hub')
if hub is not None:
    scope = hub.par.pagescope.val
    if 'MIDI' not in scope.split():
        hub.par.pagescope = (scope + ' MIDI').strip()
        print('[ok] pagescope actualizado con MIDI')

print('\n[OK] pestana MIDI lista')
