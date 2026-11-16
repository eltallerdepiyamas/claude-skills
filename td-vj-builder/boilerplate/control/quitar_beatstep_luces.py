# quitar_beatstep_luces.py — desmonta las luces del Beatstep (no funcionaron).
# Apaga las notas que TD le mandaba (canales 9, 10 y 11, pads 37-52) y borra los dos nodos que
# creo control/setup_beatstep_luces.py: /project2/bs_luces (MIDI Out) y /project2/bs_luces_exec.
# No toca el MIDI In del Beatstep, los pads ni el MIDI Mapper. Idempotente.
# Textport:  exec(open(project.folder + '/control/quitar_beatstep_luces.py', encoding='utf-8').read())
R = op('/project2')
d, ex = R.op('bs_luces'), R.op('bs_luces_exec')
if ex is not None:
    ex.par.active = False            # primero se calla, para que no vuelva a prender nada
if d is not None:
    try:
        for c in (9, 10, 11):
            for n in range(37, 53):
                d.sendNoteOff(c, n)
    except Exception as e:
        print('[aviso] no se pudieron apagar las notas:', e)
quitados = []
for o in (ex, d):
    if o is not None:
        quitados.append(o.name)
        o.destroy()
print('[ok] luces del Beatstep quitadas:', quitados or 'ya no habia nada')
