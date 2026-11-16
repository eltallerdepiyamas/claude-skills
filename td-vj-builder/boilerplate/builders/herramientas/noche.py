# noche.py — rutina de prueba sin operador (soak test):
#   1. apaga el piloto y regresa sus valores de fabrica · 2. guarda el .toe (con AUTO apagado)
#   3. corre revisar_visuales.py (los 48 pads) · 4. al terminar prende el PILOTO y lo deja rotando,
#      con el vigia y el registro de resistencia (control/soak_log.csv cada 5 min, control/piloto_log.txt).
# En la manana: leer control/revision_visuales.md, soak_log.csv y piloto_log.txt. Apagar AUTO con el chip.
import os, shutil, time
S = op('/project2/show')
S.par.Pilotoauto = False
for n in ('Pilotoduracion', 'Pilotominimo'):
    p = getattr(S.par, n)
    p.val = p.default
c = project.folder + '/control/'
sello = time.strftime('%Y%m%d_%H%M')
for f in ('piloto_log.txt', 'soak_log.csv'):
    if os.path.exists(c + f):
        shutil.move(c + f, c + f.replace('.', '_antes_%s.' % sello))
project.save()
print('guardado:', project.name)
lib = S.op('revisar_visuales_lib')
exec(open(project.folder + '/builders/herramientas/revisar_visuales.py', encoding='utf-8').read())
op('/project2/show/revisar_visuales_lib').store('luego_piloto', True)
print('noche en marcha: revision -> piloto automatico con registro')
