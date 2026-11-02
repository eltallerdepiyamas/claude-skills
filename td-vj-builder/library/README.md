# library/ — shaders reutilizables

Shaders que funcionaron en proyectos pasados, guardados para reusar o adaptar.
El skill revisa esta carpeta ANTES de escribir un shader nuevo: si hay algo cercano
al mood pedido, parte de eso en vez de empezar de cero.

Organiza por categoría:
- visuals/   (generativos, snake_case, u_color1/2/3)
- effects/   (circuito cerrado, camelCase, sTD2DInputs[0..1])
- layouts/   (multi-cámara, sTD2DInputs[0..4])

Nombra describiendo el look, no el proyecto (ej. effects/ghost_trail.frag,
visuals/neon_grid.glsl). Cuando muevas uno aquí, anota en LEARNINGS.md de qué
proyecto salió y qué rangos quedaron buenos.

## Índice

_Origen de cada archivo. Antes de escribir un shader nuevo, busca aquí algo cercano y adáptalo._

### visuals/ (42)

| Archivo | Proyecto |
|---|---|
| `bauhaus_ml.glsl` | mercado libre |
| `campo_bokeh.glsl` | petite amie |
| `code_rain.glsl` | corona |
| `cuadritos.glsl` | mercado libre |
| `cuerdas.glsl` | petite amie |
| `data_barcode.glsl` | corona |
| `datamatics.glsl` | corona |
| `destellos.glsl` | mercado libre |
| `dot_matrix.glsl` | corona |
| `dot_wave.glsl` | corona |
| `eclipse.glsl` | petite amie |
| `eclipse_field.glsl` | mercado libre |
| `envios_network.glsl` | mercado libre |
| `esferas.glsl` | mercado libre |
| `estela.glsl` | mercado libre |
| `floor_presence.glsl` | mercado libre |
| `flow_field.glsl` | mercado libre |
| `grano_degradado.glsl` | petite amie |
| `grid_tunnel.glsl` | corona |
| `hud_detection.glsl` | mercado libre |
| `humo_tinta.glsl` | petite amie |
| `industrial_grid.glsl` | corona |
| `kick_blocks.glsl` | corona |
| `liquid_light.glsl` | petite amie |
| `mareas_color.glsl` | petite amie |
| `matrix_pulse.glsl` | mercado libre |
| `module_grid.glsl` | corona |
| `niebla_capas.glsl` | petite amie |
| `ondas.glsl` | mercado libre |
| `op_sphere.glsl` | mercado libre |
| `ovalos.glsl` | mercado libre |
| `piso_amarillo.glsl` | mercado libre |
| `radar_sweep.glsl` | corona |
| `ring_chase.glsl` | corona |
| `ring_matrix.glsl` | corona |
| `scanner.glsl` | corona |
| `shingle_wall.glsl` | corona |
| `splashes.glsl` | mercado libre |
| `tier_pulse.glsl` | corona |
| `tile_constellation.glsl` | corona |
| `tower_climb.glsl` | corona |
| `warp_burst.glsl` | corona |

### effects/ (25)

| Archivo | Proyecto |
|---|---|
| `01_liquid_light_show.frag` | apf |
| `02_crt_edge_bleed.frag` | apf |
| `03_geometric_mandelwarp.frag` | apf |
| `04_scanline_interference.frag` | apf |
| `05_color_cycle_solarize.frag` | apf |
| `anamorph_ghost.frag` | petite amie |
| `breath_zoom.frag` | petite amie |
| `chromatic_split.glsl` | little jesus |
| `crt_edge_bleed.frag` | petite amie |
| `crt_pvm.frag` | ed maverick |
| `displacement_wave.glsl` | little jesus |
| `dos_voces.frag` | petite amie |
| `echo_fractal.frag` | petite amie |
| `eco_lento.frag` | petite amie |
| `invert_pulse.glsl` | little jesus |
| `liquid_light_show.frag` | petite amie |
| `liquid_memory.frag` | petite amie |
| `memory_marbling.frag` | petite amie |
| `nucleo_frio.frag` | petite amie |
| `plasma_currents.frag` | petite amie |
| `retrato_focal.frag` | petite amie |
| `rgb_trail_decay.frag` | petite amie |
| `signal_bend.frag` | ed maverick |
| `soft_halate.frag` | petite amie |
| `spectral_mitosis.frag` | petite amie |

### layouts/ (35)

| Archivo | Proyecto |
|---|---|
| `layout_bloom.frag` | little jesus |
| `layout_breathing_grid.frag` | little jesus |
| `layout_carousel.frag` | little jesus |
| `layout_float_chaos.frag` | little jesus |
| `layout_floating_pieces.frag` | little jesus |
| `layout_focus_blur.frag` | little jesus |
| `layout_grid_wave.frag` | little jesus |
| `layout_gridwall.frag` | little jesus |
| `layout_gridwall_drift.frag` | little jesus |
| `layout_kaleidoscope.frag` | little jesus |
| `layout_magnetic_pull.frag` | little jesus |
| `layout_orbit_dance.frag` | little jesus |
| `layout_pendulum.frag` | little jesus |
| `layout_pip.frag` | little jesus |
| `layout_rand_bend.frag` | little jesus |
| `layout_rand_collage.frag` | little jesus |
| `layout_rand_drift.frag` | little jesus |
| `layout_rand_flow.frag` | little jesus |
| `layout_rand_h.frag` | little jesus |
| `layout_rand_morph.frag` | little jesus |
| `layout_rand_offset.frag` | little jesus |
| `layout_rand_orbit.frag` | little jesus |
| `layout_rand_pulse.frag` | little jesus |
| `layout_rand_split.frag` | little jesus |
| `layout_rand_stair.frag` | little jesus |
| `layout_rand_swing.frag` | little jesus |
| `layout_rand_v.frag` | little jesus |
| `layout_rand_wave.frag` | little jesus |
| `layout_ripple_grid.frag` | little jesus |
| `layout_shuffle_grid.frag` | little jesus |
| `layout_split_asimetrico.frag` | little jesus |
| `layout_stack_vertical.frag` | little jesus |
| `layout_swarm.frag` | little jesus |
| `layout_tunnel_zoom.frag` | little jesus |
| `layout_wave_scroll.frag` | little jesus |

### tracking/ (5)

| Archivo | Proyecto |
|---|---|
| `blob_tracker_callbacks.py` | mercado libre |
| `hub_blob_view_callbacks.py` | mercado libre |
| `tdvj_core_tracking.py` | mercado libre |
| `tracker_view_callbacks.py` | mercado libre |
| `tracking_hub_callbacks.py` | mercado libre |

Notas:
- `effects/01_…05_*.frag` son el set APF original; `petite amie` tiene versiones extendidas de `liquid_light_show` y `crt_edge_bleed` (más uniforms para llenar los 5 slots).
- `layouts/` son los layouts CCTV de Little Jesus (`sTD2DInputs[0..4]`, `uCamfit`, `uCamCount`).
- `tracking/` = tracking Hokuyo/blobs de ON TOUR x Mercado Libre, con su variante del núcleo (`tdvj_core_tracking.py`).
