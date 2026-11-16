# ─────────────────────────────────────────────────────────────
# setup_midi_devices.py — fuerza el orden del MIDI Device Mapper por NOMBRE del device,
# para que midi_midiin1 SIEMPRE lea del MIDI Mix y midi_midiin2 SIEMPRE del Arturia BeatStep,
# sin importar en qué orden TD los detectó al conectarse.
#
# Hace dos cosas:
#   1. Ahora mismo: busca en la tabla de devices detectados, encuentra MIDI Mix y BeatStep por
#      nombre, y setea los pars .id de midi_midiin1..3 al ID real del device deseado.
#   2. Instala en /project2 un executeDAT 'midi_devices_sync' con onStart() que repite el proceso
#      cada vez que se abre el .toe, para que el orden sea permanente.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_midi_devices.py', encoding='utf-8').read())
#
# Si una vez abierto el proyecto no detecta el MIDI Mix, abre el MIDI Device Mapper (Dialogs > MIDI
# Device Mapper), verifica que el device esté listado (puede necesitar desconectar/reconectar el USB)
# y vuelve a correr este script.
# ─────────────────────────────────────────────────────────────

# orden deseado: (nombre a buscar, substrings alternativos) -> midi_midiinN
ORDEN = [
    (1, ['MIDI Mix', 'MIDIMix', 'MIDI_Mix', 'MIDIMIX']),       # midi_midiin1
    (2, ['BeatStep Pro', 'Arturia BeatStep Pro', 'BeatStep']), # midi_midiin2
]

TAG = 'tdvj_midi_devices'


def _buscar_id(devtable, substrings):
    """Devuelve el ID del Device Mapper que empareje con alguno de los substrings (case-insensitive).
    Si no encuentra, devuelve None."""
    if devtable is None:
        return None
    # cabecera: buscar la columna que contenga el nombre del in-device
    hdr = [str(c) for c in devtable.row(0)]
    id_col = 0  # por convencion la primera columna es el ID
    name_cols = [i for i, h in enumerate(hdr) if 'name' in h.lower() or 'in' in h.lower()]
    if not name_cols:
        # fallback: considerar TODAS las columnas excepto ID
        name_cols = list(range(1, devtable.numCols))
    for r in range(1, devtable.numRows):
        for c in name_cols:
            val = str(devtable[r, c].val) if devtable[r, c] else ''
            for s in substrings:
                if s.lower() in val.lower():
                    try:
                        return int(devtable[r, id_col].val)
                    except Exception:
                        return devtable[r, id_col].val
    return None


def sync_devices():
    """Sincroniza midi_midiinN.par.id con el ID real de cada device buscado por nombre."""
    p2 = op('/project2')
    if p2 is None:
        print('[midi_devices] no existe /project2')
        return
    # cualquier midi_midiin sirve para leer la tabla de devices
    probe = p2.op('midi_midiin1') or p2.op('midi_midiin2') or p2.op('midi_midiin3')
    if probe is None:
        print('[midi_devices] no hay ningun midi_midiinN en /project2')
        return
    devtable = probe.par.device.eval()
    if devtable is None or not hasattr(devtable, 'numRows'):
        # si el par es un path str, intentar resolver
        devtable = op(probe.par.device.val)
    if devtable is None:
        print('[midi_devices] no se pudo resolver la tabla de devices')
        return

    print('[midi_devices] devices detectados:')
    for r in range(devtable.numRows):
        print('   ', ' | '.join(str(devtable[r, c].val if devtable[r, c] else '') for c in range(devtable.numCols)))

    for n, nombres in ORDEN:
        node = p2.op('midi_midiin%d' % n)
        if node is None:
            print('[midi_devices] no existe midi_midiin%d; salto' % n)
            continue
        found = _buscar_id(devtable, nombres)
        if found is None:
            print('[midi_devices] NO ENCONTRADO midi_midiin%d -> %s (conecta el USB y re-corre)' % (n, nombres[0]))
            continue
        current = node.par.id.val
        if str(current) == str(found):
            print('[midi_devices] ok   midi_midiin%d = %s (ID %s)' % (n, nombres[0], found))
        else:
            node.par.id = str(found)
            print('[midi_devices] fix  midi_midiin%d = %s (ID %s, antes era %s)' % (n, nombres[0], found, current))


# ---- 1. correr ahora ----
sync_devices()

# ---- 2. instalar executeDAT que lo re-ejecute al abrir el .toe ----
p2 = op('/project2')
ex = p2.op('midi_devices_sync') or p2.create(executeDAT, 'midi_devices_sync')
ex.tags.add(TAG)
ex.nodeX, ex.nodeY = -1200, 400
ex.par.start = True        # onStart al abrir el proyecto
ex.par.create = False
ex.par.exit = False
ex.par.framestart = False
ex.par.frameend = False
ex.par.playstatechange = False
ex.par.devicechange = True  # tambien al conectar/desconectar un MIDI device
ex.par.projectpresave = False
ex.par.projectpostsave = False
ex.text = '''# auto-generado por builders/herramientas/setup_midi_devices.py
# vuelve a sincronizar midi_midiin1 = MIDI Mix / midi_midiin2 = BeatStep al abrir el .toe
# o cuando TD detecta un cambio en los dispositivos MIDI (USB reconectado).

def _run():
    import sys
    lib = project.folder + '/builders/herramientas'
    if lib not in sys.path:
        sys.path.insert(0, lib)
    # ejecutar el script entero (incluye sync + reinstala, pero reinstalar es no-op si ya existe)
    exec(open(project.folder + '/builders/herramientas/setup_midi_devices.py', encoding='utf-8').read())

def onStart():
    _run()

def onDeviceChange():
    _run()

def onCreate(): return
def onExit(): return
def onFrameStart(frame): return
def onFrameEnd(frame): return
def onPlayStateChange(state): return
def onProjectPreSave(): return
def onProjectPostSave(): return
'''

print('[OK] midi_devices_sync instalado en /project2: se repite en cada abrir del .toe y en cada reconexión de MIDI')
