# ledfx_giro — ROTACION POR BOCINA: cada bocina gira su contenido sobre su centro, como 12 discos.
# Modos: TODAS IGUAL · ALTERNADO (una a la derecha, la siguiente a la izquierda) · OLA (cada una un poco desfasada:
# el giro corre por las bocinas) · KICK (cada kick las gira un paso, con un movimiento suave de 0.3 s).
# Velocidad en vueltas por compas (BPM detectado; sin tempo 120 BPM). Recorte circular: lo que queda fuera del circulo
# de la bocina va a negro (asi no se ven las esquinas girando; ideal para el sello y bocinas redondas).
# Pagina Giro. Apagado por default. Va despues de la cascada y antes del chaser (orden 7): gira el visual, no la luz.
# Origen: Casa Bacardi x Corona Capital (2026-11-20). Va en led_slices (o led_salida).
exec(open(project.folder + '/modulos/ledfx_comun.py', encoding='utf-8').read())
exec(open(project.folder + '/modulos/secciones.py', encoding='utf-8').read())

SHADER = r'''// giro_led — cada bocina gira su contenido sobre su centro
uniform vec4 uGiro;    // x on · y modo (0 igual, 1 alternado, 2 ola, 3 kick) · z angulo (vueltas) · w recorte circular
out vec4 fragColor;
void main() {
    vec4 src = texture(sTD2DInputs[0], vUV.st);
    if (uGiro.x < 0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    ivec2 q = ivec2(gl_FragCoord.xy);
    vec4 m = texelFetch(sTD2DInputs[1], q, 0);
    if (m.r < -0.5) { fragColor = TDOutputSwizzle(vec4(src.rgb, 1.0)); return; }
    // tamano del slice en px: cuanto cambia u, v de un pixel al vecino (dentro del mismo slice)
    vec4 mx = texelFetch(sTD2DInputs[1], q + ivec2(1, 0), 0);
    vec4 my = texelFetch(sTD2DInputs[1], q + ivec2(0, 1), 0);
    float du = abs(mx.r - m.r) < 0.5 ? mx.b - m.b : m.b - texelFetch(sTD2DInputs[1], q - ivec2(1, 0), 0).b;
    float dv = abs(my.r - m.r) < 0.5 ? my.a - m.a : m.a - texelFetch(sTD2DInputs[1], q - ivec2(0, 1), 0).a;
    vec2 tam = vec2(1.0 / max(du, 1e-5), 1.0 / max(dv, 1e-5));
    float N = max(m.g, 1.0);
    float i = m.r;
    int modo = int(uGiro.y + 0.5);
    float v = uGiro.z;
    if (modo == 1) v *= (mod(i, 2.0) < 0.5 ? 1.0 : -1.0);
    else if (modo == 2) v += i / N * 0.5;                  // ola: media vuelta de desfase de la primera a la ultima
    float a = -v * 6.2831853;
    vec2 c = (m.ba - 0.5) * tam;                           // px desde el centro de la bocina
    vec2 r = vec2(c.x * cos(a) - c.y * sin(a), c.x * sin(a) + c.y * cos(a));
    vec2 lu2 = r / tam + 0.5;
    float dentro = step(0.0, lu2.x) * step(lu2.x, 1.0) * step(0.0, lu2.y) * step(lu2.y, 1.0);
    if (uGiro.w > 0.5) dentro *= 1.0 - smoothstep(0.48, 0.5, length(lu2 - 0.5));   // recorte circular
    vec2 pix = gl_FragCoord.xy + (lu2 - m.ba) * tam;
    vec3 col = texture(sTD2DInputs[0], pix / uTDOutputInfo.res.zw).rgb * dentro;
    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
'''

