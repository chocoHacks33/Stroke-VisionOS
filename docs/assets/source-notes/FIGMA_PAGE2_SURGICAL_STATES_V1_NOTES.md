# Figma Page 2 surgical states v1 — integration handoff

## Status and source boundary

This is the cross-module handoff for translating the inspected Figma Page 2
composition into Apple Vision Pro code. It joins, without merging:

- five USDZ packages from
  [`asset_manifest_figma_page2_surgical_states_v1.json`](../../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_figma_page2_surgical_states_v1.json);
- ten non-geometry resources from
  [`asset_manifest_figma_page2_surgical_interface_v1.json`](../../../RealityKitContent/InterfaceMedia/figma_page2_surgical_interface_v1/asset_manifest_figma_page2_surgical_interface_v1.json);
- existing manifest-backed head, vascular, flow, and open-tool packages.

The Figma page and supplied interface image were composition references only.
No Figma export, pixel, icon, clinical copy, anatomy, patient record, or PHI is
redistributed. Every module and binding remains
`patient_display_authorized=false`.

The release catalog is 150 USDZ packages in 14 manifests. The complete build
map is 152 records because build records 92 and 98 remain licence-held and have
no release binary. The new packages are build records 148–152 and release
numbers 146–150.

## Five USDZ assets, one by one

| Build / release | Asset | Canonical root | Exact role and exclusion |
|---|---|---|---|
| 148 / 146 | `scalp_access_closure_registered_conceptual_v1` | `HeadRegisteredRoot/RegisteredOpenCranialAnatomyRoot/RegisteredExposureStateRoot` | HRA-derived scalp remainder and named source-surface flap. It replaces other scalp variants in the gated open state. The opening is not an incision, marking, or plan. Prohibited in ordinary EVT. |
| 149 / 147 | `cranial_bone_access_closure_registered_conceptual_v1` | `HeadRegisteredRoot/RegisteredOpenCranialAnatomyRoot/RegisteredBoneStateRoot` | Visible-Human-derived skull with generic parietal aperture and named detached flap. It replaces the base semantic skull. Craniotomy may restore it; decompressive craniectomy must leave it off. Prohibited in ordinary EVT. |
| 150 / 148 | `dural_access_closure_registered_conceptual_v1` | `HeadRegisteredRoot/RegisteredOpenCranialAnatomyRoot/RegisteredDuralStateRoot` | Registered conceptual dura remainder and named source-surface flap. It replaces other dura variants. Opening and thickness are conceptual. Prohibited in ordinary EVT. |
| 151 / 149 | `intracerebral_hematoma_registered_conceptual_v1` | `HeadRegisteredRoot/PathologyRoot` | Refined legacy project concept registered to the generic v2 brain frame. Zero-or-one reviewed Page 2 pathology alternative. Not a segmentation, measured volume, target, or completion cue. |
| 152 / 150 | `cerebral_edema_registered_conceptual_v1` | `HeadRegisteredRoot/PathologyRoot` | Refined legacy project concept registered to the generic v2 brain frame. Gated to reviewed edema/decompression context. No extent, mass effect, pressure, or prognosis meaning. |

All five use `/Asset`, metres, and Y-up. They contain no camera, light, UI,
physics, or time-sampled animation. Scalp and dura preserve the existing PBR
maps; the ImageGen holographic-linework image is look-development-only, is not
packed into a USDZ, and is not used by final runtime materials.

Records 148–150 inherit the generic v2 `HeadRegisteredRoot` transform; they are
not legacy-v1 staging geometry. Legacy open tools remain under
`LegacyHeadRoot/OpenCranialRoot`. Co-presenting a tool requires an explicit,
versioned, reviewed tool-to-anatomy transform—never transform inheritance
between roots or placement guessed from Figma/bounds.

## Six-step open composition

The interface contract uses user-controlled navigation with no auto-advance.
The visible wording below is design intent, not approved clinical copy.

