# LEARNINGS — TD Flyer Audioreactivo

Registro append-only. Lee esto antes de proponer; escribe aquí al cerrar cada flyer.
Anota rangos que se sintieron bien, nombres que el usuario conservó, qué se rompió y
cómo se arregló. El usuario aprueba cada escritura.

Formato por entrada:
## YYYY-MM-DD — <flyer / evento>
- Construido: <efectos y destino: loop / vivo>
- Rangos que funcionaron: ...
- Nombres/convenciones que el usuario conservó o cambió: ...
- Problemas y fixes: ...
- Shaders movidos a library/: ...

---

## (semilla) Convenciones confirmadas con el usuario
- Workflow SEPARADO del rig (td-vj-builder): contenedor propio, sin baseXX/project2/MIDI.
- Audio reactivo, ruteo por efecto (menú de banda + amount), no Audiotarget único.
- Audio sumado en la expresión del parámetro, no en el slider (el slider sigue arrastrable).
- Builder idempotente; tolerancia de versión con _set_par/_set_menu probando varios nombres.

## 2026-06-02 — Tarabeva (story vertical, house/punk)
- Construido: boil + feedback trail + chroma split, reactivo en vivo (3 bandas).
- Rangos que funcionaron: Boilamt ~0.01, Boilscale ~4, Trailzoom 1.01, Traildecay ~0.88,
  Chromaamt ~2 base con empuje de audio alto en agudos. gain de audio = 20 de arranque.
- Convenciones que nacieron aquí: páginas custom 'Flyer' (base) y 'Audio' (Audioreact,
  Audiosmooth, *source + *audio por efecto). Defaults: boil←Mid, estela←Low, chroma←High.
- Problemas y fixes:
  - `cos`/`sin` en expresiones de TD dan NameError → usar `math.cos`/`math.sin`.
  - Feedback TOP de esta versión: se alimenta por **Target TOP** (escrito, no arrastrado)
    con el **input vacío**. Arrastrar el comp al input → "Cook dependency loop detected".
    Sin target ni input → "Not enough sources specified". El patrón correcto salió del
    effect_builder del rig (Target TOP con fallback de nombres top/targetop/target).
  - Nombres de parámetro varían por versión (displace weight, transform scale, audiofilter
    cutoff, analyze function) → setear probando varios candidatos.
- Shaders movidos a library/: shaders/chroma_split.glsl (RGB split loop-safe con wobble).
- Decisión: fue reactivo en vivo; el loop perfecto para export quedó como paso futuro.
