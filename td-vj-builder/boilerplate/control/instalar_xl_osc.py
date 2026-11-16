# instalar_xl_osc.py — correr UNA vez en TouchDesigner (Textport, MCP correr_script o un Text DAT -> Run).
# Generico: si el show no tiene camaras / titulos / setlist, esos comandos no hacen nada; siempre sirven
# dial/reset de las perillas, blackout, modoshow y reaccion.
# Le da al Stream Deck XL (control/streamdeck_xl.companionconfig) los botones que el de 15 no tenia:
#
#   1. Agrega al DAT de callbacks de oscin1 las direcciones nuevas (/td/xl/...), SOLO SUMA:
#        /td/xl/blackout         = el BLACKOUT de la UI (fundido 0.8 s, ida y vuelta)
#        /td/xl/camfull          = 1 CAMARA FULL de la UI (layout_sc_limpio)
#        /td/xl/tituloaire       = alterna show.Tituloaire (AL AIRE)
#        /td/xl/titulo <clave>   = prepara: cancion · creditos · t1..tN · c1..cN
#        /td/xl/cancion <+1|-1>  = setlist siguiente / anterior
#        /td/xl/ircancion <n>    = setlist: ir a la cancion n
#        /td/xl/modoshow         = pone / quita el candado (MODO SHOW)
#      Van ANTES del filtro del candado: con MODO SHOW puesto siguen funcionando (como en la UI).
#      Nada de lo que ya existe cambia: el Stream Deck de 15 sigue igual.
#   2. Crea /project2/show/xl_feedback (Parameter Execute) que manda a Companion el estado de
#      BLACKOUT, titulo al aire / preparado, cancion actual / siguiente y candado (variables custom).
#
# APPLY = False (de fabrica): solo imprime lo que haria. APPLY = True: lo hace, con respaldo del callbacks
# en control/oscin1_callbacks_antes_xl.py. QUITAR = True: regresa el callbacks al respaldo y borra xl_feedback.
# Se puede correr varias veces (si ya esta instalado no lo duplica; xl_feedback se actualiza siempre).
import os, re

APPLY = False
QUITAR = False

ESC = '/project2/base17/escena_modular'
SHOW = '/project2/show'
MARCA = '# --- XL (control/instalar_xl_osc.py) ---'
CTRL = os.path.join(project.folder, 'control')
RESPALDO = os.path.join(CTRL, 'oscin1_callbacks_antes_xl.py')

XL_FUNC = '''

''' + MARCA + '''
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
'''

FEEDBACK = '''# xl_feedback — manda al Stream Deck XL (Companion) el estado de BLACKOUT, titulos, setlist y candado.
# Lo instala control/instalar_xl_osc.py. Solo manda lo que cambio. Variables: blackout · tituloaire ·
# tituloclave · tituloprep · cancion · cancionsig · cancionbloque · modoshow.
CO = '/project2/base17/escena_modular/companion_out'

def _corto(t, n=16):
    t = str(t).strip()
    return t if len(t) <= n else t[:n - 1].rstrip() + '.'

def _setlist():
    """[(nombre, bloque)] de control/setlist.txt (mismas reglas que el setlist del hub)."""
    import os
    ruta = os.path.join(project.folder, 'control', 'setlist.txt')
    out = []
    try:
        with open(ruta, encoding='utf-8-sig') as f:
            for l in f:
                l = l.strip()
                if l and not l.startswith('#'):
                    nombre, _, bloque = l.partition('|')
                    out.append((nombre.strip(), bloque.strip().lower()))
    except Exception:
        pass
    return out

def _total():
    try:
        return int(op('/project2/show/setlist_lib').module.total())
    except Exception:
        return len(_setlist())

def _bloque(n):
    sl = _setlist()
    return sl[n - 1][1] if 1 <= n <= len(sl) else ''

def _estado():
    s = op('/project2/show')
    d = {}
    for k, f in (('blackout', lambda: 'ON' if s.par.Master.eval() < 0.5 else ''),
                 ('tituloaire', lambda: 'ON' if s.par.Tituloaire.eval() else ''),
                 ('tituloclave', lambda: s.par.Titulo.eval()),
                 ('tituloprep', lambda: _corto(s.par.Titulo.menuLabels[s.par.Titulo.menuIndex])),
                 ('cancion', lambda: '%d/%d\\n%s' % (s.par.Cancion.eval(), _total(), _corto(s.par.Cancionnombre.eval(), 14))),
                 ('cancionbloque', lambda: _bloque(s.par.Cancion.eval())),
                 ('cancionsig', lambda: _corto(s.par.Cancionsigue.eval())),
                 ('modoshow', lambda: 'ON' if s.par.Modoshow.eval() else ''),
                 ('salidaled', lambda: 'ON' if s.par.Salidaled.eval() else ''),
                 ('pantallas', lambda: 'ON' if s.par.Pantallas.eval() else ''),
                 ('reaccion', lambda: '%d%%' % round(s.par.Reaccion.eval() * 100))):
        try:
            d[k] = f()
        except Exception:
            pass
    return d

def enviar(todo=False):
    co = op(CO)
    yo = op('/project2/show/xl_feedback')
    if co is None or yo is None:
        return
    antes = dict(yo.fetch('xl_antes', {}, search=False))
    for k, v in _estado().items():
        if todo or antes.get(k) != v:
            try:
                co.sendOSC('/custom-variable/%s/value' % k, [v])
            except Exception:
                pass
            antes[k] = v
    yo.store('xl_antes', antes)

def onValueChange(par, prev):
    enviar()
    return

def onPulse(par):
    return
'''

