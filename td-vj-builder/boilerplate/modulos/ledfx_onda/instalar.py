# ledfx_onda — ONDA DE KICK: cada kick (o cada N) lanza un pulso de luz que viaja de bocina en bocina y se apaga
# (segunda capa). Se ve como el sonido corriendo por las bocinas. Hasta 4 ondas a la vez.
# Desde: en orden (A-1 -> ultimo) · desde el centro hacia los extremos · desde los extremos al centro · ida y vuelta.
# Como se ve: LUZ (suma un halo en la tinta) o BRILLO (solo aviva el visual donde pasa la onda; lo demas en Fondo).
# Pagina Onda. Apagado por default. Kick = canal kick de /project2/audio/master_audio.
# Origen: Casa Bacardi x Corona Capital (2026-11-20). Va en led_slices (o led_salida). Orden en la cadena 40.
exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())
AUDIO = '/project2/audio/master_audio'

SHADER = r'''// onda_led — pulsos que viajan de bocina en bocina (uno por kick)
uniform vec4 uOn;      // x on · y desde (0 orden, 1 centro, 2 extremos, 3 ida y vuelta) · z modo (0 luz, 1 brillo) · w fondo
uniform vec4 uOnda;    // x velocidad (bocinas / s) · y ancho (bocinas) · z decaimiento (s) · w intensidad
uniform vec4 uEdad;    // edad (s) de hasta 4 ondas; < 0 = no hay
uniform vec4 uTinta;
out vec4 fragColor;

float distancia(float i, float N, int desde) {
    float c = (N - 1.0) * 0.5;
    if (desde == 1) return abs(i - c);                    // centro -> extremos
    if (desde == 2) return c - abs(i - c);                // extremos -> centro
    return i;                                             // en orden (e ida y vuelta)
}

void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uOn.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    vec4 m = texelFetch(sTD2DInputs[1], ivec2(gl_FragCoord.xy), 0);
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    float N = max(m.g, 1.0);
    int desde = int(uOn.y + 0.5);
    float d = distancia(m.r, N, desde) + (m.b - 0.5) * 0.6;   // un poco de recorrido dentro de la bocina
    float largo = (desde == 1 || desde == 2) ? (N - 1.0) * 0.5 : N - 1.0;
    float w = max(uOnda.y, 0.2);
    float nivel = 0.0;
    for (int k = 0; k < 4; k++) {
        float edad = uEdad[k];
        if (edad < 0.0) continue;
        float pos = edad * uOnda.x - w;                   // entra desde antes de la primera bocina
        if (desde == 3) {                                 // ida y vuelta
            float per = 2.0 * largo;
            float q = mod(pos + w, per + 2.0 * w) - w;
            pos = q <= largo + w ? q : per - q;
        }
        float e = exp(-pow((d - pos) / w, 2.0)) * exp(-edad / max(uOnda.z, 0.05));
        nivel = max(nivel, e);
    }
    vec3 col;
    if (uOn.z > 0.5) col = src.rgb * mix(uOn.w, 1.0 + 0.5 * uOnda.w, nivel);           // BRILLO
    else col = src.rgb + uTinta.rgb * nivel * uOnda.w;                                  // LUZ
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

LIB = r'''# onda_lib — lanza una onda por kick (lo escribe modulos/ledfx_onda; no editar aqui)
H = parent()


def kick(val, prev):
    thr = H.par.Ondaumbral.eval()
    if not (prev < thr <= val) or not H.par.Ondaon.eval():
        return
    n = H.fetch('onda_kicks', 0, search=False) + 1
    H.store('onda_kicks', n)
    if n % max(1, int(H.par.Ondacada.eval())) == 0:
        lanzar()


def lanzar():
    ondas = [t for t in H.fetch('onda_t', [], search=False) if absTime.seconds - t < 8.0][-3:]
    ondas.append(absTime.seconds)
    H.store('onda_t', ondas)


def edad(k):
    ondas = H.fetch('onda_t', [], search=False)
    if k >= len(ondas):
        return -1.0
    return absTime.seconds - ondas[-1 - k]
