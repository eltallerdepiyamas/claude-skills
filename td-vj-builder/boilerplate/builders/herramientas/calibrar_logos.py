# calibrar_logos.py — comprueba el tamano estandar del logo (show.Logotamano) en CH11.
# Los visuales GLSL usan un factor K calculado de su shader (logo_tamano.py). Medir la salida final engana: los
# anillos, halos y estelas llegan mas lejos que el sello. Por eso aqui se mide el LOGO SOLO donde se puede:
# en las redes pal_norte (el transform que escala el logo antes del efecto) y, en los GLSL, solo como referencia.
import ast
import numpy as np
R = op('/project2')
S = R.op('show')
src = open(project.folder + '/builders/herramientas/ui_bancos.py', encoding='utf-8').read()
B = next(ast.literal_eval(n.value) for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'BANCOS')
lib = op('/project2/show/revisar_visuales_lib')
objetivo = S.par.Logotamano.eval()


def medir(top):
    a = top.numpyArray(delayed=False)
    lum = a[:, :, :3].max(axis=2) * (a[:, :, 3] if a.shape[2] > 3 else 1)
    h, w = lum.shape
    banda = lum[:, w // 2 - int(0.06 * h): w // 2 + int(0.06 * h)]
    tope = np.percentile(banda, 99.5)
    if tope < 0.02:
        return None
    filas = np.where((banda > 0.25 * tope).mean(axis=1) > 0.04)[0]
    return (filas.max() - filas.min()) / float(h) if len(filas) > 1 else None


for nombre, k, _ in B[11]:
    b = lib.module.base_de(k)
    trim = b.par.Tamano.eval() if hasattr(b.par, 'Tamano') else 1.0
    solo = b.op('logo_escala') or (b.op('red/logo_tamano') if b.op('red') else None)
    m = medir(solo) if solo is not None else None
    f = medir(b.op('out1'))
    print('%-18s %-7s ajuste %.2f | quiere %.2f | logo solo %s | salida completa %s' % (
        nombre, b.name, trim, objetivo * trim, '%.2f' % m if m else '-', '%.2f' % f if f else '-'))