| Step | Interaction ID | Scene ID | Geometry recipe / rule |
|---:|---|---|---|
| 1 | `OPEN_CONFIRM_POSITION` | `OPEN_CONFIRM_SITE` | `figma_page2_craniotomy_position_planning`; realistic brain + scalp + cranial-bone state for generic orientation only, never patient planning or navigation. |
| 2 | `OPEN_CREATE_ACCESS` | `OPEN_ESTABLISH_CRANIAL_ACCESS` | Scalp and cranial-bone replacements; app-owned visibility/pose only, no drilling or cutting physics. |
| 3 | `OPEN_DURAL_ACCESS` | `OPEN_ESTABLISH_DURAL_ACCESS` | `figma_page2_dura_access`; add realistic brain and conceptual dura replacement with a non-graphic disclosure. |
| 4 | `OPEN_TREAT_CONDITION` | `OPEN_TREAT_REVIEWED_CONDITION` | `figma_page2_open_branch_treatment`; a clinician chooses zero or one reviewed pathology context. Tools stay explanatory; no procedure is inferred. |
| 5 | `OPEN_CLOSE_DURA_SKULL` | `OPEN_REPLACE_AND_FIX_BONE_FLAP` | `figma_page2_dura_bone_flap_closure` for craniotomy only. Decompressive craniectomy uses its own leave-off state and no fixation. |
| 6 | `OPEN_CHECK_RESULT` | `OPEN_POST_CLOSURE_REVIEW` | `figma_page2_final_closed_result`; unload access layers and return to existing closed assets. Interface completion is not treatment success or outcome. |

`EVT`, `OPEN_CRANIOTOMY`, `DECOMPRESSIVE_CRANIECTOMY`, and `OPTIONAL_EVD`
are distinct pathway IDs. Cross-pathway transition is disabled. Ordinary EVT
must reject every new USDZ before resolving its URL. Optional EVD is off by
default and carries no target, trajectory, depth, level, pressure, flow, or
operating instruction.

## Runtime state

Use the eight exact manifest state IDs:

```text
figma_page2_head_orientation
figma_page2_stroke_flow_explanation
figma_page2_craniotomy_position_planning
figma_page2_dura_access
figma_page2_open_branch_treatment
figma_page2_dura_bone_flap_closure
figma_page2_final_closed_result
figma_page2_authoring_review
```

Recommended orthogonal app state:

```text
page2Pathway = off | evt | openCraniotomy | decompressiveCraniectomy | optionalEVD
page2OpenStep = off | confirmPosition | createAccess | duralAccess |
                treatCondition | closeDuraSkull | checkResult
page2Pathology = none | hematomaConcept | edemaConcept
boneClosure = notApplicable | craniotomyReplace | decompressiveLeaveOff
```

Changing pathway stops animation, unloads incompatible payloads, clears step,
pathology, hotspot, and closure state, then restores the reviewed baseline.
Visited/completed means interface navigation only.

## Native attachment ownership

SwiftUI/RealityKit owns the title pill, left sticker rail, right topic pill,
right detail card, warning, bottom timeline, case carousel, controls, hotspots,
leader lines, localized copy, accessibility, and progress. visionOS owns hand
presence, gaze privacy, pinch, hover, passthrough, and boundaries. No one bakes
these into anatomy.

The attachment file provides initial model envelope and layout values only.
Replace them after physical-device human-factors review. Keep Pause,
Reset/Home, Exit/Return, Show Less/More, and Restore Original available. With
Reduce Transparency, use an opaque high-contrast surface. With Dynamic Type,
scroll rather than shrinking below reviewed type. With Reduce Motion, use a
static state swap.

The copy and anchor catalogs fail closed. Render nothing unless the exact asset
revision/hash, entity selector, local transform, display copy, citation, locale,
accessible equivalent, review IDs, and display authorization are complete.
Never use a mesh centre, colour, guessed name, OCR, Figma label, or generated
wording as fallback.

## Physics and animation

