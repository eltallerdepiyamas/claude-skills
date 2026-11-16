# setup_piloto.py — instala el PILOTO AUTOMATICO y el VIGIA DE VIDEO (para shows sin operador).
#   show: paginas Piloto y Vigia (los ajustes; la UI los muestra en la pestana PILOTO y el chip AUTO de arriba).
#   /project2/show/piloto: piloto_lib (logica, de builders/herramientas/piloto_lib.py) · piloto_exec (cada cuadro)
#                          · piloto_pulsos (Siguiente) · piloto_perform (FPS/memoria) · vigia_res (salida 64x36)
#   /project2: piloto_b (switch que prepara lo que entra) + piloto_cross (fundido) entre switch2 y level1.
# Idempotente: conserva los valores que ya tengas. armar.py lo corre. Apagado por default (Pilotoauto).
R = op('/project2')
S = R.op('show')


def pagina(n):
    return next((g for g in S.customPages if g.name == n), None) or S.appendCustomPage(n)


def num(pg, n, label, v, lo, hi, entero=False):
    if not hasattr(S.par, n):
        p = (pg.appendInt if entero else pg.appendFloat)(n, label=label)[0]
        p.default = v
        p.val = v
    p = getattr(S.par, n)
    p.normMin, p.normMax = lo, hi
    p.clampMin, p.min = True, lo
    return p


def tog(pg, n, label, v):
    if not hasattr(S.par, n):
        p = pg.appendToggle(n, label=label)[0]
        p.default = v
        p.val = v
    return getattr(S.par, n)


def menu(pg, n, label, nombres, etiquetas, v):
    if not hasattr(S.par, n):
        p = pg.appendMenu(n, label=label)[0]
        p.menuNames, p.menuLabels = nombres, etiquetas
        p.default = v
        p.val = v
    return getattr(S.par, n)


pg = pagina('Piloto')
tog(pg, 'Pilotoauto', 'AUTO (piloto automatico)', False)
if not hasattr(S.par, 'Pilotosiguiente'):
    pg.appendPulse('Pilotosiguiente', label='Siguiente ya')
tog(pg, 'Pilotoquedarse', 'Quedarse aqui', False)
num(pg, 'Pilotoduracion', 'Duracion por visual (s)', 30.0, 5.0, 180.0)
num(pg, 'Pilotovariacion', 'Variacion (±)', 0.25, 0.0, 0.8)
num(pg, 'Pilotominimo', 'Minimo en pantalla (s)', 8.0, 2.0, 60.0)
tog(pg, 'Pilotodrop', 'Cambiar en drop', True)
num(pg, 'Pilotodropsens', 'Sensibilidad del drop', 0.5, 0.0, 1.0)
tog(pg, 'Pilotoenkick', 'Cambiar en kick', True)
menu(pg, 'Pilototransicion', 'Transicion', ['fundido', 'corte'], ['Fundido', 'Corte (en kick)'], 'fundido')
num(pg, 'Pilototransdur', 'Duracion transicion (s)', 1.5, 0.0, 4.0)
tog(pg, 'Pilotoch9', 'CH9 OTROS', True)
num(pg, 'Pilotopeso9', 'Peso CH9', 1.0, 0.0, 3.0)
tog(pg, 'Pilotoch10', 'CH10 CIRCULARES', True)
num(pg, 'Pilotopeso10', 'Peso CH10', 1.0, 0.0, 3.0)
tog(pg, 'Pilotoch11', 'CH11 LOGOS', True)
num(pg, 'Pilotopeso11', 'Peso CH11', 1.0, 0.0, 3.0)
num(pg, 'Pilotologo', 'Logo cada N cambios (0 = libre)', 4, 0, 12, entero=True)
menu(pg, 'Pilotoorden', 'Orden', ['aleatorio', 'secuencia'], ['Aleatorio sin repetir', 'En secuencia'], 'aleatorio')
if not hasattr(S.par, 'Pilotoexcluir'):
    pg.appendStr('Pilotoexcluir', label='Excluir pads (ej. 9-4 10-12)')
