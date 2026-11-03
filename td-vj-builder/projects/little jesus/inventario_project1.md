# Inventario de /project1

## Entradas desde /project2

- `math30` (mathCHOP): gain bind `op('/project2/base17/escena_modular').par.Gain`
- `select2` (selectTOP): top→`../project2/null28`
- `select47` (selectTOP): top→`../project2/null19`
- `select51` (selectCHOP): chops→`../project2/MIDI`
- `select55` (selectTOP): top→`../project2/base17/escena_modular/CAM_2`
- `select57` (selectCHOP): chops→`../project2/MIDI`
- `select58` (selectCHOP): chops→`../project2/MIDI`
- `select59` (selectCHOP): chops→`../project2/MIDI`

## Salidas (sin nada despues, o Window/Spout/NDI)

- `null18` (nullTOP) ← —
- `null30` (nullTOP) ← lookup2
- `ndiout1` (ndioutTOP) ← comp1
- `select47` (selectTOP) ← —

## Cadena de imagen (TOPs y COMPs)

| Operador | Tipo | Entra de | Sale a | Expresiones / referencias |
|---|---|---|---|---|
| `null18` | nullTOP | — | — |  |
| `ramp32` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp31` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp30` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp29` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp28` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp27` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp26` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp25` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `blend_switch3` | baseCOMP | ramp17, ramp18, ramp19, ramp20, ramp21, ramp22, ramp23, ramp24, ramp25, ramp26, ramp27, ramp28, ramp29, ramp30, ramp31, ramp32 | switch5 | opviewer→`./out1`; Scene=`op('null1')['kdown']` |
| `ramp24` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp23` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp22` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp21` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp20` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp19` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp18` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp17` | rampTOP | — | blend_switch3 | phase=`absTime.seconds * 0.3` |
| `ramp16` | rampTOP | — | blend_switch2 |  |
| `ramp15` | rampTOP | — | blend_switch2 |  |
| `ramp14` | rampTOP | — | blend_switch2 |  |
| `ramp13` | rampTOP | — | blend_switch2 |  |
| `ramp12` | rampTOP | — | blend_switch2 |  |
| `ramp11` | rampTOP | — | blend_switch2 |  |
| `ramp10` | rampTOP | — | blend_switch2 |  |
| `ramp9` | rampTOP | — | blend_switch2 |  |
| `blend_switch2` | baseCOMP | ramp1, ramp2, ramp3, ramp4, ramp5, ramp6, ramp7, ramp8, ramp9, ramp10, ramp11, ramp12, ramp13, ramp14, ramp15, ramp16 | switch5 | opviewer→`./out1`; Scene=`op('null1')['kdown']` |
| `ramp8` | rampTOP | — | blend_switch2 |  |
| `ramp7` | rampTOP | — | blend_switch2 |  |
| `switch5` | switchTOP | blend_switch2, blend_switch3 | base6 | index=`op('null50')['ch1n28']` |
| `ramp6` | rampTOP | — | blend_switch2 |  |
| `ramp5` | rampTOP | — | blend_switch2 |  |
| `ramp4` | rampTOP | — | blend_switch2 |  |
| `ramp3` | rampTOP | — | blend_switch2 |  |
| `base6` | baseCOMP | switch5 | lookup2 | opviewer→`./out1`; Phase bind `op('./ramp1').par.phase` |
| `ramp2` | rampTOP | — | blend_switch2 |  |
| `ramp1` | rampTOP | — | blend_switch2 |  |
| `constant3` | constantTOP | — | comp3 |  |
| `null30` | nullTOP | lookup2 | — |  |
| `comp3` | compositeTOP | constant3, null8 | switch8 |  |
| `monochrome1` | baseCOMP | select2 | switch10 | opviewer→`./out1` |
| `lookup2` | lookupTOP | feedback_HSV1, base6 | V2_COLOR, null30 |  |
| `PrismTop4` | baseCOMP | blend_switch | switch1 | opviewer→`./out1`; Resx=`me.inputs[0].width`; Resy=`me.inputs[0].height`; Rotsinphase=`absTime.seconds * 0.1`;… |
| `switch8` | switchTOP | null8, comp3 | switch12 | index=`op('trigger1')['kick']` |
| `select55` | selectTOP | — | comp1 | top→`../project2/base17/escena_modular/CAM_2` |
| `switch1` | switchTOP | null7, PrismTop4 | lumalevel1 | index=`op('null2')['ch1n25']` |
| `lumalevel1` | lumalevelTOP | switch1 | switch2, comp4 | blacklevel=`op('null6')['ch1ctrl60']` |
| `V2_COLOR` | baseCOMP | null42, lookup2 | null43 | opviewer→`./out1`; Scene=`op('null39')['ch1n13']` |
| `curcuitBending1` | baseCOMP | null43 | blend_switch | opviewer→`./out1`; Power=`op('null2')['ch1n16'].eval()`; Fx1=`op('null2')['ch1n16'].eval()`; Amount bind `op('… |
| `null43` | nullTOP | V2_COLOR | curcuitBending1 |  |
| `blend_switch` | baseCOMP | curcuitBending1 | PrismTop4, null7 | opviewer→`./out1`; Scene=`op('null50')['ch1n22']` |
| `switch2` | switchTOP | comp4, lumalevel1 | null8 |  |
| `switch10` | switchTOP | select2, monochrome1 | feedback_HSV1 | index=`op('null50')['ch1n22']` |
| `feedback_HSV1` | baseCOMP | switch10 | lookup2, null42 | opviewer→`./out1` |
| `null8` | nullTOP | switch2 | switch12, switch8, comp3 |  |
| `switch12` | switchTOP | null8, switch8 | comp1 | index=`op('null2')['ch1n23']` |
| `select2` | selectTOP | — | monochrome1, switch10 | top→`../project2/null28` |
| `null7` | nullTOP | blend_switch | switch1 |  |
| `comp1` | compositeTOP | switch12, select55 | ndiout1 |  |
| `ndiout1` | ndioutTOP | comp1 | — | fps=`me.time.rate` |
| `comp4` | compositeTOP | overlays, lumalevel1 | switch2 |  |
| `overlays` | baseCOMP | — | comp4 | opviewer→`./out1` |
| `null42` | nullTOP | feedback_HSV1 | V2_COLOR |  |
| `curcuitBending` | baseCOMP | — | — | opviewer→`./out1`; Power=`op('null2')['ch1n14'].eval()`; Amount=`op('null5')['ch1ctrl19']`; Tx=`op('null10')['… |
| `select47` | selectTOP | — | — | top→`../project2/null19` |
| `audioAnalysis` | containerCOMP | switch6 | null4 | resizecomp=`me`; repocomp=`me`; opviewer→`./out1`; Low=`op('./low_')[0]`; Mid=`op('./mid_')[0]`; High=`op('./h… |

## Otros operadores (conteo)

- selectCHOP: 57
- nullCHOP: 50
- tableDAT: 36
- mathCHOP: 32
- limitCHOP: 16
- logicCHOP: 16
- countCHOP: 13
- textDAT: 5
- keyboardinCHOP: 5
- midiinCHOP: 3
- oscoutCHOP: 3
- switchCHOP: 2
- constantCHOP: 2
- lfoCHOP: 1
- mergeCHOP: 1
- renameCHOP: 1
- expressionCHOP: 1
- triggerCHOP: 1
- audiodeviceinCHOP: 1

## PrismTop4

- Tipo: baseCOMP · entra de: /project1/blend_switch · sale a: /project1/switch1
- Hacia atras: blend_switch (baseCOMP) ← curcuitBending1 (baseCOMP) ← null43 (nullTOP) ← V2_COLOR (baseCOMP) ← null42 (nullTOP) ← feedback_HSV1 (baseCOMP)

| Pestaña | Parametro | Etiqueta | Valor | Rango | Modo |
|---|---|---|---|---|---|
| Custom | Resx | Res | 1920.0 | 0.0..1.0 | expr `me.inputs[0].width` |
| Custom | Resy | Res | 1080.0 | 0.0..1.0 | expr `me.inputs[0].height` |
| Custom | Blendop | Blend Operation | add |  |  |
| Custom | Fit | Fit | fitbest |  |  |
| Custom | Tx | Translate | 0.0 | 0.0..1.0 |  |
| Custom | Ty | Translate | 0.0 | 0.0..1.0 |  |
| Custom | Scale | Scale | 0.55 | 0.0..2.0 |  |
| Custom | R | Rotate | 0.0 | 0.0..360.0 |  |
| Custom | Sides | Sides | 3 | 3.0..40.0 |  |
| Custom | Softness | Softness | 0.2 | 0.0..0.2 |  |
| Custom | Rotsinamp | Rot Sin Amp | 1.0 | 0.0..1.0 |  |
| Custom | Rotsinphase | Rot Sin Phase | 102.49000000000001 | 0.0..1.0 | expr `absTime.seconds * 0.1` |
| Patterns | Middlescale | Middle Scale | 0.0 | 0.0..1.0 |  |
| Patterns | Opacity | Input Under | 1.0 | 0.0..1.0 |  |
| Patterns | Pattern | Pattern | 0 |  |  |
| Patterns | Pattern0instances | Instances | 4 | 1.0..15.0 | expr `op('null15')['ch1ctrl18']` |
| Patterns | Pattern0radius | Radius | 2.5899999141693115 | 0.0..4.0 | expr `op('null19')['ch1ctrl22']` |
| Patterns | Pattern0amp | Instance Scale | 3.009999990463257 | 0.0..3.0 | expr `op('null23')['ch1ctrl26']` |
| Patterns | Pattern0phase | Phase | 10.249 | 0.0..1.0 | expr `((me.curBlock.index/me.curBlock.sequence.numBlocks) + … |
| Patterns | Pattern0alpha | Alpha | 0.5399999618530273 | 0.0..1.0 | expr `op('null35')['ch1ctrl30']` |
| Patterns | Pattern1instances | Instances | 10 | 1.0..15.0 |  |
| Patterns | Pattern1radius | Radius | 2.9 | 0.0..4.0 |  |
| Patterns | Pattern1amp | Instance Scale | 1.85 | 0.0..3.0 |  |
| Patterns | Pattern1phase | Phase | 0.436 | 0.0..1.0 |  |
| Patterns | Pattern1alpha | Alpha | 0.62 | 0.0..1.0 |  |
| Chroma | Layers | Layers | 30 | 0.0..30.0 |  |
| Chroma | Chromatic | Chromatic | -0.89 | -1.0..1.0 |  |
| Chroma | Distortion | Distortion | 0.36 | -1.0..1.0 |  |