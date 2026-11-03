# Mapa de knobs del MIDImix

## MIDI In en el proyecto

- `/project1/midiin1` (midiinCHOP)
- `/project1/midiin2` (midiinCHOP)
- `/project1/midiin3` (midiinCHOP)
- `/project2/MIDI` (midiinCHOP)

## Quien lee cada CC

| CC | Posicion | Operador | Donde | Texto |
|---|---|---|---|---|
| ch1 cc2 | ? | `/project1/select6` | channames (valor) | `ch1ctrl60 ch1n2` |
| ch1 cc4 | ? | `/project1/select11` | channames (valor) | `ch1n4` |
| ch1 cc5 | ? | `/project1/select7` | channames (valor) | `ch1ctrl61 ch1n5` |
| ch1 cc5 | ? | `/project2/base1/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base10/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base11/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base12/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base13/switch2` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base2/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base3/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base4/switch2` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base5/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base6/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc5 | ? | `/project2/base9/switch1` | index (expr) | `op('/project1/null44')['ch1n5']` |
| ch1 cc7 | ? | `/project1/select18` | channames (valor) | `ch1n7` |
| ch1 cc8 | ? | `/project1/select37` | channames (valor) | `ch1n8 ch1n10` |
| ch1 cc10 | ? | `/project1/select37` | channames (valor) | `ch1n8 ch1n10` |
| ch1 cc11 | ? | `/project1/select33` | channames (valor) | `ch1n11 ch1n13` |
| ch1 cc13 | ? | `/project1/V2_COLOR` | Scene (expr) | `op('null39')['ch1n13']` |
| ch1 cc13 | ? | `/project1/select33` | channames (valor) | `ch1n11 ch1n13` |
| ch1 cc14 | ? | `/project1/curcuitBending` | Power (expr) | `op('null2')['ch1n14'].eval()` |
| ch1 cc14 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc16 | ? | `/project1/curcuitBending1` | Power (expr) | `op('null2')['ch1n16'].eval()` |
| ch1 cc16 | ? | `/project1/curcuitBending1` | Fx1 (expr) | `op('null2')['ch1n16'].eval()` |
| ch1 cc16 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc17 | ? | `/project1/curcuitBending` | Fx2 (expr) | `op('null2')['ch1n17'].eval()` |
| ch1 cc17 | ? | `/project1/curcuitBending` | Fx3 (expr) | `op('null2')['ch1n17'].eval()` |
| ch1 cc17 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc19 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc20 | ? | `/project1/curcuitBending` | Fx4 (expr) | `op('null2')['ch1n20'].eval()` |
| ch1 cc20 | ? | `/project1/curcuitBending` | Fx5 (expr) | `op('null2')['ch1n20'].eval()` |
| ch1 cc20 | ? | `/project1/curcuitBending` | Scaledownres (expr) | `op('null2')['ch1n20'].eval()` |
| ch1 cc20 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc22 | ? | `/project1/blend_switch` | Scene (expr) | `op('null50')['ch1n22']` |
| ch1 cc22 | ? | `/project1/select27` | channames (valor) | `ch1ctrl46 ch1n28 ch1n22 ch1n26 ch1n27` |
| ch1 cc22 | ? | `/project1/switch10` | index (expr) | `op('null50')['ch1n22']` |
| ch1 cc23 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc23 | ? | `/project1/switch12` | index (expr) | `op('null2')['ch1n23']` |
| ch1 cc25 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc25 | ? | `/project1/switch1` | index (expr) | `op('null2')['ch1n25']` |
| ch1 cc26 | ? | `/project1/select27` | channames (valor) | `ch1ctrl46 ch1n28 ch1n22 ch1n26 ch1n27` |
| ch1 cc26 | ? | `/project1/select4` | channames (valor) | `ch1n14 ch1n17 ch1n20 ch1n16 ch1n19 ch1n23 ch1n25 ch1n26` |
| ch1 cc27 | ? | `/project1/select27` | channames (valor) | `ch1ctrl46 ch1n28 ch1n22 ch1n26 ch1n27` |
| ch1 cc28 | ? | `/project1/select27` | channames (valor) | `ch1ctrl46 ch1n28 ch1n22 ch1n26 ch1n27` |
| ch1 cc28 | ? | `/project1/switch5` | index (expr) | `op('null50')['ch1n28']` |
| ch2 cc61 | ? | `/project2/table1` | texto DAT | `ch2n61` |
| ch2 cc62 | ? | `/project2/table1` | texto DAT | `ch2n62` |
| ch2 cc63 | ? | `/project2/table1` | texto DAT | `ch2n63` |
| ch2 cc64 | ? | `/project2/table1` | texto DAT | `ch2n64` |
| ch2 cc65 | ? | `/project2/table1` | texto DAT | `ch2n65` |
| ch2 cc66 | ? | `/project2/table1` | texto DAT | `ch2n66` |
| ch2 cc67 | ? | `/project2/table1` | texto DAT | `ch2n67` |
| ch2 cc68 | ? | `/project2/table1` | texto DAT | `ch2n68` |
| ch2 cc69 | ? | `/project2/table1` | texto DAT | `ch2n69` |
| ch2 cc70 | ? | `/project2/table1` | texto DAT | `ch2n70` |
| ch2 cc71 | ? | `/project2/table1` | texto DAT | `ch2n71` |
| ch2 cc72 | ? | `/project2/table1` | texto DAT | `ch2n72` |
| ch2 cc73 | ? | `/project2/table1` | texto DAT | `ch2n73` |
| ch10 cc37 | ? | `/project2/table1` | texto DAT | `ch10n37` |
| ch10 cc38 | ? | `/project2/table1` | texto DAT | `ch10n38` |
| ch10 cc39 | ? | `/project2/table1` | texto DAT | `ch10n39` |
| ch10 cc40 | ? | `/project2/table1` | texto DAT | `ch10n40` |
| ch10 cc41 | ? | `/project2/table1` | texto DAT | `ch10n41` |
| ch10 cc42 | ? | `/project2/table1` | texto DAT | `ch10n42` |
| ch10 cc43 | ? | `/project2/table1` | texto DAT | `ch10n43` |
| ch10 cc44 | ? | `/project2/table1` | texto DAT | `ch10n44` |
| ch10 cc45 | ? | `/project2/table1` | texto DAT | `ch10n45` |
| ch10 cc46 | ? | `/project2/table1` | texto DAT | `ch10n46` |
| ch10 cc47 | ? | `/project2/table1` | texto DAT | `ch10n47` |
| ch10 cc48 | ? | `/project2/table1` | texto DAT | `ch10n48` |
| ch10 cc49 | ? | `/project2/table1` | texto DAT | `ch10n49` |
| ch10 cc50 | ? | `/project2/table1` | texto DAT | `ch10n50` |
| ch10 cc51 | ? | `/project2/table1` | texto DAT | `ch10n51` |
| ch10 cc52 | ? | `/project2/table1` | texto DAT | `ch10n52` |
| ch11 cc37 | ? | `/project2/table1` | texto DAT | `ch11n37` |
| ch11 cc38 | ? | `/project2/table1` | texto DAT | `ch11n38` |
| ch11 cc39 | ? | `/project2/table1` | texto DAT | `ch11n39` |
| ch11 cc40 | ? | `/project2/table1` | texto DAT | `ch11n40` |
| ch11 cc41 | ? | `/project2/table1` | texto DAT | `ch11n41` |
| ch11 cc42 | ? | `/project2/table1` | texto DAT | `ch11n42` |
| ch11 cc43 | ? | `/project2/table1` | texto DAT | `ch11n43` |
| ch11 cc44 | ? | `/project2/table1` | texto DAT | `ch11n44` |
| ch11 cc45 | ? | `/project2/table1` | texto DAT | `ch11n45` |
| ch11 cc46 | ? | `/project2/table1` | texto DAT | `ch11n46` |
| ch11 cc47 | ? | `/project2/table1` | texto DAT | `ch11n47` |
| ch11 cc48 | ? | `/project2/table1` | texto DAT | `ch11n48` |
| ch11 cc49 | ? | `/project2/table1` | texto DAT | `ch11n49` |
| ch11 cc50 | ? | `/project2/table1` | texto DAT | `ch11n50` |
| ch11 cc51 | ? | `/project2/table1` | texto DAT | `ch11n51` |
| ch11 cc52 | ? | `/project2/table1` | texto DAT | `ch11n52` |