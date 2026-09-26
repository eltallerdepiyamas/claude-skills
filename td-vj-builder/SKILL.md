---
name: td-vj-builder
description: Build TouchDesigner VJ content for live shows — generative visuals, live-camera effects/filters, and multi-camera CCTV layouts — by writing GLSL shaders and the Python setup scripts that construct each network inside the existing baseXX containers of /project2. Use this skill whenever the user wants to create, design, or generate VJ visuals, camera effects, camera filters, feedback effects, or camera layouts for TouchDesigner; whenever they mention base17/escena_modular, a "midisampler" rig, a setup_baseXX script, or a project research .md to turn into effects; or whenever they reference this TouchDesigner VJ rig. Build content even when the user only describes a mood, an artist, or a show rather than asking for "a shader" explicitly.
---

# TD VJ Builder

This skill builds TouchDesigner content for a live VJ rig. It writes two artifacts per item: a GLSL shader (`.glsl`/`.frag`) and a Python builder (`setup_baseXX_<name>.py`) that the user loads into a Text DAT inside the target container and runs. The skill never operates TouchDesigner directly — it produces files.

The rig is fixed and the skill must respect it exactly. A MIDI sampler maps physical controls to parameters by base number, so **base numbers and the parameter contract are load-bearing — never rename a baseX and never deviate from the 5-slider contract.**

## The rig (memorize this)

```
/project2
  ├── base1 … base16          → VISUALES (generative GLSL content)
  ├── base17                  → camera-layout host; contains escena_modular
  │     └── escena_modular
  │           ├── CAM_1 … CAM_5   (Video Device In TOPs)
  │           ├── switch1          (active camera/layout output)
  │           ├── audio_in         (CHOP with channels: low mid high  + others)
  │           └── layout_*         → CCTV LAYOUTS live here as Base COMPs
  ├── base18 … base24         → EFECTOS / FILTROS (closed-circuit camera FX)
  └── base38 … base45         → EFECTOS / FILTROS (continuation; respect the jump)
```

Signal for an effect: `base17/switch1` (live camera mix) → `baseXX` (effect) → out. Resolution always comes from `escena_modular` (`ResW`/`ResH`) — never hardcode.

## The three modes

When invoked for a new project, **ask which modes are needed** before building:

1. **Visuales** (base1–16): self-contained generative shaders, optionally audio-reactive, optionally mixing a video input. Convention: `u_time`, `u_res`, `u_bass`, `u_color1/2/3`, plus the effect's own `u_*` uniforms; `#define u_input sTD2DInputs[0]`.
2. **Efectos / filtros** (base18–24, then base38–45): process the live camera feed from `base17/switch1`. Convention: `uTime`, `uResolution`, `texture(sTD2DInputs[0], vUV.st)`, `TDOutputSwizzle(...)`, optional `feedbackTOP` loop on input 1.
3. **Layouts CCTV** (`layout_*` inside `base17/escena_modular`): GLSL-multi shaders that arrange 2–5 cameras. Cameras are `sTD2DInputs[0..4]` — never `uniform sampler2D`.

For **visuales specifically, always ask: "¿generativos puros o mezclan un input de video?"** — it decides whether the builder wires a source into `sTD2DInputs[0]` and whether `u_input` is used.

## Workflow

1. **Ask which modes** are needed (visuales / efectos / layouts / combinación).
2. **Read the project research `.md`** (see `references/research-prompt.md` for the prompt the user runs to generate it). Ask for it if not provided. It carries mood, palette, camera context, audio character, and a per-item list already shaped to the 5-slot contract.
3. **Read `LEARNINGS.md`** (in the skill folder) before proposing — it accumulates what worked in past projects. Then **check `library/`** for existing shaders to reuse or adapt before writing from scratch.
4. **Propose** what to build per category and confirm with the user.
5. **Auto-assign base numbers** by category, in order, filling the lowest free slots (assume a fresh project unless told otherwise; the user may override with "este en base20"). Visuales 1→16; efectos 18→24 then 38→45; layouts are named `layout_<name>`, not numbered.
6. For each approved item: **write the shader** (reuse from `library/` when possible), then **generate the builder** from the matching template in `templates/`. Save shaders and builders to `/mnt/user-data/outputs/`.
7. **After the project**, append a dated entry to `LEARNINGS.md` and copy any shader worth reusing into `library/`. Archive the research `.md` + what was built under `projects/`. (See "Learning loop" below.)

