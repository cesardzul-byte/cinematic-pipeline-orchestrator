---
id: oc-01
type: character
version: 0.6.0
origin: "Personaje original, sin nombre definitivo"
anchor_language: en
min_scale_medium: [POSE_EFFORTLESS]
exports:
  - CORE_IDENTITY
  - DETAIL_TIER_2
  - TIER3_HANDS
  - TIER3_WAIST
  - TIER3_HEM
  - STATE_CALM
  - STATE_BATTLE
  - MOTION_BEHAVIOR
  - POSE_EFFORTLESS
  - POSE_ADVANCE
  - POSE_STANDOFF
  - POSE_SOVEREIGN
  - CHARACTER_NEGATIVES
  - NEGATIVE_FALLBACK
reference_images:
  - 6ce91523-6f8b-45a8-b6ec-7e38ef90c384  # oc-01_manhwa-vivid_front_v2.png
  - bcd7648f-2531-4cc0-a6ad-68dbec0f824b  # oc-01_manhwa-vivid_fullbody_v2.png
---

# Character: OC-01 (sin nombre)

> Este archivo define **solo la identidad**: rostro, cuerpo, cabello, vestuario, estados y comportamiento.
> No contiene términos de medio, técnica, iluminación ni paleta. Todo eso vive en `style-guide.md`.

## Core Identity & Visual Anchors

Se pega **íntegro, sin parafrasear**, en todas las tomas. Tiene unas 105 palabras.

<!-- BEGIN CORE_IDENTITY -->
```text
A tall East Asian man in his late twenties with a calm, regal bearing of effortless power; broad-shouldered, athletic and lean. Pale skin, narrow face, sharp jaw. Straight dark brows, relaxed; deep-set, heavy-lidded dark eyes with a calm, impassive gaze. Very long, voluminous ash-gray hair in a high ponytail with a small gold ornament, long bangs framing the face. White outer robe over a deep red inner robe, wide sleeves, gold embroidery along the hems, wide red belt, steel bracers. Calf-length black mantle lined in white, draped high over his shoulders with a thick silver-gray fur collar; ornate gold-trimmed steel pauldrons show beneath it. Tall black boots.
```
<!-- END CORE_IDENTITY -->

## Detail Tiers

Los accesorios pequeños son los que más se deforman en video.

- El Tier 2 entra automáticamente según el tamaño del plano.
- El Tier 3 está dividido por zona del cuerpo y solo entra cuando la toma lo pide en `details`. Nombrar algo que queda fuera de cuadro obliga al modelo a encuadrarlo o a inventarlo.

| Tamaño de plano | Bloques |
|---|---|
| wide / full | CORE_IDENTITY |
| medium | CORE_IDENTITY + DETAIL_TIER_2 |
| close-up | CORE_IDENTITY + DETAIL_TIER_2 + los `TIER3_*` listados en `details` |
| insert | CORE_IDENTITY + los `TIER3_*` listados en `details` |

`details` solo se admite con cámara static o slow.

<!-- BEGIN DETAIL_TIER_2 -->
```text
The red inner robe's crossed collar shows at the throat beneath the white one. A few loose strands escape the ponytail at his temples. Fine gold cloud patterns are engraved on the pauldrons.
```
<!-- END DETAIL_TIER_2 -->

| Bloque | Úsalo en |
|---|---|
| `TIER3_HANDS` | Insert de las manos y los brazaletes |
| `TIER3_WAIST` | Insert del cinturón |
| `TIER3_HEM` | Insert del borde del manto |

<!-- BEGIN TIER3_HANDS -->
```text
Steel bracers engraved with gold cloud patterns; long, calloused fingers.
```
<!-- END TIER3_HANDS -->

<!-- BEGIN TIER3_WAIST -->
```text
A square gold plate buckle fastens the wide red belt.
```
<!-- END TIER3_WAIST -->

<!-- BEGIN TIER3_HEM -->
```text
Gold embroidery of clouds and mountain peaks along the mantle's lower border, white lining showing in the folds.
```
<!-- END TIER3_HEM -->

## States

Se usa **un solo** estado por toma.

<!-- BEGIN STATE_CALM -->
```text
His robes and mantle are clean and intact.
```
<!-- END STATE_CALM -->

<!-- BEGIN STATE_BATTLE -->
```text
His mantle is torn and dusty at the hem, with dark blood spatters on the white sleeves. His face stays clean and perfectly calm.
```
<!-- END STATE_BATTLE -->

## Motion Behavior (solo video)

