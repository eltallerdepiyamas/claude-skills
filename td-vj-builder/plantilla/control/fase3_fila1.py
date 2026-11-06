# =============================================================
# fase3_fila1.py  —  fila 1 del MIDImix (knobs 1-5, CC 17 21 25 29 47) = visual activo
#
# Mismo mecanismo que la fila 2 (fase3_fila2.py con LINE = 'vis'):
# - Visual activo = el baseNN que sale por /project2/switch2 (-> switch1 / switch3 -> switch6..21).
# - Cada visual mueve sus 5 del contrato (Mezcla, Tiempo, Distorsion, Color, Firma) o su tabla `knobs`.
# - Takeover proporcional, lag, y vis_knobs_cook para que siga vivo al abrir el .toe.
# - /project2/vis_knobs_map muestra que mueve cada knob ahora.
# Uso (Textport):
#   exec(open(project.folder + '/control/fase3_fila1.py', encoding='utf-8').read())
# =============================================================

LINE = 'vis'
exec(open(project.folder + '/control/fase3_fila2.py', encoding='utf-8').read())
