# recuadros_project2.py — recuadros de titulo (annotateCOMP 'zona_*') alrededor de cada grupo de /project2.
# NO mueve nodos: solo dibuja el recuadro ajustado a donde ya estan. Correrlo SIEMPRE despues de acomodar
# (acomodar_pads.py lo llama al final). Reporta nodos sin grupo, intrusos dentro de un recuadro y recuadros encimados.
import re
R = op('/project2')
M = 30          # margen alrededor de los nodos
TITULO = 50     # espacio para el titulo arriba
PAD = r'(constant|logic|chopexec)(\d+|_pad50)'
# (nombre, titulo, color, regex de nombres). El orden importa: el primero que atrapa un nodo se lo queda.
GRUPOS = [
    ('zona_midi_entrada', 'MIDI ENTRADA (Beatstep / canales)', (0.35, 0.45, 0.9), r'midi_midiin\d+|bs_canal\w*'),
    ('zona_midi_tabla', 'MIDI (tabla de notas)', (0.35, 0.45, 0.9), r'MIDI'),
    ('zona_monitor_bases', 'MONITOR DE BASES', (0.6, 0.6, 0.6), r'constant34'),
    ('zona_carpeta', 'CARPETA DE VIDEO / PLAY', (0.6, 0.6, 0.6), r'folder\d+\w*|play'),
    ('zona_tablas', 'TABLAS DE PADS Y NOMBRES', (0.9, 0.75, 0.3), r'table1|pad_lib|vis_nombres_tabla'),
    ('zona_knobs', 'KNOBS (visual y fx) · MONITOR MIDI', (0.9, 0.55, 0.25), r'(vis|fx)_knobs_\w+|midi_monitor_lib'),
    ('zona_reset_midi', 'RESET MIDI', (0.9, 0.55, 0.25), r'reset_midi_\w+'),
    ('zona_control_p1', 'CONTROL /project1', (0.9, 0.55, 0.25), r'control_p1'),
    ('zona_audio', 'AUDIO (analisis -> master_audio)', (0.75, 0.4, 0.85), r'audio'),
    ('zona_hub', 'HUB show · UI · MCP', (0.75, 0.4, 0.85), r'show|ui_perform|td_mcp|_respaldo'),
    ('zona_audio_io', 'AUDIO ARCHIVO / SALIDA', (0.75, 0.4, 0.85), r'audiofilein\d+|audiodevout\d+'),
    ('zona_visuales', 'VISUALES · una fila por base (pad a la izquierda)', (0.3, 0.8, 0.45),
     r'base\d+|null\d+|vid\d+|switch([3-9]|1\d|2[01])|' + PAD),
    ('zona_salida', 'SALIDA · switch2 (+ fundido del piloto) -> master_visuales', (0.95, 0.3, 0.3), r'switch2|piloto_\w+|level\d+|out\d+|master_\w+'),
]

for a in [o for o in R.children if o.OPType == 'annotateCOMP' and (o.name.startswith('zona_') or re.match(r'annotate\d+$', o.name))]:
    a.destroy()

nodos = [o for o in R.children if o.OPType != 'annotateCOMP']
dueno = {}
for o in nodos:
    for g in GRUPOS:
        if re.fullmatch(g[3], o.name):
            dueno[o.path] = g[0]
            break
cajas = {}
for nombre, titulo, color, _ in GRUPOS:
    miembros = [o for o in nodos if dueno.get(o.path) == nombre]
    if not miembros:
        continue
    x0 = min(o.nodeX for o in miembros) - M
    x1 = max(o.nodeX + o.nodeWidth for o in miembros) + M
    y0 = min(o.nodeY for o in miembros) - M
    y1 = max(o.nodeY + o.nodeHeight for o in miembros) + M + TITULO
    a = R.create(annotateCOMP)
    a.name = nombre               # create() ignora el nombre en los annotate
    a.nodeX, a.nodeY, a.nodeWidth, a.nodeHeight = x0, y0, x1 - x0, y1 - y0
    pn = {q.name for q in a.pars()}
    if 'Titletext' in pn:
        a.par.Titletext = titulo
    if 'Bodytext' in pn:
        a.par.Bodytext = ''
    for k, c in enumerate('rgb'):
        if 'Backcolor' + c in pn:
            getattr(a.par, 'Backcolor' + c).val = color[k] * 0.35
    if 'Backcoloralpha' in pn:
        a.par.Backcoloralpha = 0.22
    cajas[nombre] = (x0, y0, x1, y1)

sin = [o.name for o in nodos if o.path not in dueno]
intrusos = []
for nombre, (x0, y0, x1, y1) in cajas.items():
    for o in nodos:
        if dueno.get(o.path) != nombre and o.nodeX < x1 and o.nodeX + o.nodeWidth > x0 and o.nodeY < y1 and o.nodeY + o.nodeHeight > y0:
            intrusos.append((nombre, o.name))
choques = []
ks = list(cajas)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        a, b = cajas[ks[i]], cajas[ks[j]]
        if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]:
            choques.append((ks[i], ks[j]))
print('recuadros:', len(cajas), '| sin grupo:', sin, '| intrusos:', intrusos, '| recuadros encimados:', choques)
