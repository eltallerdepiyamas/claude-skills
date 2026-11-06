# probar_reset.py — SOLO LEE: que cambiaria RESET ahora.
cb = op('/project2/base17/escena_modular/oscin1_callbacks').module
print([x for x in cb.resetActivo(aplicar=False) if x[1] != x[2]][:10])
print('foco:', op('/project2/base17/escena_modular').fetch('mix_comp', ''))
print('faders:', op('/project2/base17/escena_modular/scene_faders_map').text.replace('\n', ' | '))
print('extras base1:', [p.name for p in op('/project2/base17/escena_modular/scene_faders_lib').module.extras(op('/project2/base1'))])
print('feedbackTOP en /project1:', [f.path for f in op('/project1').findChildren(type=feedbackTOP)][:4], '· cue:', hasattr(op('/project2/base17/escena_modular/cam1_stock').par, 'cuepulse'))
