# ─────────────────────────────────────────────────────────────
# setup_orden_pestanas.py — fija el orden de las pestanas custom de /project2/show.
#
# Criterio: izquierda = setup del show (lo tocas 1 vez al llegar, raro durante),
#           derecha = navegas durante el show.
#
# Propuesta de orden (editable abajo):
#   Dispositivos → Resolucion → Audio → LUT → MIDI → Ensayo → Pantallas → Correccion de color
#
# Idempotente: solo reordena, no destruye nada. Las pestañas que no estén en ORDEN
# quedan al final en el mismo orden relativo que tenían.
# (La pestaña "Camaras" del hub NO existe — esos params viven en escena_modular.)
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/setup_orden_pestanas.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────

ORDEN = [
    'Dispositivos',
    'Resolucion',
    'Audio',
    'LUT',
    'MIDI',
    'Ensayo',
    'Pantallas',
    'Correccion de color',
]

show = op('/project2/show')
if show is None:
    raise SystemExit('[err] No existe /project2/show')

existentes = [pg.name for pg in show.customPages]
# primero las que pide ORDEN (si existen), luego las demas en su orden actual
final = [n for n in ORDEN if n in existentes]
sobrantes = [n for n in existentes if n not in final]
final += sobrantes

try:
    show.sortCustomPages(*final)
    print('[ok] orden final:', ' → '.join(final))
except AttributeError:
    # fallback: setear .order de cada page (si esa API existe en esta version)
    for idx, n in enumerate(final):
        pg = next((p for p in show.customPages if p.name == n), None)
        if pg is not None and hasattr(pg, 'order'):
            pg.order = idx
    print('[ok] fallback .order aplicado:', ' → '.join(final))

ignoradas = [n for n in ORDEN if n not in existentes]
if ignoradas:
    print('     pestanas listadas en ORDEN que no existen:', ', '.join(ignoradas))
