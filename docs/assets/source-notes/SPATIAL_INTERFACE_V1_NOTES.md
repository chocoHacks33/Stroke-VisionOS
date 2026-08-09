# Spatial interface v1 — resource and integration notes

## Purpose

`spatial_interface_v1` is the non-geometry handoff for reproducing the supplied
Apple Vision Pro composition without turning cards, hands, glass, text, or
annotations into USDZ models. It gives a future native visionOS app four
deterministic scene recipes, fictional demo-card media, review-blocked content
scaffolds, native design starting points, and explicit integration guards.

The module is a developer preview. It is not patient-display authorized, a
clinical dashboard, a patient record, a Simulator build, or evidence that any
screen has run on physical Apple Vision Pro hardware.

## Location and inventory

The module lives at
`RealityKitContent/InterfaceMedia/spatial_care_interface_v1/` and contains 14
manifested resources:

| Resource | Role |
|---|---|
| `asset_manifest_spatial_interface_v1.json` | Module identity, hashes, platform ownership, dependencies, and prohibitions |
| `spatial_scene_preset_catalog_v1.json` | Landing, guided, scholar, and detached-vignette composition recipes |
| `spatial_ui_design_tokens_v1.json` | Native-glass roles, semantic typography/color, spacing, accessibility fallbacks, and depth starting points |
| `spatial_icon_catalog_v1.json` | Semantic SF Symbol candidates plus localized text fallbacks; no copied icon art |
| `demo_case_library_v1.json` | Four fictional, non-PHI educational scene selectors |
| `educational_evidence_card_catalog_v1.json` | Three empty, fail-closed evidence placeholders |
| `spatial_annotation_anchor_map_v1.json` | Eight SHA-bound annotation requests with no guessed selectors, transforms, or display copy |
| `spatial_annotation_anchor_map_v1.schema.json` | Draft 2020-12 schema for the annotation handoff |
| `stroke_care_wordmark_v1.svg` | Project-owned code-native vector wordmark |
| Four `case_portraits/fictional_case_portrait_*.png` files | Synthetic demo-card identifiers only |
| `previews/spatial_care_interface_storyboard_v1.png` | Supporting, non-runtime composition target |
| `image_generation_provenance_v1.json` | ImageGen prompt-intent, hash, dimension, source, and use-boundary record |

The module contains zero USDZ files and does not alter any anatomy package.

## Scene presets

### `stroke_care_landing_scene_v1`

- Parent: `AdaptivePresentationRoot`.
- Optional source: `brain_orientation_calm_educational_v1` only after exact
  asset, policy, mapping, specialist, human-factors, and patient-display
  approval. The current source remains display-blocked.
- App-owned presentation: hologram material and orientation ring.
- Native UI: wordmark, explanation, Family and Presenter actions, disclosure.
- Fail-closed behavior: render the landing UI with no 3D brain.
- Exclusion: detailed anatomy, pathology, vessels, blood/flow, micro content,
  and procedure tools.

### `stroke_guided_head_scene_v1`

- Parent: `PatientContextRoot/HeadRegisteredRoot`.
- Base components: cutaway scalp, realistic brain, cerebral arteries, and
  neck-access arteries.
- Discrete state assets: Circle-of-Willis flow overlay, conceptual right-M1
  clot, and optional right-sided illustrative flow animation.
- Optional context: eyes, semantic skull, deep structures, and ventricles.
- Native UI: progress, reviewed facts, tool rail, flow control, annotations,
  and complete Reset/Home.
- Exclusion: intact scalp, combined hero/cutaway assemblies, haemorrhage,
  micro-scale tissue zones, neural review assembly, and open-cranial tools.

The currently released pathology and baked animation are right-sided. The app
must say “conceptual right-M1 occlusion.” It must reject left-MCA copy rather
than mirror or silently relabel the assets.

### `stroke_scholar_head_scene_v1`

- Parent: `PatientContextRoot/HeadRegisteredRoot`.
- Base: brain, cerebral arteries, and conceptual right-M1 clot.
- Focus choices: one of the frontal, parietal, temporal, insular/opercular, or
  basal-ganglia/deep-nuclei packages.
- Only one focus package may be active. Hide or cut the opaque cortex before an
  internal focus is shown.
- Structural labels only. “Scholar” means higher information density, not
  clinical validation, patient-specific function, diagnosis, or permission to
  infer motor, speech, language, deficit, perfusion, or outcome.

### `m1_occlusion_vessel_vignette_scene_v1`

- Parent: `TeachingVignetteRoot`.
- Variant A loads `artery_cutaway_complete_v2` under
  `VesselWallVignetteRoot`.
