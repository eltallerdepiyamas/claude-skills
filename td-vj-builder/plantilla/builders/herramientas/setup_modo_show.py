# ─────────────────────────────────────────────────────────────
# setup_modo_show.py — MODO SHOW (candado) · hub /project2/show, pestaña "Candado"
#
#   Modoshow        "Modo SHOW (candado)": bloquea lo peligroso para que un clic equivocado no tumbe el show:
#                   resolucion (W/H), fuente de audio y el DEMO (y, si el show las tiene, Dispositivos,
#                   Pantallas y lo de camaras). Ademas la UI ignora ACTUALIZAR THUMBS (congela ~3 s)
#                   y el Stream Deck ignora thumbs y demo.
#                   Traido de LJ Metropolitan (2026-11-15): lo que no existe en un show se salta solo.
#   Candadoajustes  "Tambien los ajustes del soundcheck": con el candado puesto, bloquea ademas lo que se deja
#                   fijo en el soundcheck: en CADA escena todo lo de la pagina Layout que no sea sus 5 sliders
#                   (extras como Huelinea, Marco, Doble, Entrada, Suave, Hue, Altura; Bgcolor y Color1-5),
#                   los toggles de LUT por camara y los nombres de las camaras.
#   Siguen libres SIEMPRE: los 5 sliders de cada escena, Bypass, Split abierto, Paleta Audio, la pestaña Audio
#   de cada escena, elegir escena / camara / lugares, correccion de color, Gain y Reaccion global, REC de ensayo.
#
# Bloquear = par.enable False (se ve gris y no se puede mover con el mouse). Al quitar el candado se vuelven a
# habilitar SOLO los que el candado apago (lista guardada en show.store('candado_pars')).
# El boton MODO SHOW de la barra superior de la UI (setup_ui.py) mueve show.Modoshow.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_modo_show.py', encoding='utf-8').read())
# Idempotente. QUITAR = True lo desmonta (y deja todo desbloqueado).
# ─────────────────────────────────────────────────────────────
QUITAR = False

LIB = r'''# modoshow_lib — candado del MODO SHOW (lo escribe builders/herramientas/setup_modo_show.py; no editar aqui)
SHOW = '/project2/show'
ESC = '/project2/base17/escena_modular'

# (operador, nombres o paginas) que se bloquean siempre con el candado
# El LUT NO se bloquea (pedido 2026-11-12: llegan mas LUTs y se cambian / dosifican en vivo)
PELIGROSO_SHOW = ['W', 'H', 'Audiofuente', 'Audioarchivo', 'Audiodriver', 'Audiodevice']
PELIGROSO_SHOW_PAGINAS = ['Dispositivos', 'Pantallas']
PELIGROSO_ESC = ['W', 'H', 'Vivoprendido', 'Demo', 'Democada', 'Demograbar', 'Demounavez', 'Demotexto', 'Demofam',
                 'Recsel', 'Recfuente', 'Recaudio', 'Recaudiochop']
# lo que se deja fijo en el soundcheck
AJUSTES_SHOW = []
AJUSTES_ESC = ['Nombre1', 'Nombre2', 'Nombre3', 'Nombre4', 'Nombre5', 'Nombre6', 'Camfit']
LIBRES_ESCENA = ('Bypass', 'Abierto', 'Paletaaudio')


def _pars(o, nombres=(), paginas=()):
    out = []
    if o is None:
        return out
    for n in nombres:
        p = getattr(o.par, n, None)
        if p is not None:
            out += list(p.tuplet)
    for g in o.customPages:
        if g.name in paginas:
            out += list(g.pars)
    return out


def _ajustes_escena(c):
    """Pagina Layout de una escena menos sus 5 sliders de rol, Bypass, Split abierto y Paleta Audio."""
    pg = next((g for g in c.customPages if g.name == 'Layout'), None)
    if pg is None:
        return []
    cinco = [p.name for p in pg.pars if (p.isFloat or p.isInt) and p.style not in ('RGB', 'RGBA')][:5]
    return [p for p in pg.pars if p.name not in cinco and p.name not in LIBRES_ESCENA
            and p.mode == type(p.mode).CONSTANT]


def lista(ajustes):
    s, e = op(SHOW), op(ESC)
    ps = _pars(s, PELIGROSO_SHOW, PELIGROSO_SHOW_PAGINAS) + _pars(e, PELIGROSO_ESC)
    if ajustes:
        ps += _pars(s, AJUSTES_SHOW) + _pars(e, AJUSTES_ESC)
        for c in (e.children if e is not None else []):
            if c.isCOMP and c.name.startswith('layout_'):
                ps += _ajustes_escena(c)
    return ps


def aplicar():
    """Deja los parametros como diga el hub: primero suelta lo que el candado tenia, luego bloquea lo que toque."""
    s = op(SHOW)
    for ruta, nombre in (s.fetch('candado_pars', [], search=False, storeDefault=False) or []):
        o = op(ruta)
        p = getattr(o.par, nombre, None) if o is not None else None
        if p is not None:
            p.enable = True
    hechos = []
    if s.par.Modoshow.eval():
        for p in lista(bool(s.par.Candadoajustes.eval())):
            if p.enable and not p.readOnly:
                p.enable = False
                hechos.append((p.owner.path, p.name))
    s.store('candado_pars', hechos)
    return len(hechos)
'''

EXEC = '''# modoshow_exec — al mover el candado en el hub, bloquea / suelta (modoshow_lib)
def onValueChange(par, prev):
    op('modoshow_lib').module.aplicar()
    return
'''


def run():
    s = op('/project2/show')
    if s is None:
        print('[falla] no encuentro /project2/show')
        return
    viejo = s.op('modoshow_lib')
    if viejo is not None and getattr(s.par, 'Modoshow', None) is not None:
        s.par.Modoshow = False              # suelta todo antes de rehacer
        try:
            viejo.module.aplicar()
        except Exception:
            pass
    for n in ('modoshow_lib', 'modoshow_exec'):
        o = s.op(n)
        if o is not None:
            o.destroy()
    if QUITAR:
        for g in list(s.customPages):
            if g.name == 'Candado':
                g.destroy()
        s.unstore('candado_pars')
        print('[ok] MODO SHOW desmontado')
        return
    pg = next((g for g in s.customPages if g.name == 'Candado'), None) or s.appendCustomPage('Candado')
    if getattr(s.par, 'Modoshow', None) is None:
        pg.appendToggle('Modoshow', label='Modo SHOW (candado)')
    if getattr(s.par, 'Candadoajustes', None) is None:
        pg.appendToggle('Candadoajustes', label='Tambien los ajustes del soundcheck')[0].val = False
    s.par.Modoshow.default = False
    s.par.Candadoajustes.default = False    # de fabrica los extras de las escenas quedan libres (boton aparte en la UI)
    s.par.Modoshow = False                  # nunca arranca con candado
    lib = s.create(textDAT, 'modoshow_lib')
    lib.text = LIB
    lib.nodeX, lib.nodeY = -600, -900
    ex = s.create(parameterexecuteDAT, 'modoshow_exec')
    ex.nodeX, ex.nodeY = -400, -900
    ex.par.op = s.path
    ex.par.pars = 'Modoshow Candadoajustes'
    ex.par.valuechange = True
    ex.text = EXEC
    m = lib.module
    print('[ok] MODO SHOW: candado bloquea %d parametros (%d con los ajustes del soundcheck)'
          % (len(m.lista(False)), len(m.lista(True))))

run()