## Per-project CLAUDE.md (automatic)

Whenever the skill builds anything, it writes or updates a `CLAUDE.md` in the project folder (next to the `.toe`) — the on-disk context for that show, so sessions don't re-ask. Use `references/project-claude-md-template.md` as the structure. Behaviour:
- If no `CLAUDE.md` exists in the project folder → create it from the template, filling real paths (from `project.folder`), the rig ranges, and a table of the bases just occupied.
- If it exists → merge: refresh the bases/layouts tables and the date, and NEVER erase the user's "Notas del show" section. Surface the write to the user.
- This is separate from the patch's architecture CLAUDE.md (which describes `/project2`); this one is per-show working context.

## The parameter contract (every baseXX gets this)

This is what makes one set of MIDI knobs control every effect. On the **root of each baseXX** (page `Filter` for effects, `Visual` for visuals), create:

**Five float sliders, in fixed role order**, named after the real uniform they drive, with the parameter's real range (not normalized). The MIDI knob assigned to a slot must mean the same thing across every effect, so order by role, not by importance:

1. **Intensity / amount** — the effect's overall presence
2. **Speed / time** — animation/motion rate
3. **Distortion / spatial deformation**
4. **Color / chroma**
5. **Signature** — the single most characteristic control of *that* effect

If an effect lacks a natural fit for a slot (e.g. no color control), put the next most expressive parameter there and note it in a comment. Never leave a slot empty.

**On/off, separate from the 5:** a `Bypass` toggle (the `switch1`/`cross` wet–dry that the user liked from the feedback effects). Bypass is not one of the five sliders.

**Audio page** (separate custom page `Audio`) on every baseXX:
- `Audioreact` — master toggle (toggle).
- `Low`, `Mid`, `High` — band toggles that **sum** (any combination).
- `Audiotarget` — menu choosing which of the 5 sliders the audio energy pushes.
- `Audiomult` — float slider 0–3, local intensity (per-base; never edit the source so other effects stay put).

