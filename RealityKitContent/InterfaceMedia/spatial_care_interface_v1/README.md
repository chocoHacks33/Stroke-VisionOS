# Spatial-care interface resource pack v1

This directory contains **14 manifest-backed, non-USDZ supporting resources**
for reproducing the supplied four-state spatial-computing concept with native
visionOS UI and the repository's existing anatomy. These resources do not add
to the 145-package 3D count. Every item remains
`patient_display_authorized=false`.

The pack is a developer handoff, not a finished screen, clinical dashboard,
patient record, simulator capture, or evidence source. Read
[`MASTER.md`](../../../MASTER.md) for canonical roots, scene state, physics,
Houdini/Solaris handoff, exclusions, and release gates.

## One-by-one inventory

| # | Manifest resource ID | File | What it represents and where it belongs |
|---:|---|---|---|
| 1 | `spatial_scene_preset_catalog_v1` | [`spatial_scene_preset_catalog_v1.json`](spatial_scene_preset_catalog_v1.json) | Four deterministic developer-preview scene recipes: landing, guided right-M1 head, scholar structural detail, and detached vessel/micro vignette. The host app validates every referenced USDZ ID and enforces all exclusions before loading. |
| 2 | `demo_case_library_v1` | [`demo_case_library_v1.json`](demo_case_library_v1.json) | Four fictional educational scenarios connected to the scene presets. It contains no real name, diagnosis, timestamp, recommendation, eligibility, or outcome. The fictional-case badge is mandatory. |
| 3 | `educational_evidence_card_catalog_v1` | [`educational_evidence_card_catalog_v1.json`](educational_evidence_card_catalog_v1.json) | Three intentionally empty evidence-card slots. Claim and source fields are null; patient/family display fails closed until current source, exact copy, accessibility, locale, expiry, and review are approved together. |
| 4 | `spatial_annotation_anchor_map_v1` | [`spatial_annotation_anchor_map_v1.json`](spatial_annotation_anchor_map_v1.json) | Eight exact-package-hash annotation requests for brain, arteries, right-M1 marker, selected structural regions, and right ICA. Entity selectors, transforms, and display copy are deliberately null so the app cannot guess an anchor. |
| 5 | `spatial_annotation_anchor_map_v1_schema` | [`spatial_annotation_anchor_map_v1.schema.json`](spatial_annotation_anchor_map_v1.schema.json) | Draft 2020-12 structural schema for the annotation review scaffold. A reviewed tool must validate it before consuming future completed anchors. |
| 6 | `spatial_ui_design_tokens_v1` | [`spatial_ui_design_tokens_v1.json`](spatial_ui_design_tokens_v1.json) | Native glass roles, typography, spacing, semantic colours, attachment/depth starting points, motion, contrast, and accessibility requirements. Values are design starting points requiring Simulator and physical-device QA. |
| 7 | `spatial_icon_catalog_v1` | [`spatial_icon_catalog_v1.json`](spatial_icon_catalog_v1.json) | Semantic feature-to-SF-Symbol candidate mapping with localized text fallbacks. No copied icon artwork is included, and symbols carry no clinical-success or measurement meaning. |
| 8 | `stroke_care_wordmark_v1` | [`stroke_care_wordmark_v1.svg`](stroke_care_wordmark_v1.svg) | Original code-native landing wordmark. It is project identity—not a certification, hospital, regulator, or medical-device mark. |
| 9 | `fictional_case_portrait_01_v1` | [`fictional_case_portrait_01.png`](case_portraits/fictional_case_portrait_01.png) | Synthetic demo portrait for Fictional Scenario 01/right-M1 orientation. It represents no real person or patient. |
| 10 | `fictional_case_portrait_02_v1` | [`fictional_case_portrait_02.png`](case_portraits/fictional_case_portrait_02.png) | Synthetic demo portrait for Fictional Scenario 02/qualitative flow-cue comparison. It represents no real person or patient. |
| 11 | `fictional_case_portrait_03_v1` | [`fictional_case_portrait_03.png`](case_portraits/fictional_case_portrait_03.png) | Synthetic demo portrait for Fictional Scenario 03/structural anatomy detail. It represents no real person or patient. |
| 12 | `fictional_case_portrait_04_v1` | [`fictional_case_portrait_04.png`](case_portraits/fictional_case_portrait_04.png) | Synthetic demo portrait for Fictional Scenario 04/detached vessel teaching view. It represents no real person or patient. |
| 13 | `spatial_care_interface_storyboard_v1` | [`spatial_care_interface_storyboard_v1.png`](previews/spatial_care_interface_storyboard_v1.png) | ImageGen supporting target board for the landing, case browser, guided, and scholar compositions. It is not a runtime image or Simulator proof; generated visible wording must not be copied into the app. |
| 14 | `image_generation_provenance_v1` | [`image_generation_provenance_v1.json`](image_generation_provenance_v1.json) | Built-in ImageGen provenance, reconstructed prompt intent, hashes, dimensions, source-reference hash, and use restrictions for all five generated images. |

[`asset_manifest_spatial_interface_v1.json`](asset_manifest_spatial_interface_v1.json)
binds the 14 resource IDs to exact paths, byte counts, SHA-256 values, media
types, and runtime/supporting roles.

## Platform ownership

| Visual in the concept | Correct owner |
|---|---|
| Passthrough room or Simulator scene | visionOS / Simulator |
| Optional fully synthetic room | `spatial_care_environment_v1`, gated and disabled by default |
| Head, brain, arteries, right-M1 marker, flow and micro view | Existing USDZ manifests |
| Hands, gaze, hover and pinch | visionOS natural input; no custom hand mesh |
| Glass cards, buttons, text, warnings and topic rails | Native SwiftUI |
| 3D labels, leader lines, focus ring and attachments | App-owned RealityKit/SwiftUI attachments bound to reviewed anchors |
| Four portraits and fictional case text | This pack, always visibly fictional |
| Evidence statements | External reviewed content workflow; current placeholders stay hidden |

## Four-state connection

1. **Landing** — native wordmark and role actions; no detailed anatomy. The calm
   brain candidate remains blocked unless a future exact asset/policy review
   authorizes it.
2. **Case browser** — native carousel with the four fictional portraits and
   badge. Selection chooses a predetermined lesson; it never diagnoses or
   recommends.
3. **Guided head** — compose existing cutaway head, brain, arteries, neck
   arteries, conceptual right-M1 marker, and optional qualitative flow cues.
   App UI owns the short step rail, facts, Pause/Replay and Reset.
4. **Scholar head** — keep at most one semantic structure focus active; open
   vessel or micro content in a detached magnified root with persistent scale
   warnings. Evidence and unreviewed annotations stay hidden.

The current pathology and baked animation are right-sided. Do not label them
left MCA and do not mirror them. A left-sided version requires new source-backed
registered geometry, animation, copy, and clinical review.

## Validation and remaining work

See [integration notes](../../../docs/assets/source-notes/SPATIAL_INTERFACE_V1_NOTES.md)
and [validation](../../../docs/assets/validation/SPATIAL_INTERFACE_V1_VALIDATION.md).
Before patient/family use, implement the native app, fill exact annotation and
evidence review records, validate the JSON schema with a Draft 2020-12 tool,
capture genuine Simulator evidence, test on physical Vision Pro, and complete
clinical, privacy, accessibility, and human-factors review.
