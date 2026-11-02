"""
rig.py — lo propio de ESTE show. tdvj_core lo lee al importarse y sobreescribe sus defaults.
Copia este archivo a <proyecto>/_lib/rig.py y ajústalo; nunca edites tdvj_core.py por un show.
"""
ROOT          = '/project2'
AUDIO_SOURCE  = '/project1/null4'                  # CHOP de análisis con canales low mid high (+ kick)

# Rangos estándar del rig (el sampler MIDI depende de ellos)
VISUAL_BASES  = list(range(1, 17))                 # visuales generativos
EFFECT_BASES  = list(range(18, 25)) + list(range(38, 46))   # efectos sobre la fuente (cámaras / assets)

# base17 = fuente limpia (cámaras). En shows con multicam aloja escena_modular.
ESCENA        = ROOT + '/base17/escena_modular'
CAMERA_SWITCH = ESCENA + '/switch1'               # TOP que reciben los efectos por default

DEFAULT_RES   = (1920, 1080)