The packages are static. Three exact movable children support host-only
qualitative closure presentation:

```text
Registered_Source_Derived_Scalp_Flap_Open
Registered_Source_Derived_Bone_Flap_Detached
Registered_Source_Derived_Conceptual_Dural_Flap_Open
```

The authored transform is the open pose; source identity is the closed pose.
The app owns duration, easing, pause, replay, interruption, static Reduce Motion
fallback, and reset. Use a kinematic presentation proxy or direct transform
interpolation with no dynamic body or anatomy contact. Do not communicate
trajectory, force, cutting, tissue deformation, fixation, watertight closure,
timing, completion, or outcome.

Hematoma and edema are visibility/highlight contexts only. Do not animate
growth, evacuation, pressure, mass effect, tissue response, or prognosis.

## Houdini / Solaris handoff

Keep each USDZ/USDC as an immutable payload. Suggested layer and variants:

```text
17_page2_open_states.usda
page2Pathway={off,evt,openCraniotomy,decompressiveCraniectomy,optionalEVD}
page2OpenStep={off,confirmPosition,createAccess,duralAccess,treatCondition,
               closeDuraSkull,checkResult}
scalpState={base,accessOpen,sourceIdentityClosed}
cranialBoneState={base,accessOpen,craniotomyReplaced,decompressiveLeaveOff}
duraState={base,accessOpen,sourceIdentityClosed}
page2Pathology={none,hematomaConcept,edemaConcept}
```

Author no `evt` variant with Page 2 open payloads and no decompressive variant
that restores/fixes the flap. Put only references, visibility opinions, and
reviewed rigid transforms in the state layer. Keep branch selection, clinical
copy, authorization, and progress in the lesson/app layer. Keep native UI and
attachment transforms out of USD. Do not create a duplicate combined head or
review USDZ.

Place records 148–150 under
`/World/Patient/Head/RegisteredOpenCranial/{Exposure,Bone,Dura}` so they inherit
the registered head frame. Keep legacy tools under `/World/OpenCranial` and
author any reviewed co-presentation transform separately in
`25_tool_placement.usda`.

## Performance and loading

The five packages total 17,779,140 bytes and 120,461 triangles. The three
access layers account for 119,381 triangles. Load only the current replacements
and unload them for the closed-result recipe. Do not co-load base and replacement
scalp/skull/dura. The full release payload is 298,669,039 bytes (284.83 MiB),
not a preload target.

The per-package desktop RealityKit load observations recorded in the validation
report prove structural loading only. They are not Simulator, physical Vision
Pro, frame-time, memory, thermal, comfort, or latency budgets. Profile the exact
active scene on physical hardware with RealityKit Trace; test attachment count,
transparency, shadows, materials, animation interruption, and pathway unload
separately.

## Validation and release gates

Current technical evidence:

- 5/5 strict ARKit USD PASS;
- 5/5 desktop RealityKit load/model/material/bounds PASS;
- exact USDZ byte/SHA-256 integrity PASS;
- required named entities, metre/Y-up/default prim, package references,
  preview dimensions, no-camera/light/UI/physics/animation contract PASS;
- ten-resource interface pack exact byte/SHA-256, JSON, pathway separation,
  null binding, and patient-display block PASS.

This does not authorize patient or family display. Required remaining gates
include neurosurgery, stroke neurology, neuroanatomy, patient education,
accessibility, privacy, human factors, representative users, clinical evidence,
localized copy, simulator integration, physical-device composition/comfort,
RealityKit performance, quality, legal/licensing, institutional governance, and
the exact signed review record.

See the [module validation](../../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/validation/FIGMA_PAGE2_SURGICAL_STATES_VALIDATION_V1.md),
[source provenance](../../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/FIGMA_PAGE2_SURGICAL_STATES_SOURCE_PROVENANCE_V1.md),
and [interface pack README](../../../RealityKitContent/InterfaceMedia/figma_page2_surgical_interface_v1/README.md).
