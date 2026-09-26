# Research — Casino Marquee (visuales generativas)

## Concepto
Gráficos planos y contundentes salidos de una **marquesina de casino de Las Vegas, ~1970**.
Minimalistas en detalle, maximalistas en impacto. Cada forma está **definida por un contorno
de bombillas encendidas**. Nítido, sin degradados ni texturas: solo colores sólidos de alto
contraste, pensados para bajar limpio a una **matriz de LEDs (panel grande)**.

## Lenguaje visual (fundamento)
- **Bombilla incandescente en secuencia (chase).** Las marquesinas usaban circuitos temporizados
  para parpadeo, destello y encendido secuencial: iluminar secciones en orden simula movimiento.
  Es el corazón de cada pieza.
- **Starburst atómico / Googie.** La forma radiante de la era atómica (Space Age) aparecía
  constantemente en la señalización; se asocia a la arquitectura Googie.
- **Íconos animados.** Flechas que apuntan, dados, ruedas que giran, letras en cascada.
- **Plano y de alto contraste.** Fondo casi negro, bombillas saturadas. Legible de lejos y
  a baja resolución (matriz).

## Paleta
| Rol | Color | Hex aprox | Uniform |
|-----|-------|-----------|---------|
| A | Oro | `#FFB800` | `u_color1` (`Colora`) |
| B | Rojo | `#F21A33` | `u_color2` (`Colorb`) |
| C | Azul eléctrico | `#0A85FF` | `u_color3` (`Colorc`) |

Los tres se exponen como pickers RGB en cada base; `u_colormix` navega la paleta.

## Salida
Panel LED grande. Resolución tomada de `escena_modular` (`ResW`/`ResH`) con fallback 1920×1080.
Diseño chunky a propósito para que cada bombilla se lea como pixel.

## Audio
Contrato estándar: `audio_in` (Select CHOP, `low mid high`) desde `project1/null4`.
Página Audio por base: `Audioreact`, toggles `Low/Mid/High` que suman, `Audiotarget`
(a cuál de los 5 sliders empuja la energía) y `Audiomult`. Default sugerido: energía → `Speed`
(el chase late con la música).

## Catálogo — batch 1 (base1–7)
Cada pieza: contrato de 5 sliders en orden de rol
(1 Intensidad · 2 Speed · 3 Distort · 4 Color Mix · 5 Signature) + Bypass.

| Base | Pieza | Qué es | Signature (slider 5) |
|------|-------|--------|----------------------|
| 1 | `marquee_frame` | Marco rectangular de bombillas con chase en el perímetro | `Density` (bombillas) |
| 2 | `atomic_starburst` | Sunburst de rayos de bulbos pulsando desde el centro | `Rays` |
| 3 | `bulb_arrow` | Flecha de bombillas con blink secuencial, rotable | `Direction` (grados) |
| 4 | `dot_matrix_field` | Campo/retícula de bulbos con olas on/off (lo más "matriz") | `Density` (celdas) |
| 5 | `spin_ring` | Anillos concéntricos girando en cascada (rueda/ruleta) | `Rings` |
| 6 | `chevron_march` | Galones de bulbos marchando (luces de pista direccionales) | `Count` |
| 7 | `circulos` | Círculos concéntricos pulsando hacia afuera (ripple/diana) | `Rings` |

## Notas de implementación
- GLSL puro (sin Container), samplers vía `sTD2DInputs` (no aplican aquí por ser generativos).
- Sin indexado dinámico de arrays; los loops (aristas del marco, segmentos de la flecha) usan
  posiciones calculadas, no indexado de array.
- Todos los uniforms se asignan en la página **Vectors** del GLSL TOP.
- `bgtop = ./out1` en cada base para el thumbnail.
- Deformación (`Distort`) con tope bajo: la forma siempre se mantiene legible.
