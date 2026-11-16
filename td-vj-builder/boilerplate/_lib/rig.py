"""
rig.py — lo propio de ESTE show. tdvj_core lo lee al importarse y sobreescribe sus defaults.
Copia este archivo a <proyecto>/_lib/rig.py y ajústalo; nunca edites tdvj_core.py por un show.
"""
ROOT          = '/project2'
AUDIO_SOURCE  = '/project2/audio/master_audio'             # (antes /project1/null4; el audio vive en /project2/audio desde 2026-11-04)                  # CHOP de análisis con canales low mid high (+ kick)

# Rangos estándar del rig (el sampler MIDI depende de ellos)
VISUAL_BASES  = list(range(1, 17))                 # visuales generativos
EFFECT_BASES  = list(range(18, 33))                # efectos sobre la fuente (LJ renumeró base38–45 → 25–32)

# base17 = fuente limpia (cámaras). En shows con multicam aloja escena_modular.
ESCENA        = ROOT + '/base17/escena_modular'
CAMERA_SWITCH = ROOT + '/base17/switch1'               # TOP que reciben los efectos por default

DEFAULT_RES   = (1920, 1080)
