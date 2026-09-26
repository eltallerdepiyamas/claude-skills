"""
TEMPLATE — flyer_builder.py  ·  FLYER ANIMADO AUDIO-REACTIVO (standalone)
========================================================================
Toma una imagen fija (flyer/poster) y construye una red que la anima:
  boil (noise -> displace)  ->  feedback trail  ->  chroma split (RGB)
Reacciona al audio en vivo por 3 bandas (low/mid/high). Sin MIDI.
NO depende de /project2 ni de ningun baseXX: crea su propio contenedor.

PARA ADAPTARLO (lo hace el skill al generar):
  - CONTAINER: nombre del Base COMP que se crea.
  - IMAGE_PATH: ruta LOCAL del flyer en la maquina del usuario.
  - Para QUITAR un efecto: comenta su bloque en build() y recablea el
    siguiente _connect(...) al nodo anterior. Los bloques estan marcados
    (# --- boil ---, # --- feedback trail ---, # --- chroma ---).
  - Revisa library/shaders/ antes de escribir un shader nuevo.

COMO LO CORRE EL USUARIO EN TOUCHDESIGNER
  1) Cambia IMAGE_PATH por la ruta real del flyer.
  2) Crea un Text DAT, pega TODO este archivo, click derecho -> Run.
  3) Aparece el Base COMP en '/'. El viewer esta en out_null.
  4) Toca musica / habla al mic y ajusta las paginas custom 'Flyer' y 'Audio'.

IDEMPOTENTE: re-correrlo reconstruye limpio (borra ajustes manuales de la sesion).

GOTCHAS (ver SKILL.md): math.cos/sin en expresiones; Feedback TOP por Target TOP
con input vacio; 16-bit en el feedback; audio sumado en la expresion, no en el slider.
"""

import td

# ----------------------------- CONFIG -----------------------------
CONTAINER   = 'flyer_loop'          # nombre del contenedor que se crea en '/'
PARENT_PATH = '/'                   # donde vive el contenedor
IMAGE_PATH  = 'C:/ruta/a/tu/flyer.png'   # <-- CAMBIA ESTO a tu ruta local
LOOP_FPS    = 60                    # solo informativo
USE_16BIT_FEEDBACK = True           # 16-bit float en el feedback (menos banding)

# Shader de chroma embebido (no necesitas archivo externo)
CHROMA_SRC = r"""
out vec4 fragColor;
uniform vec2  uResolution;
uniform float uOffset;
uniform float uTime;
uniform float uWobble;
void main(){
    vec2 uv = vUV.st;
    vec2 px = 1.0 / uResolution;
    float ang = uTime * uWobble;
    vec2  dir = vec2(cos(ang), sin(ang)) * uOffset * px;
    float r = texture(sTD2DInputs[0], uv + dir).r;
    float g = texture(sTD2DInputs[0], uv      ).g;
    float b = texture(sTD2DInputs[0], uv - dir).b;
    float a = texture(sTD2DInputs[0], uv      ).a;
    fragColor = TDOutputSwizzle(vec4(r, g, b, a));
}
"""

# Tipos de operador
baseCOMP        = td.baseCOMP
moviefileinTOP  = td.moviefileinTOP
noiseTOP        = td.noiseTOP
displaceTOP     = td.displaceTOP
feedbackTOP     = td.feedbackTOP
transformTOP    = td.transformTOP
levelTOP        = td.levelTOP
compositeTOP    = td.compositeTOP
glslTOP         = td.glslTOP
nullTOP         = td.nullTOP
outTOP          = getattr(td, 'outTOP', None)
textDAT         = td.textDAT

audiodeviceinCHOP = td.audiodeviceinCHOP
audiofilterCHOP   = td.audiofilterCHOP
analyzeCHOP       = td.analyzeCHOP
renameCHOP        = td.renameCHOP
mergeCHOP         = td.mergeCHOP
lagCHOP           = td.lagCHOP
mathCHOP          = td.mathCHOP
nullCHOP          = td.nullCHOP
# ------------------------------------------------------------------


# --------- helpers tolerantes a version (mismo espiritu que tus builders) ---------
def _create(parent, optype, name, x, y):
    n = parent.op(name)
    if n is None:
        n = parent.create(optype, name)
    n.nodeX, n.nodeY = x, y
    return n


def _connect(src, dst, idx=0):
    dst.inputConnectors[idx].connect(src)


def _set_par(node, names, value, mode='val'):
    """Intenta poner un par probando varios nombres posibles."""
    if isinstance(names, str):
        names = (names,)
    for nm in names:
        p = getattr(node.par, nm, None)
        if p is None:
            continue
        try:
            if mode == 'expr':
                p.expr = value
                p.mode = td.ParMode.EXPRESSION
            else:
                p.val = value
            return nm
        except Exception:
            continue
    return None