'''

H, MODO = host()
if H is None:
    print('[fallo] ledfx_onda: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    pg = pagina(H, 'Onda')
    par(H, pg, 'Toggle', 'Ondaon', 'Onda de kick prendida', False)
    menu(H, pg, 'Ondadesde', 'Recorre', ['orden', 'centro', 'extremos', 'idavuelta'],
         ['En orden (A-1 -> ultimo)', 'Del centro a los extremos', 'De los extremos al centro', 'Ida y vuelta'], 'centro')
    menu(H, pg, 'Ondamodo', 'Como se ve', ['luz', 'brillo'], ['Luz (halo en la tinta)', 'Brillo (aviva el visual)'], 'luz')
    menu(H, pg, 'Ondatinta', 'Tinta', ['a', 'b', 'blanco'], ['Color A (paleta)', 'Color B (paleta)', 'Blanco'], 'a')
    par(H, pg, 'Float', 'Ondaint', 'Intensidad', 0.8, (0.0, 2.0))
    par(H, pg, 'Float', 'Ondafondo', 'Fondo en modo brillo', 0.4, (0.0, 1.0))
    par(H, pg, 'Int', 'Ondacada', 'Una onda cada (kicks)', 1, (1, 8))
    par(H, pg, 'Float', 'Ondaumbral', 'Umbral del kick', 0.5, (0.05, 1.0))
    par(H, pg, 'Float', 'Ondavel', 'Velocidad (bocinas / s)', 20.0, (2.0, 60.0))
    par(H, pg, 'Float', 'Ondaancho', 'Ancho (bocinas)', 1.2, (0.3, 4.0))
    par(H, pg, 'Float', 'Ondadecay', 'Se apaga en (s)', 0.6, (0.1, 3.0))
    if not hasattr(H.par, 'Ondaprueba'):
        pg.appendPulse('Ondaprueba', label='Lanzar una onda (prueba)')
    secciones(H, 'Onda', [('Honda', 'ONDA DE KICK', ['Ondaon', 'Ondadesde', 'Ondaprueba']),
                          ('Hondalook', 'COMO SE VE', ['Ondamodo', 'Ondatinta', 'Ondaint', 'Ondafondo']),
                          ('Hondaritmo', 'RITMO Y FORMA', ['Ondacada', 'Ondaumbral', 'Ondavel', 'Ondaancho', 'Ondadecay'])])

    lib = nuevo(H, textDAT, 'onda_lib', 2000, 750)
    lib.text = LIB
    k = nuevo(H, selectCHOP, 'onda_kick', 2000, 600)
    k.par.chops = AUDIO
    k.par.channames = 'kick'
    kx = nuevo(H, chopexecuteDAT, 'onda_kick_exec', 2200, 600)
    kx.par.chop = k.name
    for pn in ('channels', 'channel'):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = 'kick'
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False), ('whileon', False), ('whileoff', False)):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = v
    kx.text = "def onValueChange(channel, sampleIndex, val, prev):\n    op('onda_lib').module.kick(val, prev)\n    return\n"
    px = nuevo(H, parameterexecuteDAT, 'onda_pulso', 2200, 750)
    px.par.op = H.path
    px.par.pars = 'Ondaprueba'
    px.par.onpulse = True
    px.text = "def onPulse(par):\n    op('onda_lib').module.lanzar()\n    return\n"

    dat = nuevo(H, textDAT, 'onda_led_pixel', 2000, 450)
    dat.text = SHADER
    g = nuevo(H, glslTOP, 'onda_led', 2000, 300)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 4
    g.par.vec0name = 'uOn'
    g.par.vec0valuex.expr = 'int(parent().par.Ondaon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Ondadesde.menuIndex'
    g.par.vec0valuez.expr = 'parent().par.Ondamodo.menuIndex'
    g.par.vec0valuew.expr = 'parent().par.Ondafondo'
    g.par.vec1name = 'uOnda'
    g.par.vec1valuex.expr = 'parent().par.Ondavel'
    g.par.vec1valuey.expr = 'parent().par.Ondaancho'
    g.par.vec1valuez.expr = 'parent().par.Ondadecay'
    g.par.vec1valuew.expr = 'parent().par.Ondaint'
    g.par.vec2name = 'uEdad'
    for i, c in enumerate('xyzw'):
        getattr(g.par, 'vec2value' + c).expr = "op('onda_lib').module.edad(%d) if absTime.frame >= 0 else -1" % i
    g.par.vec3name = 'uTinta'
    tinta_exprs(g, 'vec3', 'Ondatinta')
    cadena = registrar(H, g, 40, 'Ondaon', 'Ondadesde', 'ONDA')
    g.cook(force=True)
    print('[ok] ledfx_onda en %s | cadena %s | errores: %s' % (H.path, cadena, g.errors() or 'ninguno'))