tog(pg, 'Pilotoderiva', 'Deriva de sliders', True)
num(pg, 'Pilotoderivarango', 'Rango de deriva (±)', 0.12, 0.0, 0.5)
num(pg, 'Pilotoretomar', 'Retomar tras manual (s)', 20.0, 0.0, 300.0)
num(pg, 'Pilotoregistro', 'Registro de resistencia (min, 0 = no)', 5.0, 0.0, 60.0)
pv = pagina('Vigia')
tog(pv, 'Vigia', 'Vigia de video', True)
num(pv, 'Vigianegro', 'Umbral de negro (pico de brillo)', 0.05, 0.0, 0.3)
num(pv, 'Vigiasat', 'Umbral de saturado (% de pantalla)', 0.6, 0.2, 1.0)
num(pv, 'Vigiatol', 'Tolerancia (s)', 4.0, 1.0, 30.0)

# --- COMP piloto dentro de show
P = S.op('piloto') or S.create(baseCOMP, 'piloto')
P.nodeX, P.nodeY = 400, -600
P.comment = 'piloto automatico + vigia de video · builders/herramientas/setup_piloto.py'
lib = P.op('piloto_lib') or P.create(textDAT, 'piloto_lib')
lib.text = open(project.folder + '/builders/herramientas/piloto_lib.py', encoding='utf-8').read().lstrip('﻿')
lib.nodeX, lib.nodeY = 0, 0
P.unstore('pil')
P.unstore('bancos_cache')
ex = P.op('piloto_exec') or P.create(executeDAT, 'piloto_exec')
ex.nodeX, ex.nodeY = 200, 0
ex.text = '\n'.join(['# cada cuadro: piloto automatico + vigia (piloto_lib)', 'def onFrameStart(frame):',
                     "    op('piloto_lib').module.tick()", '    return', ''])
ex.par.framestart = True
ex.par.active = True
px = P.op('piloto_pulsos') or P.create(parameterexecuteDAT, 'piloto_pulsos')
px.nodeX, px.nodeY = 400, 0
px.par.op = S.path
px.par.pars = 'Pilotosiguiente Pilotoauto'
px.par.onpulse = True
px.par.valuechange = True
px.text = '\n'.join(['def onPulse(par):', "    op('piloto_lib').module.siguiente()", '    return', '',
                     'def onValueChange(par, prev):', "    op('piloto_lib').module.log('AUTO ' + ('ON' if par.eval() else 'OFF'))",
                     '    return', ''])
pf = P.op('piloto_perform') or P.create(performCHOP, 'piloto_perform')
pf.nodeX, pf.nodeY = 0, -150
sel = P.op('vigia_in') or P.create(selectTOP, 'vigia_in')
sel.par.top = '/project2/master_visuales'
sel.nodeX, sel.nodeY = 200, -150
res = P.op('vigia_res') or P.create(resolutionTOP, 'vigia_res')
res.inputConnectors[0].connect(sel)
res.par.outputresolution = 'custom'
res.par.resolutionw, res.par.resolutionh = 64, 36
res.nodeX, res.nodeY = 400, -150

# --- fundido entre switch2 y level1
sw, lv = R.op('switch2'), R.op('level1')
b = R.op('piloto_b')
if b is None:
    b = R.create(switchTOP, 'piloto_b')
    for inp in sw.inputs:
        inp.outputConnectors[0].connect(b)
    b.par.index = sw.par.index.eval()
b.nodeX, b.nodeY = sw.nodeX, sw.nodeY - 200
b.comment = 'piloto: prepara el visual que entra (mismas entradas que switch2)'
cr = R.op('piloto_cross')
if cr is None:
    cr = R.create(crossTOP, 'piloto_cross')
    cr.inputConnectors[0].connect(sw)
    cr.inputConnectors[1].connect(b)
    lv.inputConnectors[0].connect(cr)
    cr.par.cross = 0.0
cr.nodeX, cr.nodeY = sw.nodeX + 600, sw.nodeY - 100
cr.comment = 'piloto: fundido (0 = switch2 al aire)'
falta = len(sw.inputs) - len(b.inputs)
print('[ok] piloto instalado · AUTO', 'ON' if S.par.Pilotoauto.eval() else 'OFF', '· entradas piloto_b %d/%d' % (len(b.inputs), len(sw.inputs)),
      '' if not falta else '[X] faltan entradas en piloto_b: borra piloto_b y vuelve a correr')
