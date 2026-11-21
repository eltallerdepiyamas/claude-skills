# desinstalar audio_auto: fuera el COMP y los parametros; el micro vuelve a escuchar solo en EN VIVO.
S = op('/project2/show')
A = op('/project2/audio')
u = A.op('audio_auto') if A is not None else None
if u is not None:
    u.destroy()
v = A.op('audio_vivo') if A is not None else None
if v is not None:
    v.par.active.expr = "op('/project2/show').par.Audiofuente == 'vivo'"
for n in ('Audiodriver', 'Audiodevice'):
    p = getattr(S.par, n, None)
    if p is not None:
        p.enableExpr = "me.par.Audiofuente == 'vivo'"
for n in ('Sepauto', 'Audioauto', 'Audioautonivel', 'Audioautoestado', 'Audioautosube', 'Audioautosubeseg',
          'Audioautobaja', 'Audioautobajaseg'):
    p = getattr(S.par, n, None)
    if p is not None:
        p.destroy()
print('[ok] audio_auto desinstalado')
