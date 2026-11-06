"""pal_norte.py: monta una red vieja de Pal Norte (.tox) dentro de una base y recrea lo que usaba afuera."""
from td import op, project, selectCHOP, constantCHOP, constantTOP, baseCOMP, moviefileinTOP, feedbackTOP, fitTOP, transformTOP, countCHOP, renameCHOP, speedCHOP, tableDAT, rampTOP
AUDIO = '/project2/audio/master_audio'


def _chop(b, nombre, canal):
    o = b.op(nombre) or b.create(selectCHOP, nombre)
    o.par.chop = AUDIO
    o.par.channames = canal


def _vacio(b, ruta):
    c = b.op(ruta[0]) or b.create(baseCOMP, ruta[0])
    n = c.op(ruta[1]) or c.create(constantTOP, ruta[1])
    n.par.colorr = n.par.colorg = n.par.colorb = 0
    return n


def montar(n, tox, png=None):
    b = op('/project2/base%d' % n)
    b.allowCooking = True
    r = b.op('red')
    if r is not None:      # no pisar los cambios a mano
        return next(o.path for o in r.children if o.OPType == 'outTOP')
    r = b.loadTox(project.folder + '/assets/tox_pal_norte/%s.tox' % tox)
    r.name = 'red'
    for o in r.findChildren(type=feedbackTOP):      # su Reset leia un teclado que ya no existe
        p = o.par.resetpulse
        if p.mode.name == 'EXPRESSION':
            p.expr = ''
            p.mode = type(p.mode).CONSTANT
    _chop(b, 'select2', 'low')
    _chop(b, 'select3', 'high')
    _chop(b, 'select4', 'mid')
    _chop(b, 'math_low', 'low')
    _chop(b, 'math_mid', 'mid')
    _chop(b, 'math_high', 'high')
    k = b.op('constant2') or b.create(constantCHOP, 'constant2')
    k.par.const0name, k.par.const0value, k.par.const1name, k.par.const1value = 'resX', 1920, 'resY', 1080
    _vacio(b, ('bg_scanlines', 'out1'))
    _vacio(b, ('project1', 'null20'))
    bg = b.op('BG') or b.create(constantTOP, 'BG')
    bg.par.colorr = bg.par.colorg = bg.par.colorb = 0
    bg.par.outputresolution = 'custom'
    bg.par.resolutionw, bg.par.resolutionh = 1920, 1080
    idx = b.op('master_switch') or b.create(constantCHOP, 'master_switch')
    idx.par.const0name, idx.par.const0value = 'index_logo', 0
    _chop(b, 'rename1', 'low')
    _chop(b, 'select1', 'low')
    _chop(b, 'null1', 'low')
    rp = b.op('ramp1') or b.create(rampTOP, 'ramp1')
    rp.par.type = 'circular'
    for m in r.findChildren(type=moviefileinTOP):
        if png:
            m.par.file.mode = type(m.par.file.mode).CONSTANT
            m.par.file = 'assets/' + png
    if png:
        for nom in ('moviefilein3', 'moviefilein4'):
            m = b.op(nom) or b.create(moviefileinTOP, nom)
            m.par.file = 'assets/' + png
    if r.inputConnectors:
        x = b.op('logo_chico') or b.create(fitTOP, 'logo_chico')
        x.inputConnectors[0].connect(b.op('moviefilein3'))
        x.par.outputresolution = 'custom'
        x.par.resolutionw, x.par.resolutionh = 1920, 1080
        x.par.fit = 'fitbest'
        y = b.op('logo_escala') or b.create(transformTOP, 'logo_escala')
        y.inputConnectors[0].connect(x)
        y.par.sx = y.par.sy = 0.5
        y.par.extend = 'zero'
        r.inputConnectors[0].connect(y)
    return next(o.path for o in r.children if o.OPType == 'outTOP')


def montar_generador(n):
    """/project1/project1 de Pal Norte: 13 UberRamp que cambian con el kick. Recrea afuera sus rampas, conteo y velocidad."""
    b = op('/project2/base%d' % n)
    b.allowCooking = True
    r = b.op('red')
    if r is not None:
        return r.path + '/out1'
    r = b.loadTox(project.folder + '/assets/tox_pal_norte/project1.tox')
    r.name = 'red'
    for c in r.children:
        if c.isCOMP and hasattr(c.par, 'enableexternaltox'):
            c.par.enableexternaltox = False
    _chop(b, 'math_low', 'low')
    _chop(b, 'math_mid', 'mid')
    _chop(b, 'math_high', 'high')
    _chop(b, 'kick', 'kick')
    cnt = b.op('count3') or b.create(countCHOP, 'count3')
    cnt.inputConnectors[0].connect(b.op('kick'))
    cnt.par.threshup = 0.5
    idx = b.op('index_data2') or b.create(renameCHOP, 'index_data2')
    idx.inputConnectors[0].connect(cnt)
    idx.par.renamefrom = '*'
    idx.par.renameto = 'cycles_pulse'
    sp = b.op('speed1') or b.create(speedCHOP, 'speed1')
    sp.inputConnectors[0].connect(b.op('math_low'))
    k2 = b.op('constant2') or b.create(constantCHOP, 'constant2')
    k2.par.const0name, k2.par.const0value, k2.par.const1name, k2.par.const1value = 'resX', 1920, 'resY', 1080
    t = b.op('rampas') or b.create(tableDAT, 'rampas')
    t.clear()
    t.appendRow(['pos', 'r', 'g', 'b', 'a'])
    for pos, v in ((0, 0), (0.45, 1), (1, 0)):
        t.appendRow([pos, v, v, v, 1])
    for k, tipo in ((1, 'circular'), (2, 'horizontal'), (3, 'circular'), (4, 'circular'), (5, 'horizontal'), (6, 'circular')):
        m = b.op('ramp%d' % k) or b.create(rampTOP, 'ramp%d' % k)
        m.par.dat = t.path
        m.par.type = tipo
        m.par.phase.expr = "op('speed1')['low'] + absTime.seconds * 0.2"
    return b.path + '/red/out1'
