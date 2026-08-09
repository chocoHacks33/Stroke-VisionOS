# Figma Page 2 surgical-interface contract pack v1

This directory is an isolated, non-geometry developer handoff for translating
the supplied Page 2 composition into native visionOS UI. It contains no copied
Figma artwork, clinical copy, PHI, patient record, anatomy, USDZ, gesture mesh,
or validated surgical simulation. Every resource is
`patient_display_authorized=false`.

The Figma file was used only to identify broad interface intent: a case entry,
a manipulable head presentation, native-glass attachments, reviewed hotspots,
and a step-oriented walkthrough. It is not an anatomical, procedural, timing,
device, treatment, or outcome source.

## Manifested resources

| Resource | Role |
|---|---|
| `page2_interaction_contract_v1.json` | Navigation and interaction state contract, including a separately gated open-cranial sequence. |
| `page2_attachment_layout_v1.json` | Native SwiftUI/RealityKit attachment starting points; no UI is baked into anatomy. |
| `page2_ui_tokens_v1.json` | Native-glass, typography, colour, motion, and accessibility starting points. |
| `page2_icon_catalog_v1.json` | SF Symbols candidate mapping with mandatory localized text equivalents. |
| `surgical_walkthrough_scene_catalog_v1.json` | Mutually separated EVT, open craniotomy, decompressive craniectomy, and optional-EVD scene states. Asset bindings and display copy fail closed. |
| `surgical_walkthrough_anchor_map_v1.json` | Empty review scaffold. Every asset revision, selector, transform, and display-copy field is null until reviewed together. |
| `surgical_walkthrough_copy_catalog_v1.json` | Pathway-specific clinical copy slots. All actual title, body, voiceover, accessibility, citation, and locale fields are null and review-blocked. |
| `figma_page2_surgical_interface_provenance_v1.json` | Authorship, source boundary, and licensing/provenance declaration. |
| `validate_figma_page2_surgical_interface_v1.py` | Deterministic JSON, safety-invariant, path, byte-count, and SHA-256 validation. |
| `README.md` | This scope, integration, and validation handoff. |

`asset_manifest_figma_page2_surgical_interface_v1.json` indexes the ten
resources above by exact relative path, byte count, SHA-256, media type, and
runtime role. The manifest intentionally does not hash itself.

## Integration boundary

- Keep `EVT`, `OPEN_CRANIOTOMY`, and `DECOMPRESSIVE_CRANIECTOMY` mutually
  exclusive. Ordinary EVT remains endovascular and must never show a scalp
  incision, bone flap, open dura, or exposed brain.
- Keep the reviewed closure states distinct. A craniotomy presentation may
  replace the bone flap; a decompressive-craniectomy end state must not.
- Treat `OPTIONAL_EVD` as conditional companion content only after an explicit
  reviewed scenario selection. It is never a routine step and carries no
  settings, parameters, targets, or operating instructions here.
- Resolve all anatomy and device assets through their own release manifests.
  This pack names no runtime USDZ binding and changes no 3D asset tree.
- Render panels, copy, controls, progress, and warnings as accessible native
  SwiftUI attachments. Use the platform for hands, gaze, hover, and pinch.
- Hide every unresolved scene, anchor, and copy slot. Never infer an anchor
  from a screenshot and never use Figma/OCR/generated text as clinical copy.
- A visited timeline state indicates interface navigation only—not treatment
  completion, success, prognosis, or outcome.

## Validation

From this directory, run:

```sh
python3 validate_figma_page2_surgical_interface_v1.py
```

Passing validation means only that local files parse, exact byte/hash records
match, and the fail-closed invariants remain intact. It is not clinical,
anatomical, accessibility, Simulator, physical-device, comfort, performance,
privacy, regulatory, or patient-display evidence.

Before any patient/family pilot, bind and review exact asset revisions,
selectors, transforms, laterality, localized copy, citations, accessibility,
and pathway transitions together; then complete clinical, human-factors,
privacy, accessibility, Simulator, and physical Vision Pro validation.