def _callbacks():
    o = op(ESC + '/oscin1')
    if o is None:
        return None
    cb = o.par.callbacks.eval() if hasattr(o.par, 'callbacks') else None
    return cb or o.parent().op('oscin1_callbacks')

def _guardar(path, texto):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(texto)

def _archivo(cb):
    """Archivo fuente del callbacks: el del DAT si tiene, si no control/oscin1_callbacks.py (de ahi lo recarga
    actualizar_companion.py: si no se parcha el archivo, el parche se pierde al actualizar Companion)."""
    p = getattr(cb.par, 'file', None)
    ruta = p.eval() if p is not None else ''
    if not ruta:
        return os.path.join(CTRL, 'oscin1_callbacks.py')
    return ruta if os.path.isabs(ruta) else os.path.join(project.folder, ruta)

def _parchar(txt):
    """Inserta la entrada a _xl justo despues de  if parts[0] != 'td': return  y agrega _xl al final."""
    lineas = txt.split('\n')
    for i, l in enumerate(lineas):
        if l.strip().replace('"', "'") == "if parts[0] != 'td':":
            ind = l[:len(l) - len(l.lstrip())]
            sig = lineas[i + 1]
            uno = sig[:len(sig) - len(sig.lstrip())][len(ind):] or '    '
            nuevo = [ind + "if len(parts) >= 3 and parts[1] == 'xl':   " + MARCA,
                     ind + uno + '_xl(parts[2], args)',
                     ind + uno + 'return']
            return '\n'.join(lineas[:i + 2] + nuevo + lineas[i + 2:]).rstrip('\n') + '\n' + XL_FUNC
    return None

def instalar():
    cb = _callbacks()
    s = op(SHOW)
    if cb is None or s is None:
        print('[falla] no encontre', ESC + '/oscin1', 'o', SHOW)
        return
    txt = cb.text.lstrip('\ufeff')
    m = re.search(re.escape(MARCA) + r'\r?\ndef _xl', txt)
    if m is not None:
        # ya instalado: solo refresca el bloque _xl del final (por si se agregaron comandos, p. ej. perillas)
        nuevo = txt[:m.start()].rstrip() + XL_FUNC
        if nuevo.replace('\r', '') == txt.replace('\r', ''):
            print('[ok] el callbacks ya tiene las direcciones /td/xl/ al dia')
        else:
            print('[plan] callbacks', cb.path, ': actualizar el bloque _xl')
            if APPLY:
                cb.text = nuevo
                f = _archivo(cb)
                if f:
                    _guardar(f, nuevo)
    else:
        nuevo = _parchar(txt)
        if nuevo is None:
            print("[falla] no encontre  if parts[0] != 'td':  en", cb.path, '- no toque nada')
            return
        print('[plan] callbacks', cb.path, ': +', nuevo.count('\n') - txt.count('\n'), 'renglones (/td/xl/...)')
        if APPLY:
            _guardar(RESPALDO, txt)
            cb.text = nuevo
            f = _archivo(cb)
            if f:
                _guardar(f, nuevo)
            print('[ok] respaldo en', RESPALDO)
    fb = s.op('xl_feedback')
    print('[plan] ' + ('actualizar' if fb else 'crear') + ' ' + SHOW + '/xl_feedback (Parameter Execute)')
    if not APPLY:
        print('APPLY = False: no cambie nada. Pon APPLY = True y vuelve a correrlo.')
        return
    if fb is None:
        fb = s.create(parameterexecuteDAT, 'xl_feedback')
        fb.nodeX, fb.nodeY = -400, -900
        fb.tags.add('tdvj_xl')
    fb.text = FEEDBACK
    for nombre, valor in (('op', SHOW), ('pars', 'Master Tituloaire Titulo Cancion Modoshow Salidaled Pantallas Reaccion'),
                          ('valuechange', True), ('onpulse', False), ('active', True)):
        p = getattr(fb.par, nombre, None)
        if p is not None:
            p.val = valor
    try:
        fb.module.enviar(True)
    except Exception as e:
        print('[aviso] no pude mandar el estado a Companion todavia:', e)
    # marca para setup_mix_feedback: con el XL no se "presiona" la tecla 1/1/0 (en el XL es un pad)
    s.store('streamdeck_xl', True)
    print('[ok] Stream Deck XL listo del lado de TD')

def quitar():
    cb = _callbacks()
    s = op(SHOW)
    if cb is not None and MARCA in cb.text:
        if not os.path.exists(RESPALDO):
            print('[falla] no hay respaldo en', RESPALDO, '- no toque el callbacks')
        else:
            print('[plan] regresar', cb.path, 'al respaldo')
            if APPLY:
                with open(RESPALDO, encoding='utf-8') as f:
                    viejo = f.read()
                cb.text = viejo
                ruta = _archivo(cb)
                if ruta:
                    _guardar(ruta, viejo)
    fb = s.op('xl_feedback') if s is not None else None
    if fb is not None:
        print('[plan] borrar', fb.path)
        if APPLY:
            fb.destroy()
    if APPLY and s is not None:
        s.unstore('streamdeck_xl')
    print('[ok] quitado' if APPLY else 'APPLY = False: no cambie nada.')

quitar() if QUITAR else instalar()
