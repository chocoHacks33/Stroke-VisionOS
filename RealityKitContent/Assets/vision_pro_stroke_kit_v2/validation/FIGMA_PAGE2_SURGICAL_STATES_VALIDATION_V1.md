# Figma Page 2 surgical-state validation v1

Validation date: 2026-08-10

## Outcome

**5/5 packages pass; 0 fail.**
Module/state contract checks: **PASS**.

| Asset | Triangles | USDZ bytes | RK models | RK materials | RK dimensions X × Y × Z (m) | RK load ms | Result |
|---|---:|---:|---:|---:|---|---:|---|
| `scalp_access_closure_registered_conceptual_v1` | 61,242 | 7,723,532 | 2 | 2 | 0.197 × 0.280 × 0.242 | 138.6 | PASS |
| `cranial_bone_access_closure_registered_conceptual_v1` | 32,912 | 3,307,150 | 16 | 16 | 0.189 × 0.297 × 0.258 | 39.6 | PASS |
| `dural_access_closure_registered_conceptual_v1` | 25,227 | 6,693,170 | 2 | 2 | 0.158 × 0.174 × 0.173 | 131.7 | PASS |
| `intracerebral_hematoma_registered_conceptual_v1` | 240 | 14,794 | 3 | 3 | 0.042 × 0.040 × 0.029 | 5.8 | PASS |
| `cerebral_edema_registered_conceptual_v1` | 840 | 40,494 | 1 | 1 | 0.075 × 0.072 × 0.076 | 360.8 | PASS |

Every package passed `/usr/bin/usdchecker --arkit --strict`, contains exactly one
embedded USD stage, declares metre scale and Y-up, matches the manifest's USDC
and USDZ byte counts and SHA-256 hashes, and loads through the desktop RealityKit
probe with positive finite bounds and at least one model/material. Package asset
references resolve inside their USDZ archives. Runtime bounds match Blender
X/Y/Z to RealityKit X/Y/Z after the documented X/Z/Y axis mapping. All five
previews are 1600 × 1200.

No stage contains Camera, Light, Physics, time-sampled animation, glass/text/UI,
or hotspot prims. The three closure flaps remain distinct named entities. Their
closed pose is source identity; any animation is app-owned and makes no physical
trajectory or technique claim.

## USDZ SHA-256

- `scalp_access_closure_registered_conceptual_v1` — `076f8d74c238c2158686ceeacf9de1e58d8fae81483e9d4dfecd96434855da35`
- `cranial_bone_access_closure_registered_conceptual_v1` — `aca23f23d39187ba4b25d5bfb1acba4bc761236b9deae7bac06f2b1e4fb58322`
- `dural_access_closure_registered_conceptual_v1` — `02c6075a2bf5adc960774fc59caf3969b9aabd7387fd7670fc977361587238e2`
- `intracerebral_hematoma_registered_conceptual_v1` — `acd4f4195eca205ae686d10e2e69910ea34a69fdb252ea25a31b1fd7c958b5b4`
- `cerebral_edema_registered_conceptual_v1` — `7d5ae7a5a9e55de679d9e7e5e364715d8ecd05d851813a83e81988a80450c5a9`

## Scope and safety boundary

These packages are generic, non-patient-specific educational concepts. The scalp
opening, cranial aperture, dural opening, detached poses, hematoma, and edema are
not measurements, segmentations, plans, pressure models, techniques, or outcome
claims. Ordinary ischemic mechanical-thrombectomy presentation must not load the
open-cranial recipes. Those recipes are gated to a clinician-selected hemorrhage,
decompression, or other applicable open-neurosurgery narrative.

The source-derived scalp and skull retain CC BY 4.0 attribution. The dura and
pathology contexts are explicitly labeled project-authored concepts. The
ImageGen linework PNG is registered as look-development-only; it is neither
packed into the USDZ packages nor used by final runtime materials.

All interface glass, labels, progress, evidence cards, and hotspots remain native
SwiftUI/RealityKit attachments. Specialist, accessibility, privacy, human-factors,
representative-user, simulator, and physical-device review is still required.
`patient_display_authorized` remains `false` for every package and the module.
Desktop RealityKit load times are structural evidence only—not Vision Pro
performance, comfort, or clinical validation.
