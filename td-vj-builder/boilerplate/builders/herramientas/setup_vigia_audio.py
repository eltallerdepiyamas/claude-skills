# setup_vigia_audio.py — vigia de audioAnalysis. Idempotente.
# Problema (2026-11-15): la cadena interna de /project2/audio/audioAnalysis se queda "dormida" (sus CHOPs con 0
# canales); sus salidas Low/Mid/High/Kick truenan con float(None), master_audio da 0 y ningun visual recibe Energy.
# Como las salidas truenan, nada vuelve a pedir que esa cadena se cocine. Un cook forzado la despierta.
# El vigia (Execute DAT en /project2/audio) revisa cada 30 cuadros y al abrir el .toe; solo actua si esta dormida.
# Uso: exec(open(project.folder + '/builders/herramientas/setup_vigia_audio.py', encoding='utf-8').read())
A = op('/project2/audio')
CODIGO = '''# audio_vigia — lo crea builders/herramientas/setup_vigia_audio.py. Despierta audioAnalysis si se duerme.
def _dormido(aa):
    for n in ('low_', 'mid_', 'high_'):
        o = aa.op(n)
        if o is not None and o.numChans == 0:
            return True
    return False

def despertar(forzar=False):
    aa = op('/project2/audio/audioAnalysis')
    if aa is None:
        return False
    if not (forzar or _dormido(aa)):
        if aa.errors():               # error viejo que TD no limpia solo: un cook del componente lo borra
            aa.cook(force=True)
        return False
    for o in aa.findChildren(type=CHOP):
        o.cook(force=True)
    aa.cook(force=True)
    debug('[audio_vigia] audioAnalysis despertado')
    return True

def onStart():
    run("op('/project2/audio/audio_vigia').module.despertar(True)", delayFrames=30)
    return

def onFrameStart(frame):
    if frame % 30 == 0:
        despertar()
    return
'''
v = A.op('audio_vigia') or A.create(executeDAT, 'audio_vigia')
v.text = CODIGO
v.nodeX, v.nodeY = A.op('master_audio').nodeX, A.op('master_audio').nodeY - 200
for pn, val in (('start', True), ('framestart', True), ('active', True)):
    p = getattr(v.par, pn, None)
    if p is not None:
        p.val = val
v.comment = 'despierta audioAnalysis si se queda sin canales (setup_vigia_audio.py)'
print('[ok] audio_vigia listo · ahora:', 'despertado' if v.module.despertar() else 'audioAnalysis bien')
