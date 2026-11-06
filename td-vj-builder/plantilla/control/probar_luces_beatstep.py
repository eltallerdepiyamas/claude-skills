# probar_luces_beatstep.py — parpadeo por CC para ver si los botones 1-16 de arriba responden.
# CC 1-119 (los de modo de canal, 120-127, no), canales 9, 10 y 11: 127/0 cada 2 s, 5 veces. Termina en 0.
CODIGO = """
d = op('/project2/bs_luces')
for c in (9, 10, 11):
    for n in range(1, 120):
        d.sendControl(c, n, %d)
"""
fps = int(project.cookRate)
for i in range(10):
    run(CODIGO % (127 if i % 2 == 0 else 0), delayFrames=max(1, i * 2 * fps))
print('parpadeo CC de 20 s iniciado')
