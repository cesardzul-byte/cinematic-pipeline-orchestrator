---
id: manhwa-vivid
type: style
version: 1.0.0
reference: "Ilustración manhwa de contorno grueso, color vivo y sombreado duro"
anchor_language: en
palette_policy: full-color
exports:
  - STYLE_ANCHORS
  - STYLE_MOTION
  - STYLE_COMPOSITION
  - STYLE_NEGATIVES
  - STYLE_NEGATIVE_FALLBACK
---

# Style Guide: Manhwa Vivid

> Este archivo define **solo el render**: medio, línea, color, sombreado, luz y movimiento.
> No describe a ningún personaje. Para cambiar de estética, se reemplaza este archivo por otro que cumpla el *Swap Contract*.

## Style Anchors

<!-- BEGIN STYLE_ANCHORS -->
```text
Bold modern manhwa illustration with thick, confident black ink outlines and sharp tapered strokes. Vivid, saturated colors in flat cel shading with hard-edged shadows, plus rough sketch hatching on fabric folds. High contrast with crisp white rim light along the silhouette. Clean, energetic, hand-inked finish.
```
<!-- END STYLE_ANCHORS -->

## Style Motion (solo video)

<!-- BEGIN STYLE_MOTION -->
```text
Dynamic hand-drawn motion: hair and fabric whip in sharp, sweeping shapes. Outlines, hatching and colors stay consistent from frame to frame.
```
<!-- END STYLE_MOTION -->

## Composition Defaults (opcional)

Por defecto, el compilador solo lo incluye cuando la toma no define `setting`.

<!-- BEGIN STYLE_COMPOSITION -->
```text
Heroic low-angle framing that makes the figure loom large, strong backlight, soft pale-blue gradient background with a few scattered paint-splatter dots.
```
<!-- END STYLE_COMPOSITION -->

## Palette

Los valores hex son para referencia humana y para el etalonaje. **No se pegan en prompts.**

| Rol | Hex | Uso |
|---|---|---|
| Tinta | `#0B0B0D` | Contornos y rellenos negros |
| Blanco | `#FFFFFF` | Luz de contorno y brillos |
| Azul pálido | `#C9D6E3` | Fondos en degradado |

## Color Policy (`full-color`)

- Los colores del personaje se renderizan con toda su saturación.
- El contraste lo dan los contornos negros gruesos y la luz de contorno blanca.
- Esta política se aplica únicamente a través del texto de `STYLE_ANCHORS`. El compilador no lee `palette_policy`.

## Style Negatives

Solo se usan en modelos con campo de prompt negativo.

<!-- BEGIN STYLE_NEGATIVES -->
```text
photorealistic, photograph, 3D render, CGI, painterly brushstrokes, watercolor, oil painting, charcoal sketch, soft blurry shading, muted colors, desaturated palette, sepia, glossy airbrushing, lens flare, chibi, super-deformed, western cartoon, comic panels, speech bubbles, sound effects, text, watermark, signature, logo, blurry face, extra fingers, fused fingers, deformed hands, extra limbs, flickering, frame jitter, line boil, morphing textures, inconsistent line weight
```
<!-- END STYLE_NEGATIVES -->

En modelos **sin campo negativo**, el compilador añade este bloque al final del prompt positivo:

<!-- BEGIN STYLE_NEGATIVE_FALLBACK -->
```text
A hand-drawn 2D manhwa illustration with bold ink outlines and vivid flat colors in every frame.
```
<!-- END STYLE_NEGATIVE_FALLBACK -->

## Swap Contract

Cualquier estilo alternativo debe cumplir esto:

1. **Bloques.**
   - Obligatorios: `STYLE_ANCHORS` y `STYLE_NEGATIVES`.
   - Obligatorio para modelos de video: `STYLE_MOTION`.
   - Opcionales: `STYLE_COMPOSITION` y `STYLE_NEGATIVE_FALLBACK`.
   - Todo bloque presente debe figurar en `exports`, y viceversa. El compilador lo verifica.
2. **No describir a ningún personaje**: ni rasgos, ni cabello, ni ropa, ni colores de vestuario.
3. **Declarar `palette_policy`** como documentación. La política real tiene que estar escrita en `STYLE_ANCHORS`.
4. **Conservar los negativos de artefactos** (manos, flicker, morphing). Esos son universales, no estéticos.