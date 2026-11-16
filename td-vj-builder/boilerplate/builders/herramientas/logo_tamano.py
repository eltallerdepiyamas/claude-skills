# logo_tamano.py — TAMANO DE LOGO ESTANDAR para todos los visuales de CH11 (los que usan el sello).
#   show.Logotamano (pagina Logo) = alto del PNG del sello / alto de pantalla. Igual en TODOS los visuales de logo.
#   base.Tamano = ajuste fino por visual (1.0 = estandar). Excepcion, no regla.
# Cada visual traduce a su propia escala con un factor K (medido en su shader), asi 0.75 es 0.75 real en todos.
# Idempotente. Correr despues de build_all.py (armar.py lo corre). Respaldo de los Tamano de antes en control/.
import ast, json, os, re
R = op('/project2')
S = R.op('show')
EXPR = "op('/project2/show').par.Logotamano * parent().par.Tamano * %s"
# factor por shader: cuanto hay que multiplicar el tamano estandar para que el sello mida lo mismo
K = {'murcielago_particulas': 1.0, 'sello_giratorio': 1.0, 'onda_circular': 1.0, 'halftone_circular': 1.0,
     'eclipse_feedback': 1.0, 'moneda_glitch': 1.0,
     'tunel_circular': 1.0 / 0.75,      # el shader lo divide entre (0.75 + 0.3 * energia)
     'sello_particulas': 0.5,           # su sello() usa 2 * tam
     'sello_metalico': 1.0, 'sello_prism': 1.0, 'logo_slice': 1.0, 'sello_concentrico': 1.0, 'sello_flare': 1.0,
     # CH12 (2026-11-16): todos dibujan el sello con c / u_tamano
     'anillos_lzx': 1.0, 'rutt_etra_sello': 1.0, 'datamosh_sello': 1.0, 'edge_feedback_sello': 1.0, 'bloom_sello': 1.0,
     'sello_reaccion': 1.0, 'sello_keyer': 1.0, 'sello_voronoi': 1.0}

# 1. parametro global
pg = next((p for p in S.customPages if p.name == 'Logo'), None) or S.appendCustomPage('Logo')
if not hasattr(S.par, 'Logotamano'):
    p = pg.appendFloat('Logotamano', label='Tamano logo')[0]
    p.default = 0.75
    p.val = 0.75
p = S.par.Logotamano
p.normMin, p.normMax, p.clampMin, p.min = 0.2, 1.5, True, 0.05

src = open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read()
B = next(ast.literal_eval(n.value) for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'BANCOS')


def base_de(k):
    sw = R.op('switch2')
    o = sw.inputs[k] if k < len(sw.inputs) else None
    for _ in range(4):
        if o is None:
            return None
        if o.parent() != R:
            return o.parent()
        if re.match(r'base\d+$', o.name):
            return o
        nul = next((i for i in o.inputs if i.OPType == 'nullTOP'), None) if o.OPType == 'switchTOP' else None
        o = nul if nul is not None else (o.inputs[0] if o.inputs else None)
    return None


def ajuste(b):
    """par Tamano de la base = ajuste fino (1.0). Guarda el valor viejo la primera vez."""
    if not hasattr(b.par, 'Tamano'):
        pag = next((q for q in b.customPages if q.name == 'Visual'), None) or b.appendCustomPage('Visual')
        pag.appendFloat('Tamano', label='Tamano (ajuste)')
        b.par.Tamano.default = 1.0
        b.par.Tamano.val = 1.0
    t = b.par.Tamano
    if t.label != 'Tamano (ajuste)':
        viejos[b.name] = t.eval()
        t.label = 'Tamano (ajuste)'
        t.default = 1.0
        t.val = 1.0
    t.normMin, t.normMax = 0.5, 1.5
    t.clampMin, t.clampMax, t.min, t.max = True, True, 0.3, 2.0   # habia rangos viejos (0.2-0.55) que lo recortaban
    if not viejos.get('_ajuste_ok_' + b.name):
        t.val = 1.0
        viejos['_ajuste_ok_' + b.name] = True


def uniforme(g, nombre, expr):
    libre = None
    for j in range(40):
        nm = getattr(g.par, 'uniname%d' % j, None)
        if nm is None:
            break
        if nm.eval() == nombre:
            getattr(g.par, 'value%dx' % j).expr = expr
            return
        if not nm.eval() and libre is None:
            libre = j
    getattr(g.par, 'uniname%d' % libre).val = nombre
    getattr(g.par, 'value%dx' % libre).expr = expr


CAL = project.folder + '/control/logo_calibracion.json'   # factor medido por calibrar_logos.py (base -> K)
cal = json.load(open(CAL, encoding='utf-8')) if os.path.exists(CAL) else {}
F = project.folder + '/control/logo_tamano_respaldo.json'
viejos = json.load(open(F, encoding='utf-8')) if os.path.exists(F) else {}
hechos, faltan = [], []
for nombre, k, _ in [x for c in sorted(B) if c in (11, 12) for x in B[c] if x]:   # canales de LOGOS
    b = base_de(k)
    if b is None:
        faltan.append(nombre)
        continue
    g = b.op('glsl1')
    arch = ''
    if g is not None and g.OPType == 'glslTOP' and g.par.pixeldat.eval():
        d = op(g.par.pixeldat.eval())
        arch = os.path.splitext(d.par.file.eval().split('/')[-1])[0] if d is not None and 'file' in [q.name for q in d.pars()] else ''
    if arch in K:
        ajuste(b)
        uniforme(g, 'u_tamano', EXPR % repr(round(K[arch] * cal.get(b.name, 1.0), 6)))
        hechos.append('%s (%s, K=%.3g)' % (nombre, b.name, K[arch]))
        continue
    # redes pal_norte: el logo entra por un fit a pantalla completa (alto = 1); se escala con un transform
    red = b.op('red')
    esc = b.op('logo_escala')                      # base2 ya lo trae afuera de la red
    if esc is None and red is not None and red.op('logo') is not None:
        fit = red.op('logo')
        esc = red.op('logo_tamano')
        if esc is None:
            esc = red.create(transformTOP, 'logo_tamano')
            esc.nodeX, esc.nodeY = fit.nodeX + 150, fit.nodeY - 120
            for c in list(fit.outputConnectors[0].connections):
                c.connect(esc)                      # lo que salia del fit ahora sale del transform
            esc.inputConnectors[0].connect(fit)
        esc.par.extend = 'zero'
    if esc is None:
        faltan.append('%s (%s: no encontre por donde entra el logo)' % (nombre, b.name))
        continue
    ajuste(b)
    expr = "op('/project2/show').par.Logotamano * op('%s').par.Tamano * %s" % (b.path, repr(cal.get(b.name, 1.0)))
    esc.par.sx.expr = expr
    esc.par.sy.expr = expr
    hechos.append('%s (%s, transform %s)' % (nombre, b.name, esc.name))
json.dump(viejos, open(F, 'w', encoding='utf-8'), indent=1)
print('Logotamano =', S.par.Logotamano.eval(), '|', len(hechos), 'visuales:', hechos)
print('faltan:', faltan or 'ninguno')