The audio energy is summed in the **uniform's expression**, not on the slider, so the slider stays fully MIDI-mappable. Pattern:
```
energy = (op('audio_in')['low']*Low + op('audio_in')['mid']*Mid + op('audio_in')['high']*High) * Audiomult * Audioreact
driven_uniform = clamp(parent().par.<slot> + (energy if Audiotarget==slot else 0), <min>, <max>)
```
The `audio_in` is a single Select CHOP in the base, `Channel Names = low mid high`, CHOPs = `../../project1/null4` (the rig's canonical audio-analysis source; relative path from the baseXX). One select gives all three bands; selecting bands is by name in the expression, not by extra nodes.

## Templates

Read the matching template fully before generating a builder — they encode the exact node graph, the idempotent clear/rebuild pattern, and TD-version-tolerant parameter probing:

- `templates/visual_builder.py` — generative visual (base1–16).
- `templates/image_player_builder.py` — image/logo player for visuals (base1–16): loads a **folder** of images (PNGs exported from SVGs, logos, stills) via a Movie File In TOP, switches between them live with the `Imageindex` slider, and applies a GLSL treatment (Klein tint, white/black strobe, stripes, scale). Companion shader `templates/logo_player.glsl`. Use this whenever the user wants visuals driven by their own imagery rather than pure procedural geometry. **SVGs must be rasterized to transparent PNG first** (TD TOPs can't load .svg); tell the user to export at ~2048px and drop them in the image folder — adding an image later needs no code. Same 5-slider + Bypass + Audio contract.
- `templates/effect_builder.py` — closed-circuit camera effect/filter (base18–24, base38–45), with optional feedback loop.
- `templates/layout_builder.py` — CCTV multi-camera layout (`layout_*` inside escena_modular).
- `templates/common_vertex.vert` — pass-through vertex shader for GLSL TOPs that need one.

Each builder ends with a `run()` call and a path-fallback list (`/baseXX`, `/project2/baseXX`) so it works from a Text DAT regardless of where it's executed. Builders are idempotent: snapshot params → destroy managed children → rebuild → restore.

## Writing shaders

**Shader and parameters are one synchronized pair — generate them together, never apart.** Every uniform the `.frag` declares must have a matching Custom Parameter created on the base (in `FIVE_SLOTS`, `SIGNATURE_EXTRAS`, or `COLOR_UNIFORMS`), and every parameter must map to a real uniform. A uniform whose expression references `parent().par.X` where `X` wasn't created triggers a cook-time error (`ParCollection object has no attribute 'X'`) and the effect fails. After writing a shader, list its uniforms and confirm each one is created and bound; the builders also guard at build time — `_bind_uniform` skips and prints a `[WARN]` naming the missing parameter instead of letting TD throw, so a mismatch is visible and recoverable rather than fatal.


When writing a new shader, follow the convention of its category (above) and study `references/shader-conventions.md` for the shared helpers, the audio-reactivity pattern, and the do/don't list distilled from the user's existing corpus. Keep effects real-time at 1080p/60fps: few texture fetches, no heavy loops, 16-bit float feedback. For camera effects, **the camera must stay legible** — keep the wet/dry and portrait-safe ranges sane; don't turn the feed into unrecognizable abstraction.

**Lean on the sibling TouchDesigner skills for syntax.** If skills like `td-glsl`, `td-glsl-vertex`, or `td-pops` are installed, consult them to verify TouchDesigner GLSL syntax, built-in functions (`TDOutputSwizzle`, `TDPos`, `sTD2DInputs`, etc.), and node/parameter APIs before writing a new shader — they are the authoritative reference for TD conventions and prevent guessing. They do not change the nomenclature this skill already uses; they confirm it. This mirrors how these effects were originally authored (the user's own prompts said "use the TouchDesigner GLSL skills as reference for APIs and conventions").

## Hard rules

- Never rename, move, or destroy a `baseX` COMP. Only manage children inside it.
- Respect base-number ranges per category and the base38–45 jump. The MIDI sampler depends on it.
- Exactly 5 role-ordered sliders + separate `Bypass` + `Audio` page on every baseXX.
- GLSL output resolution defaults to **Use Input** (the effect inherits the incoming video size; change size at the source). `uResolution` is bound to the GLSL TOP's own `me.width`/`me.height` so it always matches.
- Layout cameras via `sTD2DInputs[index]`, never `uniform sampler2D`.
- **Every GLSL TOP must assign ALL uniforms the shader declares on its Vectors page** — TD prints "Uniform 'X' is not assigned" warnings and the effect renders flat/black if any are missing. In particular, effects almost always declare `uTime` (→ `absTime.seconds`) and `uResolution` (→ `escena_modular` `ResW`/`ResH`); the templates bind these as the first two uniforms, before the macros. Putting resolution on `escena_modular` means one place controls every base's resolution.
- Produce files to `/mnt/user-data/outputs/`; never claim to have run TouchDesigner.

## Learning loop

A skill folder doesn't retrain itself, but it improves by accumulation, and this skill is built to do that honestly:
- `LEARNINGS.md` — append-only log. Read before proposing; write after finishing. Record good ranges, names the user kept, what broke and the fix.
- `library/` — shaders that worked, saved for reuse/adaptation in later projects.
- `projects/` — archived research `.md` + a short manifest of what was built, so the user can say "hazme algo como el de Alan" and the precedent exists.

Always surface these writes to the user rather than doing them silently; the user approves what gets saved.
