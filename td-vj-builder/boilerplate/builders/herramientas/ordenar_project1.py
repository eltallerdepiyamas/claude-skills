# ─────────────────────────────────────────────────────────────
# ordenar_project1.py — guarda el acomodo FINAL de /project2 como plantilla y acomoda /project1
# con el mismo esquema (DE ARRIBA A ABAJO, una fila por cadena). SOLO mueve / pinta / recuadros.
#   /project2 -> control/plantilla_project2.json  (el acomodo que Sebas dejo a mano: el de referencia)
#   /project1:
#     1 CONTROL   midiin · select · math/limit/logic/count/... · null · DATs (por tipo, en columnas)
#     2 SALIDA    la cadena de TOPs de select2 (FX de /project2) hasta ndiout1 (NDI), izq -> der
#     3 RAMPAS    rampas del lookup (blend_switch2 / blend_switch3)
#     4 AUDIO     archivos / entrada en vivo / audio_fuente / audio_gain / audioAnalysis
#   Respaldo: control/ordenar_project1_respaldo.json · RESTAURAR = True lo regresa.
# ─────────────────────────────────────────────────────────────
import json, os

RESTAURAR = False
P1, P2 = op('/project1'), op('/project2')
CTRL = project.folder + '/control/'
DX, DY, GAP = 200, 130, 400
COL = dict(control=(0.08, 0.72, 0.72), salida=(0.91, 0.45, 0.11), rampas=(0.85, 0.64, 0.0), audio=(0.13, 0.70, 0.35), otros=(0.45, 0.45, 0.45))


def dump(root, path):
    json.dump({o.path: [o.nodeX, o.nodeY, list(o.color)] for o in root.children}, open(path, 'w', encoding='utf-8'), indent=0)


def caja(titulo, x0, y0, x1, y1, rgb):
    a = P1.create(annotateCOMP)
    a.name = 'zona_' + ''.join(ch if ch.isalnum() else '_' for ch in titulo.lower())[:40]
    a.nodeX, a.nodeY = x0 - 80, y1 - 90
    a.nodeWidth, a.nodeHeight = (x1 - x0) + 320, (y0 - y1) + 290
    a.par.Titletext = titulo
    a.par.Backcolorr, a.par.Backcolorg, a.par.Backcolorb = [c * 0.35 for c in rgb]
    a.par.Backcoloralpha = 0.22


def poner_cols(cols, x, y, rgb, titulo):
    """cols = listas de ops; cada lista una columna (de arriba a abajo)."""
    alto = 0
    for i, col in enumerate(cols):
        for j, o in enumerate(col):
            o.nodeX, o.nodeY = x + i * DX, y - j * DY
            o.color = rgb
            hecho.add(o)
        alto = max(alto, len(col))
    x1, y1 = x + (len(cols) - 1) * DX, y - (alto - 1) * DY
    caja(titulo, x, y, x1, y1, rgb)
    return y1


def salida():
    """Cadena de TOPs que termina en ndiout1: profundidad = distancia a la salida (columna)."""
    fin = P1.op('ndiout1') or next((o for o in P1.children if o.OPType == 'ndioutTOP'), None)
    if fin is None:
        return []
    prof, cola = {fin: 0}, [fin]
    while cola:
        o = cola.pop(0)
        for i in o.inputs:
            if i.parent() == P1 and i.OPType != 'rampTOP' and i not in prof:
                prof[i] = prof[o] + 1
                cola.append(i)
    # selects sueltos que alimentan la cadena por parametro (select2, select55...)
    n = max(prof.values())
    cols = [[] for _ in range(n + 1)]
    for o, d in prof.items():
        cols[n - d].append(o)
    return [sorted(c, key=lambda o: -o.nodeY) for c in cols]


if RESTAURAR:
    for p, (x, y, c) in json.load(open(CTRL + 'ordenar_project1_respaldo.json', encoding='utf-8')).items():
        if op(p) is not None:
            op(p).nodeX, op(p).nodeY, op(p).color = x, y, tuple(c)
    for a in [o for o in P1.children if o.OPType == 'annotateCOMP' and o.name.startswith('zona_')]:
        a.destroy()
    print('[ok] /project1 restaurado')
