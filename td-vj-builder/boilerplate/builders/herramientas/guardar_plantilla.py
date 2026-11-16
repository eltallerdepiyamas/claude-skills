# guardar_plantilla.py — guarda las posiciones actuales de /project2 como plantilla del boilerplate.
import json
R = op('/project2')
d = {o.path: [o.nodeX, o.nodeY, list(o.color)] for o in R.children}
json.dump(d, open(project.folder + '/control/plantilla_project2.json', 'w', encoding='utf-8'), indent=0)
print('[ok] plantilla:', len(d), 'nodos')