LIB = r'''# giro_lib — angulo del giro (lo escribe modulos/ledfx_giro; no editar aqui)
H = parent()


def _fase():
    t = op('/project2/audio/tempo/tempo_lib')
    return t.module.fase() if t is not None else absTime.seconds * 2.0      # sin tempo: 120 BPM


def kick(val, prev):
    if not (prev < H.par.Giroumbral.eval() <= val) or H.par.Giromodo.eval() != 'kick':
        return
    H.store('giro_n', H.fetch('giro_n', 0, search=False) + 1)
    H.store('giro_t', absTime.seconds)


def angulo():
    """vueltas"""
    if H.par.Giromodo.eval() == 'kick':
        n = H.fetch('giro_n', 0, search=False)
        x = min(1.0, (absTime.seconds - H.fetch('giro_t', -100.0, search=False)) / 0.3)
        x = x * x * (3.0 - 2.0 * x)
        return (n - 1 + x) * H.par.Giropaso.eval() if n else 0.0
    return _fase() / 4.0 * H.par.Girovel.eval()
'''

H, MODO = host()
if H is None:
    print('[fallo] ledfx_giro: no hay donde ponerlo: instala antes led_slices (o led_salida)')
else:
    pg = pagina(H, 'Giro')
    par(H, pg, 'Toggle', 'Giroon', 'Giro por bocina prendido', False)
    menu(H, pg, 'Giromodo', 'Como giran', ['igual', 'alternado', 'ola', 'kick'],
         ['Todas igual', 'Alternado (der / izq)', 'Ola (desfasadas)', 'Un paso por kick'], 'alternado')
    par(H, pg, 'Toggle', 'Girorecorte', 'Recorte circular (sin esquinas)', True)
    par(H, pg, 'Float', 'Girovel', 'Velocidad (vueltas por compas)', 0.125, (0.0, 1.0))
    par(H, pg, 'Float', 'Giropaso', 'Paso por kick (vueltas; 0.125 = 45 grados)', 0.125, (0.0, 0.5))
    par(H, pg, 'Float', 'Giroumbral', 'Umbral del kick', 0.5, (0.05, 1.0))
    secciones(H, 'Giro', [('Hgiro', 'GIRO POR BOCINA', ['Giroon', 'Giromodo', 'Girorecorte']),
                          ('Hgiritmo', 'RITMO', ['Girovel', 'Giropaso', 'Giroumbral'])])
    lib = nuevo(H, textDAT, 'giro_lib', 2600, 750)
    lib.text = LIB
    k = nuevo(H, selectCHOP, 'giro_kick', 2600, 600)
    k.par.chops = '/project2/audio/master_audio'
    k.par.channames = 'kick'
    kx = nuevo(H, chopexecuteDAT, 'giro_kick_exec', 2800, 600)
    kx.par.chop = k.name
    for pn in ('channels', 'channel'):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = 'kick'
            break
    for pn, v in (('valuechange', True), ('offtoon', False), ('ontooff', False), ('whileon', False), ('whileoff', False)):
        if getattr(kx.par, pn, None) is not None:
            getattr(kx.par, pn).val = v
    kx.text = "def onValueChange(channel, sampleIndex, val, prev):\n    op('giro_lib').module.kick(val, prev)\n    return\n"
    dat = nuevo(H, textDAT, 'giro_led_pixel', 2600, 450)
    dat.text = SHADER
    g = nuevo(H, glslTOP, 'giro_led', 2600, 300)
    g.par.pixeldat = dat.name
    g.par.outputresolution = 'useinput'
    g.seq.vec.numBlocks = 1
    g.par.vec0name = 'uGiro'
    g.par.vec0valuex.expr = 'int(parent().par.Giroon.eval())'
    g.par.vec0valuey.expr = 'parent().par.Giromodo.menuIndex'
    g.par.vec0valuez.expr = "op('giro_lib').module.angulo() if absTime.frame >= 0 else 0"
    g.par.vec0valuew.expr = 'int(parent().par.Girorecorte.eval())'
    cadena = registrar(H, g, 7, 'Giroon', 'Giromodo', 'GIRO')
    g.cook(force=True)
    print('[ok] ledfx_giro en %s | cadena %s | errores: %s' % (H.path, cadena, g.errors() or 'ninguno'))