else:
    dump(P2, CTRL + 'plantilla_project2.json')
    dump(P1, CTRL + 'ordenar_project1_respaldo.json')
    for a in [o for o in P1.children if o.OPType == 'annotateCOMP' and o.name.startswith('zona_')]:
        a.destroy()
    hecho = set()
    y = 0
    # 2 SALIDA primero (para saber que TOPs son de la cadena), se dibuja debajo del control
    sal = salida()
    for c in sal:
        hecho.update(c)
    # 1 CONTROL: CHOPs / DATs que no son audio, por tipo en columnas
    audio_t = ('audiofileinCHOP', 'audiodeviceinCHOP', 'audiodeviceoutCHOP')
    audio_n = ('audio_', 'Little_Jesus', 'switch6', 'audioAnalysis', 'null4')
    es_audio = lambda o: o.OPType in audio_t or o.name.startswith(audio_n)
    tipos = ['midiinCHOP', 'keyboardinCHOP', 'selectCHOP', 'mathCHOP', 'limitCHOP', 'logicCHOP', 'countCHOP',
             'triggerCHOP', 'lfoCHOP', 'switchCHOP', 'mergeCHOP', 'renameCHOP', 'expressionCHOP', 'constantCHOP',
             'nullCHOP', 'oscoutCHOP', 'tableDAT', 'textDAT']
    ctrl = [o for o in P1.children if (o.isCHOP or o.isDAT) and not es_audio(o) and o not in hecho]
    cols = []
    for t in tipos + sorted(set(o.OPType for o in ctrl) - set(tipos)):
        grupo = sorted([o for o in ctrl if o.OPType == t], key=lambda o: o.name)
        for k in range(0, len(grupo), 14):
            cols.append(grupo[k:k + 14])
    yb = poner_cols(cols, 0, y, COL['control'], '1 CONTROL  ·  MIDI (midiin) · selects · math/limit/logic · nulls · tablas  (por tipo)')
    y = yb - DY - GAP
    # 2 SALIDA
    yb = poner_cols(sal, 0, y, COL['salida'], '2 SALIDA  ·  select2 (FX de /project2) -> FX globales -> color_final -> overlays / strobe -> ndiout1 (NDI)')
    y = yb - DY - GAP
    # 3 RAMPAS del lookup
    ramps = sorted([o for o in P1.children if o.OPType == 'rampTOP'], key=lambda o: int(''.join(ch for ch in o.name if ch.isdigit()) or 0))
    if ramps:
        yb = poner_cols([ramps[k:k + 8] for k in range(0, len(ramps), 8)], 0, y, COL['rampas'], '3 RAMPAS  ·  paletas del lookup (blend_switch2 = 1-16 · blend_switch3 = 17-32)')
        y = yb - DY - GAP
    # 4 AUDIO
    au = sorted([o for o in P1.children if es_audio(o) and o not in hecho], key=lambda o: o.nodeX)
    if au:
        yb = poner_cols([au], 0, y, COL['audio'], '4 AUDIO  ·  archivo / en vivo -> audio_fuente -> audio_gain -> switch6 -> audioAnalysis -> null4 (AUDIO_SOURCE)')
        y = yb - DY - GAP
    resto = [o for o in P1.children if o not in hecho and o.OPType != 'annotateCOMP']
    if resto:
        poner_cols([resto[k:k + 6] for k in range(0, len(resto), 6)], 0, y, COL['otros'], '5 OTROS')
    print('[ok] plantilla de /project2 guardada en control/plantilla_project2.json (%d nodos)' % len(P2.children))
    print('[ok] /project1 acomodado: control %d · salida %d · rampas %d · audio %d · otros %d' % (
        sum(len(c) for c in cols), sum(len(c) for c in sal), len(ramps), len(au), len(resto)))