- Variant B loads
  `platelet_fibrin_thrombus_microstructure_conceptual_v3` under
  `MicroScaleRoot`.
- Exactly one scale domain is active. Neither may be registered into the head.
- The circular portal is native UI, not a USDZ.
- A persistent magnified, conceptual, nonquantitative, non-patient warning is
  mandatory.

## Native visionOS ownership

The future SwiftUI/RealityKit app, not this resource pack, must own:

- windows, ornaments, native glass, case cards, buttons, text, progress, topic
  rails, evidence surfaces, warnings, and circular portal framing;
- placement, gestures, hover, focus, selection, accessibility, localization,
  Reduce Motion, Reduce Transparency, contrast fallbacks, and Reset/Home;
- exact annotation attachments and camera-readable leader lines;
- scene/pathway state, aggregate exclusions, laterality checking, loading,
  error states, and restoration;
- app-owned material and procedural presentation effects.

Passthrough, simulated environments, hands, gaze-based targeting, and natural
input are system-provided. Do not bundle hand meshes or record raw hand/gaze
data. Hand input may select UI; it must never feed an anxiety or preference
inference.

## Annotation completion contract

The anchor map is intentionally incomplete. Every request records the exact
source package path and SHA-256 but leaves these values `null`:

- `entity_selector`;
- `local_anchor_transform`;
- `approved_display_copy`.

An implementation agent must inspect the exact package revision in RealityKit,
bind a stable child-index path or reviewed entity path, author the anchor in
source-asset local metres, verify laterality and occlusion from representative
viewpoints, and attach structural and accessible copy to one signed review
record. Bounds centres, material colors, fuzzy entity-name matches, or a
generated storyboard must never supply an anchor. A package hash change
invalidates the selector and anchor.

## Fictional case and portrait contract

The case library uses relative educational sequences with no names, real dates,
absolute clinical timestamps, identifiers, recommendations, eligibility,
outcome probability, or patient scans. Every case must retain the visible badge:

> Fictional educational scenario — not a patient record

The portraits were generated with built-in ImageGen, are synthetic, and have no
identity or clinical role. The complete reconstructed prompt intent, hashes,
dimensions, and restrictions are in `image_generation_provenance_v1.json`.
Appearance cannot be used to infer condition, history, outcome, role, or any
personal trait. A privacy reviewer must still assess accidental resemblance
before public distribution.

The storyboard is also generated and supporting-only. Visual QA found generated
phrases including “real-world cases” and a generic evidence statement. Those
pixels conflict with the machine-readable fictional-case/evidence contracts.
Do not transcribe, OCR, ship, or treat its text as approved copy. It is a layout
reference, not a runtime mock, anatomy source, clinical source, or device test.

## Evidence-card completion contract

The catalog contains placeholders, not medical claims. A card must remain
hidden in patient/family mode until a governed record approves the exact claim,
plain-language copy, current primary source, source version and date, applicable
population, limitations, locale, accessibility copy, reviewer role, review ID,
and re-verification/expiry rule together. Do not copy the supplied reference
image's citation or generated storyboard wording.

## Design-token and icon contract

Design-token values are starting points. Use native dynamic text and glass,
then replace values based on physical-device accessibility and human-factors
evidence. Colors never stand alone, and a green completion state may confirm an
interface action only—not treatment success. “Measure” is a non-clinical visual
comparison affordance and must expose no anatomy, lesion, device, distance,
trajectory, or sizing measurement.

The icon catalog contains semantic SF Symbol candidates, not copied paths.
Check symbol availability for the actual deployment target and fall back to the
localized text label.

## Remaining implementation work

1. Create and record the native Xcode visionOS project, deployment target,
   scheme, app state owner, and resource-copy phases.
2. Decode this manifest and all referenced release manifests with strict,
   fail-closed validation.
3. Implement the four presets as app-owned scene state, not duplicated geometry.
4. Implement platform UI, loading/error/empty states, family privacy flow, and
   one-action complete restoration.
5. Complete and review exact annotation selectors, transforms, copy, and
   accessibility order for the frozen package hashes.
6. Replace or hide every evidence placeholder only through the governed review
   workflow.
7. Measure visible triangles, entities, memory, draw calls, label occlusion,
   frame timing, and transition comfort in the assembled view.
8. Validate the Simulator separately from physical Vision Pro. Physical-device
   QA must cover readability, input, seated/reclined use, contrast, Reduce
   Transparency, Reduce Motion, privacy, and comfort.
9. Obtain clinical, neuroanatomy/interventional, privacy, accessibility,
   human-factors, licensing, and release approval for the exact build.
