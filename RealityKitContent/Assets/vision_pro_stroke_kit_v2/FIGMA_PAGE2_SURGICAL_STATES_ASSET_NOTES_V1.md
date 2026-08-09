# Figma Page 2 surgical-state asset notes v1

## Purpose and hard boundary

`figma_page2_surgical_states_v1` is a lean presentation module for the Figma
Page 2 surgical flow. It adds only five registered state packages and composes
all other anatomy, vascular, flow, and tool content from existing kit IDs.
There is no duplicate full-head hero assembly.

Every package is a generic, non-patient-specific educational prototype with
`patient_display_authorized=false`. Nothing is a measurement, segmentation,
diagnosis, patient plan, navigation target, pressure model, device-sizing aid,
technique, outcome claim, or training simulation. Specialist and human-factors
review is required before any patient/family display.

Open-cranial content is prohibited in the ordinary ischemic mechanical-
thrombectomy pathway. The app may load it only after a clinician selects an
applicable hemorrhage, decompression, or other open-neurosurgery narrative.

## Exact five-package inventory

| # | Asset ID | Triangles | Role |
|---:|---|---:|---|
| 1 | `scalp_access_closure_registered_conceptual_v1` | 61,242 | Registered HRA scalp remainder with a generic presentation opening and an independently transformable source-surface flap. The opening is explicitly not an incision or marking plan. Existing `Scalp_Skin_PBR_v2` texture detail is retained. |
| 2 | `cranial_bone_access_closure_registered_conceptual_v1` | 32,912 | Registered Visible-Human skull with a generic parietal aperture and detached source-derived bone flap. It is a presentation state, not a craniotomy location or geometry recommendation. |
| 3 | `dural_access_closure_registered_conceptual_v1` | 25,227 | Existing registered conceptual dura with a generic opening and independent source-surface flap. `Dura_Mater_PBR_v2` is retained so the layer reads as a restrained membrane; authored thickness remains non-physiologic. |
| 4 | `intracerebral_hematoma_registered_conceptual_v1` | 240 | Selected legacy project hematoma lobes, rescaled and registered into the generic v2 brain frame. It is non-quantitative and not a segmentation. |
| 5 | `cerebral_edema_registered_conceptual_v1` | 840 | Selected legacy project swelling volume, rescaled, softly lobulated, and registered into the generic v2 brain frame. It is a conceptual highlight, not edema extent, mass effect, or pressure data. |

Exact package bytes, USDC/USDZ SHA-256 values, bounds, preview paths, source
registrations, and review flags are in
`asset_manifest_figma_page2_surgical_states_v1.json`.

## Runtime coordinate and entity contract

- Authoring units: metres.
- Runtime USD up-axis: Y.
- Package root: `/Asset`.
- Cameras, lights, UI, glass panels, text, labels, progress bars, hotspots,
  physics, and time-sampled animation are excluded.
- Each package loads independently. Never infer a procedure from geometry.

Named movable child entities:

| Package | Entity |
|---|---|
| Scalp | `Registered_Source_Derived_Scalp_Flap_Open` |
| Bone | `Registered_Source_Derived_Bone_Flap_Detached` |
| Dura | `Registered_Source_Derived_Conceptual_Dural_Flap_Open` |

The current detached transform is the open presentation pose. Closed pose is
the corresponding source-identity placement. Any interpolation is host-app
animation only and must not be described as measured motion, a physical
trajectory, tissue behavior, surgical technique, or time estimate. No dynamic
physics is authored or implied.

## Eight app-managed scene-state recipes

| State enum | Composition contract |
|---|---|
| `figma_page2_head_orientation` | Default to `brain_anatomy_realistic_v2`; optionally hide/show `external_head_scalp_realistic_v2` with opaque visibility swaps. The simplified calm brain is a separately review-blocked replacement candidate, never a default overlay. |
| `figma_page2_stroke_flow_explanation` | Compose the realistic brain, existing cerebral arteries, ischemic MCA clot, and Circle-of-Willis flow overlay. Flow material/opacity animation is app-owned. |
| `figma_page2_craniotomy_position_planning` | Compose scalp and bone access packages only after the open-neurosurgery gate. It is generic orientation—not patient planning. |
| `figma_page2_dura_access` | Compose realistic brain plus scalp, bone, and dura packages under the same gate. Prefer opaque cutaway/visibility swaps. |
| `figma_page2_open_branch_treatment` | Compose the open layers, reviewed open-neurosurgery tool sets, and zero or one clinician-selected pathology context. The app must never infer the selection. |
| `figma_page2_dura_bone_flap_closure` | Restore dura, bone, then scalp child entities toward source identity; tool objects stay explanatory and off the anatomy unless a reviewed app script places them. |
| `figma_page2_final_closed_result` | Return to existing closed scalp/brain/skull/arterial assets. A completion halo is presentation only and cannot imply treatment success. |
| `figma_page2_authoring_review` | Reuse the seven states as app-managed miniatures for internal review. There is no duplicated review USDZ and it is not patient-displayable. |

## Materials and interface ownership

Runtime packages use restrained patient-education materials. Scalp and dura
preserve their existing registered PBR texture sets; bone is warm and matte;
pathology uses clear but non-graphic contrast. Anxiety-profile styling,
wireframe, glow, opacity transitions, LOD choice, and pacing belong to the app.
Do not stack transparent head layers by default; use explicit cutaways and
visibility swaps.

All Figma glass panels, headings, labels, callouts, evidence cards, controls,
progress, and hotspots remain native SwiftUI/RealityKit attachments. Geometry
must not be edited to bake screen text or interaction state.

## Validation and remaining work

All five USDZ packages pass strict ARKit USD validation and desktop RealityKit
load/bounds validation. See:

- `validation/FIGMA_PAGE2_SURGICAL_STATES_VALIDATION_V1.md`
- `validation/figma_page2_surgical_states_v1_validation.json`

Technical validation does not authorize healthcare deployment. Integrate in a
real visionOS target, then perform Simulator and physical-device composition,
memory/frame-time, comfort, accessibility, privacy, clinical narrative,
representative-user, and institutional governance review.