def _set_menu(node, names, want):
    """Pone un par de menu probando por valor y por etiqueta/indice."""
    if isinstance(names, str):
        names = (names,)
    for nm in names:
        p = getattr(node.par, nm, None)
        if p is None:
            continue
        for w in (want if isinstance(want, (list, tuple)) else (want,)):
            try:
                p.val = w
                return nm
            except Exception:
                pass
        # por etiqueta
        try:
            labels = list(p.menuLabels or [])
            for i, lab in enumerate(labels):
                if any(str(w).lower() in lab.lower() for w in
                       (want if isinstance(want, (list, tuple)) else (want,))):
                    p.menuIndex = i
                    return nm
        except Exception:
            pass
    return None


def _set_format16(node):
    if not USE_16BIT_FEEDBACK:
        return
    _set_menu(node, ('format',), ('rgba16float', '16-bit float (RGBA)', '16'))


def _add_float(page, name, default, rng):
    p = page.appendFloat(name, label=name)[0]
    p.default, p.val = float(default), float(default)
    if rng:
        p.normMin, p.normMax = rng
        p.clampMin, p.clampMax = True, False
    return p


def _add_toggle(page, name, default=False):
    p = page.appendToggle(name, label=name)[0]
    p.default, p.val = int(default), int(default)
    return p


def _add_menu(page, name, names, default_index=0):
    p = page.appendMenu(name, label=name)[0]
    p.menuNames, p.menuLabels = names, names
    p.default = names[default_index]
    p.val = names[default_index]
    return p


def audio_term(src_par, amt_par):
    """Termino aditivo de audio: elige banda por menu (None/Low/Mid/High) * amount * master.
    None=0, Low=1, Mid=2, High=3 (orden de menuNames)."""
    return (
        "(parent().par.{amt} * parent().par.Audioreact * ("
        "op('audio')['low']  if parent().par.{src}.menuIndex==1 else "
        "op('audio')['mid']  if parent().par.{src}.menuIndex==2 else "
        "op('audio')['high'] if parent().par.{src}.menuIndex==3 else 0.0))"
    ).format(amt=amt_par, src=src_par)


def _bind_uniform(glsl, slot, uniform, exprs):
    """Bind de uniforme via la secuencia de vectors del GLSL TOP (tolerante)."""
    for cand in (f'Uniformname{slot}', f'uniformname{slot}',
                 f'Vec{slot}name', f'vec{slot}name', f'value{slot}name'):
        np_ = getattr(glsl.par, cand, None)
        if np_ is not None:
            try: np_.val = uniform
            except Exception: pass
            break
    exprs = exprs if isinstance(exprs, (tuple, list)) else (exprs,)
    for i, e in enumerate(exprs):
        axis = 'xyzw'[i]
        for cand in (f'Value{slot}{axis}', f'value{slot}{axis}',
                     f'Vec{slot}value{i}', f'vec{slot}value{i}'):
            vp = getattr(glsl.par, cand, None)
            if vp is not None:
                try:
                    vp.expr = e
                    vp.mode = td.ParMode.EXPRESSION
                except Exception:
                    pass
                break


def _ensure_vec_rows(glsl, n):
    for cand in ('vectors', 'Vectors'):
        p = getattr(glsl.par, cand, None)
        seq = getattr(p, 'sequence', None) if p is not None else None
        if seq is not None:
            try:
                if seq.numBlocks < n:
                    seq.numBlocks = n
            except Exception:
                pass
            return


