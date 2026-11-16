# setup_ensayo.py: pestana Ensayo en /project2/show con REC on/off + grabacion con audio.
# Graba /project2/master_visuales (video) + /project2/audio/audio_fuente (audio stereo)
# a renders/ensayo_YYYYMMDD_HHMMSS.{mov|mp4}.
#
# Nodos creados (todos dentro de /project2/show):
#   rec_source  (selectTOP)        -> trae master_visuales cross-comp (TOPs solo conectan a hermanos)
#   rec_video   (moviefileoutTOP)  -> graba video+audio
#   rec_cooker  (executeDAT)       -> fuerza cookeo de rec_video cada frame cuando record=True
#   rec_exec    (parameterexecuteDAT) -> enciende/apaga grabacion al mover el par Rec del show
#
# Codec: Hap+pcm16 (.mov) -- universal, funciona con cualquier audio/resolucion.
# Para H.264 el user puede cambiar Reccodec en la UI (menu Hap / H.264 NV GPU).
# Idempotente.
import os

ROOT = '/project2'
R2 = op(ROOT)
SHOW = R2.op('show')
MASTER = R2.op('master_visuales')
AUDIO_RAW = R2.op('audio/audio_fuente') or R2.op('audio/audio_gain')   # stereo pre-gain, o mono con gain
assert SHOW is not None, 'no existe /project2/show'

OUT_DIR = project.folder.replace('\\', '/') + '/renders'
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)

def page(c, name):
    return next((p for p in c.customPages if p.name == name), None) or c.appendCustomPage(name)

# ---- Pars en show ----
pg = page(SHOW, 'Ensayo')
if not hasattr(SHOW.par, 'Rec'):
    pg.appendToggle('Rec', label='REC')
if not hasattr(SHOW.par, 'Recarchivo'):
    pg.appendStr('Recarchivo', label='Ultimo archivo')
    SHOW.par.Recarchivo.readOnly = True
if not hasattr(SHOW.par, 'Reccodec'):
    pg.appendMenu('Reccodec', label='Codec')
SHOW.par.Reccodec.menuNames = ['hap', 'h264']
SHOW.par.Reccodec.menuLabels = ['Hap (universal, .mov)', 'H.264 NV GPU (.mp4)']
if SHOW.par.Reccodec.eval() not in ('hap', 'h264'):
    SHOW.par.Reccodec.val = 'hap'
if not hasattr(SHOW.par, 'Recpulse'):
    pg.appendPulse('Recpulse', label='Toggle REC (prueba)')

# ---- Limpiar cualquier instancia vieja (en /project2 o en otro sitio) ----
for old_path in ('/project2/rec_video',):   # cualquier rec_video fuera de show
    o = op(old_path)
    if o is not None and o.parent() is not SHOW:
        o.destroy()

# ---- selectTOP (cross-comp): trae master_visuales a dentro de show ----
sel = SHOW.op('rec_source') or SHOW.create(selectTOP, 'rec_source')
sel.nodeX, sel.nodeY = 0, -400
if MASTER is not None:
    sel.par.top = MASTER.path

# ---- moviefileoutTOP dentro de show ----
rec = SHOW.op('rec_video') or SHOW.create(moviefileoutTOP, 'rec_video')
rec.nodeX, rec.nodeY = 200, -400
rec.inputConnectors[0].disconnect()
rec.inputConnectors[0].connect(sel)
rec.viewer = True   # fuerza cook del propio rec_video
# codec default: Hap+pcm16 (universal). El chopexec ajusta segun Reccodec actual al prender REC.
rec.par.videocodec = 'hap'
rec.par.audiocodec = 'pcm16'
if AUDIO_RAW is not None and hasattr(rec.par, 'audiochop'):
    rec.par.audiochop = AUDIO_RAW.path

# ---- rec_cooker (executeDAT): fuerza cook del rec cada frame cuando graba ----
# Necesario porque un moviefileoutTOP sin viewer visible no cookea automaticamente.
cook = SHOW.op('rec_cooker') or SHOW.create(executeDAT, 'rec_cooker')
cook.par.framestart = True
cook.nodeX, cook.nodeY = 400, -520
cook.text = '''# fuerza cookeo de rec_video cada frame cuando esta grabando
def onFrameStart(frame):
    rec = op('/project2/show/rec_video')
    if rec is None: return
    if rec.par.record.eval():
        rec.cook(force=True)

def onCreate(): pass
def onExit(): pass
def onFrameEnd(frame): pass
def onPlayStateChange(state): pass
def onDeviceChange(): pass
def onProjectPreSave(): pass
def onProjectPostSave(): pass
'''

# ---- rec_exec (parameterexecuteDAT): on/off en respuesta al toggle Rec ----
pex = SHOW.op('rec_exec') or SHOW.create(parameterexecuteDAT, 'rec_exec')
pex.nodeX, pex.nodeY = 200, -520
pex.par.op = SHOW
pex.par.pars = 'Rec Recpulse'
pex.par.valuechange = True
pex.par.onpulse = True
pex.text = '''# generado por setup_ensayo.py
import datetime, os

# Reccodec key -> (videocodec, audiocodec compatible, extension)
CODEC_MENU = {
    'hap':  ('hap',       'pcm16', '.mov'),
    'h264': ('h264nvgpu', 'mp3',   '.mp4'),
}

def _rec():
    return op('/project2/show/rec_video')

def _stop(SHOW):
    rec = _rec()
    if rec is None: return
    rec.par.record = False
    archivo = rec.par.file.eval()
    if archivo:
        SHOW.par.Recarchivo = os.path.basename(archivo)
    print('[rec] off')

def _start(SHOW):
    rec = _rec()
    if rec is None:
        print('[rec] falta /project2/show/rec_video'); return
    key = SHOW.par.Reccodec.eval()
    vcodec, acodec, ext = CODEC_MENU.get(key, ('hap', 'pcm16', '.mov'))
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta = project.folder.replace('\\\\', '/') + '/renders'
    if not os.path.isdir(carpeta):
        os.makedirs(carpeta)
    archivo = carpeta + '/ensayo_' + ts + ext
    rec.par.file = archivo
    rec.par.videocodec = vcodec
    rec.par.audiocodec = acodec
    rec.par.record = True
    SHOW.par.Recarchivo = os.path.basename(archivo)
    print('[rec] on -> ' + archivo)

def onValueChange(par, prev):
    SHOW = par.owner
    if par.name == 'Rec':
        if par.eval():
            _start(SHOW)
        else:
            _stop(SHOW)

def onPulse(par):
    SHOW = par.owner
    if par.name == 'Recpulse':
        SHOW.par.Rec = not SHOW.par.Rec.eval()
'''

# Asegurar que la pestana Ensayo quede en el pagescope del widget UI que muestra las pestanas de show.
# setup_ui.py sobrescribe pagescope sin incluir Ensayo; esto garantiza que vuelva a aparecer idempotentemente.
hub = op('/project2/ui_perform/par_show_hub')
if hub is not None:
    scope = hub.par.pagescope.val
    if 'Ensayo' not in scope:
        hub.par.pagescope = (scope + ' Ensayo').strip()
        print('[OK] pagescope actualizado con Ensayo')

print('[OK] Pestana Ensayo lista. REC -> ' + OUT_DIR)
print('    rec_video dentro de /project2/show (con rec_source + rec_cooker).')
