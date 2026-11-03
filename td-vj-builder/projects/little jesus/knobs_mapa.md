# Mapa de knobs del MIDImix

## MIDI In en el proyecto

- `/project1/midiin1` (midiinCHOP)
- `/project1/midiin2` (midiinCHOP)
- `/project1/midiin3` (midiinCHOP)
- `/project2/MIDI` (midiinCHOP)

## Quien lee cada CC

| CC | Posicion | Operador | Donde | Texto |
|---|---|---|---|---|
| ch1 cc17 | fila 1, col 1 | `/project1/curcuitBending` | Amount (expr) | `op('null5')['ch1ctrl17']` |
| ch1 cc17 | fila 1, col 1 | `/project1/select20` | channames (valor) | `ch1ctrl17` |
| ch1 cc17 | fila 1, col 1 | `/project1/select26` | channames (valor) | `ch1ctrl17` |
| ch1 cc17 | fila 1, col 1 | `/project1/select5` | channames (valor) | `ch1ctrl17 ch1ctrl29 ch1ctrl47 ch1ctrl61 ch1ctrl56` |
| ch1 cc18 | fila 2, col 1 | `/project1/PrismTop4` | Pattern0instances (expr) | `op('null15')['ch1ctrl18']` |
| ch1 cc18 | fila 2, col 1 | `/project1/select15` | channames (valor) | `ch1ctrl18 ch1ctrl19` |
| ch1 cc18 | fila 2, col 1 | `/project1/select21` | channames (valor) | `ch1ctrl18` |
| ch1 cc19 | fila 3, col 1 | `/project1/PrismTop4` | Pattern1instances (expr) | `op('null15')['ch1ctrl19']` |
| ch1 cc19 | fila 3, col 1 | `/project1/select15` | channames (valor) | `ch1ctrl18 ch1ctrl19` |
| ch1 cc19 | fila 3, col 1 | `/project1/select22` | channames (valor) | `ch1ctrl19` |
| ch1 cc20 | faders, col 1 | `/project1/select1` | channames (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc20 | faders, col 1 | `/project1/select1` | renamefrom (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc20 | faders, col 1 | `/project1/select23` | channames (valor) | `ch1ctrl20` |
| ch1 cc20 | faders, col 1 | `/project1/select25` | channames (valor) | `ch1ctrl20` |
| ch1 cc21 | fila 1, col 2 | `/project1/curcuitBending` | Tx (expr) | `op('null10')['ch1ctrl21']` |
| ch1 cc21 | fila 1, col 2 | `/project1/select28` | channames (valor) | `ch1ctrl21` |
| ch1 cc21 | fila 1, col 2 | `/project1/select32` | channames (valor) | `ch1ctrl21` |
| ch1 cc21 | fila 1, col 2 | `/project1/select8` | channames (valor) | `ch1ctrl21 ch1ctrl25` |
| ch1 cc22 | fila 2, col 2 | `/project1/PrismTop4` | Pattern0radius (expr) | `op('null19')['ch1ctrl22']` |
| ch1 cc22 | fila 2, col 2 | `/project1/select19` | channames (valor) | `ch1ctrl22 ch1ctrl23` |
| ch1 cc22 | fila 2, col 2 | `/project1/select39` | channames (valor) | `ch1ctrl22` |
| ch1 cc23 | fila 3, col 2 | `/project1/PrismTop4` | Pattern1radius (expr) | `op('null19')['ch1ctrl23']` |
| ch1 cc23 | fila 3, col 2 | `/project1/select19` | channames (valor) | `ch1ctrl22 ch1ctrl23` |
| ch1 cc24 | faders, col 2 | `/project1/select1` | channames (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc24 | faders, col 2 | `/project1/select1` | renamefrom (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc25 | fila 1, col 3 | `/project1/curcuitBending` | Ty (expr) | `op('null10')['ch1ctrl25']` |
| ch1 cc25 | fila 1, col 3 | `/project1/select8` | channames (valor) | `ch1ctrl21 ch1ctrl25` |
| ch1 cc26 | fila 2, col 3 | `/project1/PrismTop4` | Pattern0amp (expr) | `op('null23')['ch1ctrl26']` |
| ch1 cc26 | fila 2, col 3 | `/project1/select29` | channames (valor) | `ch1ctrl26 ch1ctrl27` |
| ch1 cc27 | fila 3, col 3 | `/project1/PrismTop4` | Pattern1amp (expr) | `op('null23')['ch1ctrl27']` |
| ch1 cc27 | fila 3, col 3 | `/project1/select29` | channames (valor) | `ch1ctrl26 ch1ctrl27` |
| ch1 cc28 | faders, col 3 | `/project1/select1` | channames (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc28 | faders, col 3 | `/project1/select1` | renamefrom (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc29 | fila 1, col 4 | `/project1/curcuitBending` | Amount2 (expr) | `op('null5')['ch1ctrl29']` |
| ch1 cc29 | fila 1, col 4 | `/project1/select5` | channames (valor) | `ch1ctrl17 ch1ctrl29 ch1ctrl47 ch1ctrl61 ch1ctrl56` |
| ch1 cc30 | fila 2, col 4 | `/project1/PrismTop4` | Pattern0alpha (expr) | `op('null35')['ch1ctrl30']` |
| ch1 cc30 | fila 2, col 4 | `/project1/select31` | channames (valor) | `ch1ctrl30 ch1ctrl31` |
| ch1 cc31 | fila 3, col 4 | `/project1/PrismTop4` | Pattern1alpha (expr) | `op('null35')['ch1ctrl31']` |
| ch1 cc31 | fila 3, col 4 | `/project1/select31` | channames (valor) | `ch1ctrl30 ch1ctrl31` |
| ch1 cc32 | faders, col 4 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc40 | ? | `/project1/select12` | channames (valor) | `ch1ctrl40 ch1ctrl56 ` |
| ch1 cc42 | ? | `/project1/select16` | channames (valor) | `ch1ctrl42` |
| ch1 cc44 | ? | `/project1/select36` | channames (valor) | `ch1ctrl44` |
| ch1 cc45 | ? | `/project1/select14` | channames (valor) | `ch1ctrl45` |
| ch1 cc46 | ? | `/project1/select27` | channames (valor) | `ch1ctrl46 ch1n28 ch1n22 ch1n26 ch1n27` |
| ch1 cc47 | fila 1, col 5 | `/project1/curcuitBending` | Vstep (expr) | `op('null5')['ch1ctrl47']` |
| ch1 cc47 | fila 1, col 5 | `/project1/select5` | channames (valor) | `ch1ctrl17 ch1ctrl29 ch1ctrl47 ch1ctrl61 ch1ctrl56` |
| ch1 cc48 | fila 2, col 5 | `/project1/select40` | channames (valor) | `ch1ctrl48 ch1ctrl49` |
| ch1 cc49 | fila 3, col 5 | `/project1/feedback_HSV1` | Alphamult (expr) | `op('null29')['ch1ctrl49']` |
| ch1 cc49 | fila 3, col 5 | `/project1/select40` | channames (valor) | `ch1ctrl48 ch1ctrl49` |
| ch1 cc50 | faders, col 5 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc51 | fila 1, col 6 | `/project1/curcuitBending` | Period (expr) | `op('null11')['ch1ctrl51']` |
| ch1 cc51 | fila 1, col 6 | `/project1/select62` | channames (valor) | `ch1ctrl51` |
| ch1 cc51 | fila 1, col 6 | `/project1/select9` | channames (valor) | `ch1ctrl51` |
| ch1 cc52 | fila 2, col 6 | `/project1/select38` | channames (valor) | `ch1ctrl52` |
| ch1 cc52 | fila 2, col 6 | `/project2/select1` | channames (valor) | `ch1ctrl52` |
| ch1 cc53 | fila 3, col 6 | `/project1/base6/ramp1` | period (expr) | `parent(2).op('null58')['ch1ctrl53']` |
| ch1 cc53 | fila 3, col 6 | `/project1/select41` | channames (valor) | `ch1ctrl53` |
| ch1 cc53 | fila 3, col 6 | `/project2/base26/base6/ramp1` | period (expr) | `op('/project1/null58')['ch1ctrl53']` |
| ch1 cc53 | fila 3, col 6 | `/project2/base29/base7/ramp1` | period (expr) | `op('/project1/null58')['ch1ctrl53']` |
| ch1 cc53 | fila 3, col 6 | `/project2/base30/base8/ramp1` | period (expr) | `op('/project1/null58')['ch1ctrl53']` |
| ch1 cc54 | faders, col 6 | `/project1/select10` | channames (valor) | `ch1ctrl54` |
| ch1 cc54 | faders, col 6 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc56 | fila 2, col 7 | `/project1/select12` | channames (valor) | `ch1ctrl40 ch1ctrl56 ` |
| ch1 cc56 | fila 2, col 7 | `/project1/select5` | channames (valor) | `ch1ctrl17 ch1ctrl29 ch1ctrl47 ch1ctrl61 ch1ctrl56` |
| ch1 cc56 | fila 2, col 7 | `/project1/select54` | channames (valor) | `ch1ctrl56` |
| ch1 cc56 | fila 2, col 7 | `/project2/base27/GLSL_Kaleidoscope1` | Kaleidonum (expr) | `op('/project1/null3')['ch1ctrl56']` |
| ch1 cc57 | fila 3, col 7 | `/project1/select46` | channames (valor) | `ch1ctrl57` |
| ch1 cc57 | fila 3, col 7 | `/project1/switch3` | index (expr) | `op('null60')['ch1ctrl57']` |
| ch1 cc58 | faders, col 7 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc59 | fila 1, col 8 | `/project1/null5_export` | texto DAT | `ch1ctrl59	3	base4/trigger1	threshup	1` |
| ch1 cc59 | fila 1, col 8 | `/project1/select13` | channames (valor) | `ch1ctrl59` |
| ch1 cc59 | fila 1, col 8 | `/project1/select35` | channames (valor) | `ch1ctrl59` |
| ch1 cc59 | fila 1, col 8 | `/project1/select7` | channames (valor) | `ch1ctrl59 ch1n5` |
| ch1 cc60 | fila 2, col 8 | `/project1/lumalevel1` | blacklevel (expr) | `op('null6')['ch1ctrl60']` |
| ch1 cc60 | fila 2, col 8 | `/project1/select53` | channames (valor) | `ch1ctrl60` |
| ch1 cc60 | fila 2, col 8 | `/project1/select6` | channames (valor) | `ch1ctrl60 ch1n2` |
| ch1 cc61 | fila 3, col 8 | `/project1/select24` | channames (valor) | `ch1ctrl61` |
| ch1 cc61 | fila 3, col 8 | `/project1/select5` | channames (valor) | `ch1ctrl17 ch1ctrl29 ch1ctrl47 ch1ctrl61 ch1ctrl56` |
| ch1 cc61 | fila 3, col 8 | `/project2/base17/animated_displacement_map2/chroma1` | satmin (expr) | `op('/project1/null5')['ch1ctrl61']` |
| ch1 cc62 | faders, col 8 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc63 | faders, col 9 | `/project1/select1` | channames (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc63 | faders, col 9 | `/project1/select1` | renamefrom (valor) | `ch1ctrl20 ch1ctrl24 ch1ctrl28 ch1ctrl63` |
| ch1 cc63 | faders, col 9 | `/project1/select34` | channames (valor) | `ch1ctrl63` |
| ch1 cc63 | faders, col 9 | `/project2/base17/escena_modular/scene_faders_in` | channames (valor) | `ch1ctrl32 ch1ctrl50 ch1ctrl54 ch1ctrl58 ch1ctrl62 ch1ctrl63` |
| ch1 cc66 | ? | `/project1/select30` | channames (valor) | `ch1ctrl66` |
| ch1 cc70 | ? | `/project1/select17` | channames (valor) | `ch1ctrl70` |
| ch10 cc21 | fila 1, col 2 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc21 | fila 1, col 2 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc22 | fila 2, col 2 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc22 | fila 2, col 2 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc23 | fila 3, col 2 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc23 | fila 3, col 2 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc24 | faders, col 2 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc24 | faders, col 2 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc25 | fila 1, col 3 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc25 | fila 1, col 3 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc26 | fila 2, col 3 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc26 | fila 2, col 3 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc27 | fila 3, col 3 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc27 | fila 3, col 3 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc28 | faders, col 3 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc28 | faders, col 3 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc55 | fila 1, col 7 | `/project1/select58` | channames (valor) | `ch10ctrl55` |
| ch10 cc56 | fila 2, col 7 | `/project1/select57` | channames (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc56 | fila 2, col 7 | `/project1/select57` | renamefrom (valor) | `ch10ctrl21 ch10ctrl22 ch10ctrl23 ch10ctrl24 ch10ctrl25 ch10ctrl26 ch10ctrl27 ch10ctrl28 ch` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | channames (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc102 | ? | `/project1/select51` | renamefrom (valor) | `ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ctrl102 ch10ct` |
| ch10 cc116 | ? | `/project1/select59` | channames (valor) | `ch10ctrl116` |
| ch11 cc21 | fila 1, col 2 | `/project1/select60` | channames (valor) | `ch11ctrl21` |