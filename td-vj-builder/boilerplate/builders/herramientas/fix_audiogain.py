# fix_audiogain.py — regresa el gain al valor anterior al hub (escena_modular.Gain = 0.422).
S = op('/project2/show')
S.par.Audiogain = op('/project2/base17/escena_modular').par.Gain.eval()
print('Audiogain =', S.par.Audiogain.eval())
