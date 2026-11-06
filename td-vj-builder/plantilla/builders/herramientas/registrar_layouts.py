# ─────────────────────────────────────────────────────────────
# registrar_layouts.py — deja el menú Modoescena y blend_switch iguales a los layouts que existen.
#
# - RETIRAR: layouts que salen del show (se copian a /project2/_respaldo/escena_modular y se quitan).
# - Quita del menú las escenas cuyo layout ya no existe.
# - Ordena el menú con ORDEN, separado por familia: primero MULTIVIEW, luego SINGLE CAM
#   (los que no estén en ORDEN van al final de su familia, en el orden de la red).
# - blend_switch.Numinputs = cantidad de escenas; opción i del menú -> entrada in(i+1).
# Cada setup_layout_*.py ya se registra solo al construirse; esto es para reordenar, retirar o reparar.
#
# Uso (Textport):
#   exec(open(project.folder + '/builders/herramientas/registrar_layouts.py', encoding='utf-8').read())
# ─────────────────────────────────────────────────────────────
import sys, importlib
LIB = project.folder + '/_lib'
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import tdvj_core, escena_registro
importlib.reload(tdvj_core)
importlib.reload(escena_registro)

# salen del show (sus builders están en builders/_descartados)
#   Columnas (las dos) -> reemplazadas por Bloques (multiview) y Formas 1 Cam (single cam)
RETIRAR = ['layout_mv_polaroid', 'layout_mv_persianas', 'layout_rs_corriente', 'layout_rs_columnas', 'layout_mv_columnas', 'layout_sc_columnas']

# orden del menú Modoescena (= orden de las entradas de blend_switch)
ORDEN = [
    # MULTIVIEW
    'layout_mv_multiview', 'layout_rs_playeras', 'layout_mv_formas', 'layout_mv_bloques',
    'layout_rs_luna', 'layout_rs_late_show', 'layout_rs_riff', 'layout_mv_baraja',
    # nuevos (2026-11-05): solidos de color, mascaras y camaras completas en su proporcion
    'layout_mv_marcos', 'layout_mv_escalera', 'layout_mv_aperturas',
    # nuevos (2026-11-04): Persianas rehecha en horizontal · Cine (ref. Frank Ocean) · Baile (ref. Harry Styles)
    'layout_mv_cine', 'layout_mv_baile', 'layout_mv_diagonales',
    # SINGLE CAM
    'layout_rs_camara_unica', 'layout_sc_formas',
]

escena_registro.retirar(RETIRAR)
escena_registro.sincronizar(orden=ORDEN)
