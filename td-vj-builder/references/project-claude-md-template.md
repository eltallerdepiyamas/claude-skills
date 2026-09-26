# Plantilla de CLAUDE.md por proyecto

El skill escribe/actualiza este archivo en la carpeta del proyecto del show (junto
al `.toe`) cada vez que construye algo. Es el contexto en disco para ese show, para
no re-preguntar cada sesión. NO confundir con el CLAUDE.md de arquitectura del patch.

Al construir, el skill:
1. Si no existe `CLAUDE.md` en la carpeta del proyecto → lo crea con esta estructura.
2. Si ya existe → actualiza la tabla de bases ocupadas y la fecha, sin borrar notas
   que el usuario haya agregado a mano (append/merge, no overwrite ciego).

---

```markdown
# PROYECTO: <ARTISTA> — <VENUE/FECHA>

Generado por td-vj-builder. Contexto en disco para este show.

## Rutas (verificar que coincidan con esta máquina)
- Proyecto .toe: <ruta de project.folder>
- Shaders de efectos:  effects_glsl/shaders/
- Shaders de visuales: visuals_glsl/shaders/
- Shaders de layouts:  layouts_glsl/shaders/
- Audio canónico (CHOPs del audio_in): ../../project1/null4  (canales: low mid high)

## Rig (fijo — no renombrar bases)
- Visuales:  base1–base16
- base17:    host de cámaras / escena_modular / layouts (layout_*)
- Efectos:   base18–base24, luego base38–base45
- GLSL output resolution: Use Input (el efecto hereda el tamaño del input)

## Bases ocupadas en este show
| Base | Categoría | Nombre | Shader | Feedback | Notas |
|------|-----------|--------|--------|----------|-------|
| base18 | efecto | neon_bleed | effects_glsl/shaders/neon_bleed.frag | sí | — |
| base19 | efecto | pulse_grid | effects_glsl/shaders/pulse_grid.frag | sí | — |

## Layouts en este show (dentro de base17/escena_modular)
| Nombre | Cámaras | Notas |
|--------|---------|-------|
| (ninguno aún) | | |

## Contrato de parámetros (recordatorio)
- 5 sliders por rol: intensidad, velocidad, distorsión, color, firma.
- Bypass aparte. Página Audio: Audioreact + Low/Mid/High + Audiotarget + Audiomult.
- Audio se suma en la expresión del uniform (clamp), no en el slider.

## Cómo correr un builder
Cargar el setup_baseXX_<name>.py en un Text DAT dentro del baseXX → Run.
(O exec(open(...).read()) desde el Textport.)

## Notas del show (libre — el skill no borra esto)
- 
```

---

## Reglas de actualización para el skill

- El skill SIEMPRE confirma con el usuario antes de sobrescribir; para `CLAUDE.md`
  el merge es seguro (actualiza tabla + fecha, preserva "Notas del show").
- Las rutas se escriben a partir de `project.folder` real, no hardcoded.
- Si el usuario corre en una carpeta nueva (otro artista), se crea un CLAUDE.md nuevo
  ahí; no se mezcla con el de otro show.
