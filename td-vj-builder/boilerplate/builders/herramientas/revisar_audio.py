# revisar_audio.py — chequeo del audio de punta a punta: fuente -> audioAnalysis -> master_audio -> Energy.
# Regla del boilerplate: el audio SIEMPRE al cien. Correrlo al abrir un show, antes de ensayar y antes del show.
# Dice en que punto se corta la senal. Si audioAnalysis esta dormido, lo despierta (audio_vigia).
# Textport: exec(open(project.folder + '/builders/herramientas/revisar_audio.py', encoding='utf-8').read())
import os
A = op('/project2/audio')
S = op('/project2/show')


def pico(o):
    try:
        return max(abs(v) for c in o.chans() for v in c.vals) if o is not None and o.numChans else 0.0
    except Exception:
        return 0.0


fallas = []
f = getattr(S.par, 'Audiofuente', None)
fuente = f.eval() if f is not None else '?'
arch = S.par.Audioarchivo.eval() if getattr(S.par, 'Audioarchivo', None) is not None else ''
if fuente == 'archivo' and arch and not os.path.exists(arch):
    fallas.append('el archivo de audio no existe en esta compu: %s' % arch)
entrada = A.op('audio_gain') or A.op('audio_fuente')
pe = pico(entrada)
if pe < 0.001:
    fallas.append('no entra senal (%s): revisa Audiofuente, el archivo o la tarjeta, y que la linea de tiempo corra' %
                  (entrada.path if entrada else 'sin audio_gain'))
v = A.op('audio_vigia')
if v is None:
    fallas.append('falta audio_vigia: corre setup_vigia_audio.py')
elif v.module.despertar():
    print('[aviso] audioAnalysis estaba dormido: despertado')
m = A.op('master_audio')
bandas = {n: round(float(m[n].eval()), 3) for n in ('low', 'mid', 'high', 'kick') if m is not None and m[n] is not None}
if pe >= 0.001 and not any(bandas.values()):
    fallas.append('entra senal pero master_audio esta en 0: audioAnalysis no responde (revisa sus errores)')
aa = A.op('audioAnalysis')
if aa is not None and aa.errors():
    fallas.append('audioAnalysis con errores: %s' % aa.errors().splitlines()[0][:120])
energia = {}
for b in op('/project2').findChildren(name='base*', depth=1):
    p = getattr(b.par, 'Energy', None)
    if p is not None and b.allowCooking:
        try:
            energia[b.name] = round(float(p.eval()), 3)
        except Exception:
            energia[b.name] = 'ERR'
print('fuente:', fuente, '| pico de entrada: %.2f' % pe, '| master_audio:', bandas)
print('Energy por base (las que tienen audio):', {k: e for k, e in energia.items() if e not in (0.0,)} or 'todas en 0')
print('[ok] audio al cien' if not fallas else '[X] ' + '\n[X] '.join(fallas))