# ------------------------------- BUILD -------------------------------
def build(base):
    # 1) limpiar lo que este builder maneja (idempotente)
    managed = [
        'flyer_in', 'boil_noise', 'boil_displace', 'trail_comp', 'trail_fb',
        'trail_xform', 'trail_level', 'chroma_dat', 'chroma', 'grade',
        'out_null', 'out1',
        'audio_devicein', 'af_low', 'af_mid', 'af_high',
        'an_low', 'an_mid', 'an_high', 'rn_low', 'rn_mid', 'rn_high',
        'audio_merge', 'audio_lag', 'audio_gain', 'audio',
    ]
    for nm in managed:
        ch = base.op(nm)
        if ch is not None:
            try: ch.destroy()
            except Exception: pass
    try: base.destroyCustomPars()
    except Exception: pass

    # 2) custom parameters (lo que ajustas a mano) ---------------------
    pf = base.appendCustomPage('Flyer')
    _add_float(pf, 'Boilamt',   0.010, (0.0, 0.05))    # cuanto deforma el ruido (px UV)
    _add_float(pf, 'Boilspeed', 0.6,   (0.0, 4.0))     # velocidad del hervor
    _add_float(pf, 'Boilscale', 4.0,   (1.0, 16.0))    # tamano del ruido (period)
    _add_float(pf, 'Traildecay',0.88,  (0.0, 0.99))    # cuanto dura la estela (opacity)
    _add_float(pf, 'Trailzoom', 1.010, (0.90, 1.10))   # >1 echo hacia afuera, <1 tunel
    _add_float(pf, 'Trailangle',0.0,   (-5.0, 5.0))    # giro de la estela (grados/frame)
    _add_float(pf, 'Chromaamt', 2.0,   (0.0, 30.0))    # separacion RGB base (px)
    _add_float(pf, 'Chromawob', 0.4,   (0.0, 4.0))     # bamboleo del split

    pa = base.appendCustomPage('Audio')
    _add_toggle(pa, 'Audioreact', default=True)               # master on/off
    _add_float(pa, 'Audiosmooth', 0.25, (0.0, 0.5))           # suavizado (caida del lag)
    # Por cada efecto: a que banda responde + cuanto. Defaults = el feel original.
    _add_menu(pa,  'Boilsource', ['None', 'Low', 'Mid', 'High'], default_index=2)   # Mid
    _add_float(pa, 'Boilaudio',  0.03, (0.0, 0.2))            # audio -> deformacion del boil
    _add_menu(pa,  'Speedsource', ['None', 'Low', 'Mid', 'High'], default_index=0)  # None
    _add_float(pa, 'Speedaudio', 0.0,  (0.0, 4.0))            # audio -> velocidad del hervor
    _add_menu(pa,  'Trailsource', ['None', 'Low', 'Mid', 'High'], default_index=1)  # Low
    _add_float(pa, 'Trailaudio', 0.012, (0.0, 0.1))           # audio -> pulso de la estela (zoom)
    _add_menu(pa,  'Chromasource', ['None', 'Low', 'Mid', 'High'], default_index=3) # High
    _add_float(pa, 'Chromaaudio', 25.0, (0.0, 80.0))          # audio -> split RGB

    # 3) cadena de VIDEO ----------------------------------------------
    flyer = _create(base, moviefileinTOP, 'flyer_in', -900, 0)
    _set_par(flyer, ('file',), IMAGE_PATH)

    # --- boil ---  ruido animado en circulo (periodico) -> displace
    noise = _create(base, noiseTOP, 'boil_noise', -900, -260)
    _set_par(noise, ('monochrome',), 1)
    _set_par(noise, ('period', 'noiseperiod'), 'parent().par.Boilscale', mode='expr')
    speed = '(parent().par.Boilspeed + ' + audio_term('Speedsource', 'Speedaudio') + ')'
    _set_par(noise, ('tx', 'transformtx'),
             'math.cos(absTime.seconds*' + speed + ')*0.5', mode='expr')
    _set_par(noise, ('ty', 'transformty'),
             'math.sin(absTime.seconds*' + speed + ')*0.5', mode='expr')

    disp = _create(base, displaceTOP, 'boil_displace', -680, 0)
    _connect(flyer, disp, 0)     # imagen a deformar
    _connect(noise, disp, 1)     # mapa de desplazamiento
    # peso del displace en X/Y = base + audio (banda elegida en pagina Audio)
    disp_expr = 'parent().par.Boilamt + ' + audio_term('Boilsource', 'Boilaudio')
    _set_par(disp, ('weightx', 'displaceweightx', 'horzweight', 'uvweightx'), disp_expr, mode='expr')
    _set_par(disp, ('weighty', 'displaceweighty', 'vertweight', 'uvweighty'), disp_expr, mode='expr')

    # --- feedback trail ---  feedbackTOP + transform + level(decay) + composite
    comp = _create(base, compositeTOP, 'trail_comp', -380, 0)
    _set_format16(comp)
    _set_menu(comp, ('operand',), ('over', 'Over'))

    fb = _create(base, feedbackTOP, 'trail_fb', -380, -240)
    _set_format16(fb)
    # Patron de feedback del rig: Target TOP = trail_comp, INPUT VACIO.
    # (se prueban varios nombres de par segun version de TD)
    _set_par(fb, ('top', 'targetop', 'target'), comp.name)

    xform = _create(base, transformTOP, 'trail_xform', -560, -240)
    _connect(fb, xform, 0)
    zoom_expr = 'parent().par.Trailzoom + ' + audio_term('Trailsource', 'Trailaudio')
    _set_par(xform, ('scalex', 'sx', 's1', 'scale1'), zoom_expr, mode='expr')
    _set_par(xform, ('scaley', 'sy', 's2', 'scale2'), zoom_expr, mode='expr')
    _set_par(xform, ('rotate', 'r', 'r1'), 'parent().par.Trailangle', mode='expr')

    tlevel = _create(base, levelTOP, 'trail_level', -560, -80)
    _connect(xform, tlevel, 0)
    _set_format16(tlevel)
    _set_par(tlevel, ('opacity', 'opacity1'), 'parent().par.Traildecay', mode='expr')

    _connect(disp, comp, 0)      # frame actual (arriba)
    _connect(tlevel, comp, 1)    # estela desvanecida (atras)

    # --- chroma ---  split RGB (GLSL); shader en library/shaders/chroma_split.glsl
    cdat = _create(base, textDAT, 'chroma_dat', -180, -240)
    cdat.text = CHROMA_SRC
    chroma = _create(base, glslTOP, 'chroma', -120, 0)
    _connect(comp, chroma, 0)
    _set_par(chroma, ('pixeldat', 'pixelshader'), cdat.name)
    _ensure_vec_rows(chroma, 5)
    _bind_uniform(chroma, 0, 'uResolution', ("op('chroma').width", "op('chroma').height"))
    _bind_uniform(chroma, 1, 'uOffset',
                  ['parent().par.Chromaamt + ' + audio_term('Chromasource', 'Chromaaudio')])
    _bind_uniform(chroma, 2, 'uTime',   ['absTime.seconds'])
    _bind_uniform(chroma, 3, 'uWobble', ['parent().par.Chromawob'])

    # grade final + salida
    grade = _create(base, levelTOP, 'grade', 120, 0)
    _connect(chroma, grade, 0)

    onull = _create(base, nullTOP, 'out_null', 320, 0)
    _connect(grade, onull, 0)
    try: onull.viewer = True
    except Exception: pass
    if outTOP is not None:
        o = _create(base, outTOP, 'out1', 500, 0)
        _connect(onull, o)

    # 4) cadena de AUDIO (3 bandas, en vivo) --------------------------
    adev = _create(base, audiodeviceinCHOP, 'audio_devicein', -900, 320)

    def band(name, x, ftype, cutoff):
        af = _create(base, audiofilterCHOP, f'af_{name}', -680, x)
        _connect(adev, af, 0)
        _set_menu(af, ('filter',), ftype)
        _set_par(af, ('cutofflog', 'cutoff', 'frequency'), cutoff)
        an = _create(base, analyzeCHOP, f'an_{name}', -480, x)
        _connect(af, an, 0)
        _set_menu(an, ('function', 'func'), ('rms', 'RMS Power', 'rmspower'))
        rn = _create(base, renameCHOP, f'rn_{name}', -300, x)
        _connect(an, rn, 0)
        _set_par(rn, ('renamefrom', 'from'), '*')
        _set_par(rn, ('renameto', 'to'), name)
        return rn

    rn_low  = band('low',  300, ('Low Pass', 'lowpass'),   150)
    rn_mid  = band('mid',  420, ('Band Pass', 'bandpass'), 1200)
    rn_high = band('high', 540, ('High Pass', 'highpass'),  4000)

    amerge = _create(base, mergeCHOP, 'audio_merge', -120, 420)
    _connect(rn_low, amerge, 0)
    _connect(rn_mid, amerge, 1)
    _connect(rn_high, amerge, 2)

    alag = _create(base, lagCHOP, 'audio_lag', 60, 420)
    _connect(amerge, alag, 0)
    _set_par(alag, ('lag1', 'lag'), 'parent().par.Audiosmooth*0.2', mode='expr')  # ataque rapido
    _set_par(alag, ('lag2',), 'parent().par.Audiosmooth', mode='expr')            # caida suave

    again = _create(base, mathCHOP, 'audio_gain', 240, 420)
    _connect(alag, again, 0)
    _set_par(again, ('gain', 'gain1'), 20.0)   # sube el RMS a un rango usable ~0-1

    _create(base, nullCHOP, 'audio', 420, 420)
    _connect(again, base.op('audio'), 0)

    print(f"[ok] {base.path} listo.")
    print("     Video: flyer_in -> boil(noise+displace) -> trail(feedback) -> chroma -> grade -> out_null")
    print("     Audio: audio_devicein -> 3 bandas (low/mid/high) -> null 'audio'")
    print("     Ajusta en las paginas custom 'Flyer' y 'Audio' del contenedor.")
    if IMAGE_PATH.startswith('C:/ruta'):
        print("     [!] Acuerdate de poner IMAGE_PATH con la ruta real de tu flyer.")


def run():
    parent = td.op(PARENT_PATH) or td.root
    base = parent.op(CONTAINER)
    if base is None:
        base = parent.create(baseCOMP, CONTAINER)
        base.nodeX, base.nodeY = 0, 0
    build(base)


run()