<!-- BEGIN MOTION_BEHAVIOR -->
```text
He moves slowly and unhurriedly with effortless, regal calm; his face stays still and impassive, while his long ponytail, wide sleeves and mantle sweep around him.
```
<!-- END MOTION_BEHAVIOR -->

## Signature Poses (opcionales)

Las manos son una zona de riesgo de deformación. Por eso casi todas las poses las ocultan tras la espalda. `POSE_EFFORTLESS` solo se permite en planos medium, close-up o insert; el compilador lo impone mediante `min_scale_medium`.

<!-- BEGIN POSE_EFFORTLESS -->
```text
Standing relaxed and upright, one hand held behind his back, the other raised casually at chest height with the palm open.
```
<!-- END POSE_EFFORTLESS -->

<!-- BEGIN POSE_ADVANCE -->
```text
Walking slowly and unhurriedly toward the camera, hands clasped behind his back, the mantle swinging behind him.
```
<!-- END POSE_ADVANCE -->

<!-- BEGIN POSE_STANDOFF -->
```text
Standing upright and perfectly still, arms crossed over his chest, the mantle hanging from his shoulders.
```
<!-- END POSE_STANDOFF -->

<!-- BEGIN POSE_SOVEREIGN -->
```text
Standing tall and perfectly still, hands clasped behind his back, gazing down calmly, the mantle spread wide behind him.
```
<!-- END POSE_SOVEREIGN -->

## Negative Constraints

<!-- BEGIN CHARACTER_NEGATIVES -->
```text
smile, smirk, grin, open mouth, teeth, laughing, shouting, frown, furrowed brows, scowl, glaring, angry expression, smug expression, tense jaw, clenched fists, aggressive stance, tears, blush, makeup, beard, stubble, scars, tattoos, glowing eyes, red eyes, golden eyes, blue eyes, heterochromia, bright eye highlights, woman, female body, child, elderly, bodybuilder, oversized muscles, skinny build, short hair, hair worn down, low ponytail, black hair, white hair, blonde hair, colored hair streaks, bangs covering the eyes, topknot, bun, braids, crown, hat, hood, helmet, white fur collar, gold rope trim, braided cord trim, red mantle, cape trailing on the ground, full plate armor, breastplate, chainmail, metal gauntlets, sword, saber, spear, katana, kimono, samurai, ninja, modern clothing, neon colors, multicolored outfit, blue robe, green robe, purple robe, bare chest, face changing between frames, hair color shifting, ponytail coming undone, robe colors swapping, mantle merging with robes
```
<!-- END CHARACTER_NEGATIVES -->

Para modelos **sin campo negativo**, el compilador añade este bloque al final del prompt positivo:

<!-- BEGIN NEGATIVE_FALLBACK -->
```text
Unarmed, wearing cloth robes with light armor only on the shoulders and forearms. Calm, relaxed face with no tension; neutral closed mouth; dark matte eyes. The gray hair stays in a high ponytail, the outer robe stays white, the inner robe deep red, the mantle black and the fur collar silver-gray in every frame.
```
<!-- END NEGATIVE_FALLBACK -->

## Assembly

Esta sección describe el **orden de las partes dentro de un solo prompt**, no el orden de las tomas del video. Ese orden vive en `storyboard.json`. El compilador es la fuente de verdad.

```
POSITIVE =
    camera_directive
  + CORE_IDENTITY
  + DETAIL_TIER_2                          (medium, close-up)
  + TIER3_* listados en `details`          (close-up/insert con cámara static o slow)
  + STATE_*                                (uno; por defecto STATE_CALM)
  + POSE_*                                 (opcional)
  + action                                 (obligatoria si no hay pose)
  + setting                                (recomendado; si falta, el compilador avisa)
  + MOTION_BEHAVIOR                        (modelos de video)
  + style-guide → STYLE_ANCHORS
  + style-guide → STYLE_MOTION             (modelos de video)
  + style-guide → STYLE_COMPOSITION        (por defecto, solo si la toma no tiene setting)
  + NEGATIVE_FALLBACK
    + style-guide → STYLE_NEGATIVE_FALLBACK  (modelos sin campo negativo)

NEGATIVE (solo modelos con campo negativo) =
    CHARACTER_NEGATIVES + style-guide → STYLE_NEGATIVES
```

Reglas:

1. Los bloques se pegan **verbatim**. No se usan sinónimos ni se reordenan.
2. La identidad va antes que la acción y el estilo.
3. Este archivo nunca se edita para cambiar de estilo. Solo se reemplaza `style-guide.md`.