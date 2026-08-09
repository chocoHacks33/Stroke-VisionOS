# Stroke VisionOS asset catalog

This directory contains **145 unique, manifest-backed runtime USDZ assets**:

- **69 release-eligible v3 assets** across five manifests: 43 anatomy/detail
  packages and 26 representative surgical-tool packages.
- **36 higher-detail v2 assets** across five manifests.
- **29 prototype-v1 assets** in one manifest.
- **1 comfort-oriented adaptive visual** in one manifest.
- **10 original optional spatial-care environment assets** in one manifest.
- **280,889,899 bytes** of runtime USDZ payload.

“Release-eligible” here means only that a package is not on the known
inner-ear licence hold and is present in the publishing catalog. It does not
mean clinically approved, hospital-ready, or suitable for patient-specific
decisions.

The count refers only to independently loadable USDZ packages. Manifests,
preview renders, material maps, and documentation are supporting files and are
not counted as additional runtime assets. Composite assemblies are counted
because they are separately loadable packages, although they duplicate geometry
from their component layers.

The complete source build has **147 unique package records**: 65 original, 71
v3, one adaptive visual derivative, and ten environment records. The two inner-ear-containing v3
packages are licence-held and their binaries are deliberately absent here, so
the release catalog contains 145 packages.

The historical review-only `stroke_kit_asset_gallery.usdz` is deliberately not
included. It is an unmanifested composite of prototype geometry, not an
additional 146th release asset or a 148th source-build package.

For the canonical scene hierarchy, all component/assembly relationships,
procedure state logic, interaction physics, and Houdini/RealityKit handoff, see
[`MASTER.md`](../../MASTER.md).

GitHub does not permit a public fork to upload new LFS objects into its parent
repository's LFS store. Consequently, this cross-fork pull request stores the
USDZ packages as ordinary binary Git objects; every individual package is below
GitHub's 50 MiB warning threshold. A maintainer with upstream write access may
migrate them to LFS in a coordinated follow-up.

## Naming and layout

Runtime filenames use stable lowercase `snake_case` IDs. Higher-detail assets
use a version suffix such as `_v1`, `_v2`, or `_v3`; combined review files say
`assembly`, `hero`, or `set`;
conceptual and educational files say so explicitly. The prototype filenames
remain unchanged because their manifest and existing viewer code reference
those exact IDs. Human-facing display names below provide readable labels
without breaking runtime references.

```text
Assets/
├── vision_pro_stroke_kit/
│   ├── asset_manifest.json
│   └── exports/usdz/                 # 29 prototype-v1 packages
└── vision_pro_stroke_kit_v2/
    ├── asset_manifest_v2.json
    ├── asset_manifest_head_details_v2.json
    ├── asset_manifest_cranial_vascular_v2.json
    ├── asset_manifest_bloodflow_v2.json
    ├── asset_manifest_devices_v2.json
    ├── asset_manifest_neural_detail_v3.json
    ├── asset_manifest_cranial_detail_v3.json  # release-safe, held records omitted
    ├── asset_manifest_intracranial_micro_v3.json
    ├── asset_manifest_endovascular_tools_v3.json
    ├── asset_manifest_open_cranial_tools_v3.json
    ├── asset_manifest_adaptive_visuals_v1.json
    ├── asset_manifest_spatial_care_environment_v1.json
    ├── exports/usdz/                 # 36 v2 + 69 v3 + 1 adaptive + 10 environment
    ├── previews/                     # supporting v2/v3 renders
    └── textures/source/              # supporting material maps
```

All stages use metres and Y-up. Macroscopic v2/v3 atlas stages preserve their
recorded project registration frames. Micro-v3 metres describe only a
presentation stage: those packages are magnified, scale-separated, and never
registered to the head. The models are generic and non-patient-specific.
See [licences](../../docs/assets/LICENSES.md),
[provenance](../../docs/assets/PROVENANCE.md), and
[validation](../../docs/assets/VALIDATION.md) before redistribution or use.

## Higher-detail v2 assets (36)

### Core registered anatomy (7)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 1 | [brain_anatomy_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/brain_anatomy_realistic_v2.usdz) | **Realistic generic brain anatomy.** Cortex, cerebellum, and brainstem hero layer in a common metre-scale frame. Generic anatomy requiring specialist review. |
| 2 | [brain_deep_structures_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/brain_deep_structures_v2.usdz) | **Generic deep brain structures.** Separately loadable semantic deep-anatomy reveal for guided explanations. |
| 3 | [brain_ventricles_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/brain_ventricles_v2.usdz) | **Generic ventricular system.** Independently toggleable ventricular anatomy for spatial orientation. |
| 4 | [skull_semantic_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/skull_semantic_realistic_v2.usdz) | **Semantic Visible Human skull.** Named cranial and facial bones suitable for isolated inspection and cutaway teaching. |
| 5 | [cerebral_arteries_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/cerebral_arteries_realistic_v2.usdz) | **Generic cerebral arterial tree.** Major cerebral pathways registered to the brain frame; ShareAlike source terms apply. |
| 6 | [ischemic_mca_clot_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/ischemic_mca_clot_v2.usdz) | **Conceptual right-M1 ischemic clot.** A teaching marker for an occlusion state, not a measured lesion or patient finding. |
| 7 | [thrombectomy_registered_hero_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/thrombectomy_registered_hero_v2.usdz) | **Registered thrombectomy anatomy hero set.** Combined review assembly; load individual layers for patient-facing interactions and performance control. |

### Head layers and meningeal context (9)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 8 | [external_head_scalp_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/external_head_scalp_realistic_v2.usdz) | **Generic external head and scalp.** Closed HRA-derived head/upper-neck exterior with a project-created skin material. |
| 9 | [external_head_scalp_cutaway_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/external_head_scalp_cutaway_v2.usdz) | **External-head cutaway.** Smooth educational cranial viewing window for revealing deeper layers without stacked transparency. |
| 10 | [eyes_context_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/eyes_context_realistic_v2.usdz) | **Bilateral eye context.** Separately toggleable Visible Human eye structures for orientation; omitted from the default layered assembly. |
| 11 | [dura_mater_conceptual_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/dura_mater_conceptual_v2.usdz) | **Conceptual dura mater shell.** Thin brain-hull-derived teaching surface; not a measured meningeal thickness. |
| 12 | [dura_mater_cutaway_conceptual_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/dura_mater_cutaway_conceptual_v2.usdz) | **Conceptual dura cutaway.** Dura shell with a rounded viewing window coordinated with the head reveal. |
| 13 | [falx_cerebri_atlas_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/falx_cerebri_atlas_v2.usdz) | **Falx cerebri atlas layer.** Independently toggleable named partition derived from atlas geometry. |
| 14 | [tentorium_cerebelli_atlas_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/tentorium_cerebelli_atlas_v2.usdz) | **Bilateral tentoria atlas layer.** Left and right tentorium structures for explaining compartment relationships. |
| 15 | [meningeal_partitions_atlas_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/meningeal_partitions_atlas_v2.usdz) | **Combined meningeal partitions.** Falx plus bilateral tentoria in one registered review layer. |
| 16 | [layered_head_cutaway_registered_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/layered_head_cutaway_registered_v2.usdz) | **Registered layered-head cutaway.** Scalp cutaway, conceptual dura, partitions, and brain. Skull and eyes remain optional separate assets to avoid cross-source intersections. |

### Cranial vascular detail (7)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 17 | [dural_venous_sinuses_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/dural_venous_sinuses_realistic_v2.usdz) | **Dural venous sinuses.** Sixteen named sinus structures. Purple/blue is a display convention and does not represent actual blood colour or oxygenation. |
| 18 | [internal_jugular_veins_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/internal_jugular_veins_realistic_v2.usdz) | **Bilateral internal jugular veins.** Separately toggleable cranial venous-outflow context. |
| 19 | [dural_sinuses_jugulars_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/dural_sinuses_jugulars_realistic_v2.usdz) | **Sinus and jugular teaching layer.** Combined dural-sinus and bilateral internal-jugular review package. |
| 20 | [head_neck_veins_supplemental_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/head_neck_veins_supplemental_v2.usdz) | **Supplemental head and neck veins.** Thirty-eight additional facial, scalp, ophthalmic, vertebral, jugular, and neck structures. |
| 21 | [head_neck_veins_expanded_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/head_neck_veins_expanded_realistic_v2.usdz) | **Expanded venous layer.** Complete 56-structure venous selection for contextual review. |
| 22 | [neck_access_arteries_realistic_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/neck_access_arteries_realistic_v2.usdz) | **Carotid and vertebral neck-access arteries.** Eight named artery structures connecting neck access context with the cranial circulation. |
| 23 | [cranial_vascular_registered_assembly_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_vascular_registered_assembly_v2.usdz) | **Registered cranial vascular assembly.** Combined 56-structure veins and eight access arteries; intended for review rather than simultaneous default loading. |

### Cerebral blood-flow teaching assets (8)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 24 | [artery_wall_cutaway_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/artery_wall_cutaway_v2.usdz) | **Magnified layered artery-wall cutaway.** Opened three-layer wall with deliberately exaggerated thickness for readability. |
| 25 | [artery_interior_bloodflow_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/artery_interior_bloodflow_v2.usdz) | **Illustrative lumen, blood, cells, and flow cues.** Magnified RBCs, streamlines, and arrows; non-CFD and non-quantitative. |
| 26 | [artery_cutaway_complete_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/artery_cutaway_complete_v2.usdz) | **Complete artery cutaway.** Combined wall, lumen, cells, and directional teaching cues. |
| 27 | [circle_of_willis_flow_overlay_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/circle_of_willis_flow_overlay_v2.usdz) | **Conceptual Circle-of-Willis flow overlay.** Simplified major-pathway directions for narrative sequencing, not perfusion analysis. |
| 28 | [red_blood_cells_closeup_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/red_blood_cells_closeup_v2.usdz) | **Magnified biconcave red-blood-cell close-up.** Two-sided central depressions designed to read clearly at educational scale. |
| 29 | [microcirculation_arterial_venous_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/microcirculation_arterial_venous_v2.usdz) | **Arteriole-capillary-venule vignette.** Conceptual route-following cells and vessel transition for microcirculation teaching. |
| 30 | [cerebral_bloodflow_animation_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/cerebral_bloodflow_animation_v2.usdz) | **Baked cerebral-flow marker animation.** Four-second posterior-to-right-MCA transform sequence with 24 RealityKit animation resources; non-CFD. |
| 31 | [cerebral_bloodflow_teaching_set_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/cerebral_bloodflow_teaching_set_v2.usdz) | **Combined blood-flow teaching set.** Static cutaway, flow overlay, RBC close-up, and microcirculation review collection. |

### Generic thrombectomy-device concepts (5)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 32 | [guidewire_educational_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/guidewire_educational_v2.usdz) | **Generic educational guidewire.** Metallic segment with curved distal tip and marker; unbranded and not dimensioned for device selection. |
| 33 | [microcatheter_educational_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/microcatheter_educational_v2.usdz) | **Generic educational microcatheter.** Hollow body, shaped tip, lumen, transition, and marker band. |
| 34 | [aspiration_catheter_educational_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/aspiration_catheter_educational_v2.usdz) | **Generic educational aspiration catheter.** Hollow large-bore concept with reinforcement and marker bands. |
| 35 | [stent_retriever_educational_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/stent_retriever_educational_v2.usdz) | **Generic educational stent retriever.** Deployed lattice, crowns, pusher, and markers; not a manufacturer-specific device. |
| 36 | [thrombectomy_device_set_educational_v2.usdz](vision_pro_stroke_kit_v2/exports/usdz/thrombectomy_device_set_educational_v2.usdz) | **Four-device comparison set.** Guidewire, microcatheter, aspiration catheter, and stent-retriever concepts arranged for review, not as a registered procedure configuration. |

## Prototype-v1 assets (29)

These assets are intentionally retained for sequencing, interaction, and
fallback testing. They are lower-detail prototypes and should not be presented
as the preferred patient-facing visual layer when a v2 equivalent exists.

### Shared anatomy (4)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 37 | [head_skin_generic.usdz](vision_pro_stroke_kit/exports/usdz/head_skin_generic.usdz) | **Generic head and scalp.** Neutral, non-identifying low-poly outer-head layer. |
| 38 | [skull_cranium_generic.usdz](vision_pro_stroke_kit/exports/usdz/skull_cranium_generic.usdz) | **Generic skull and cranium.** Simplified cranial shell and landmarks. |
| 39 | [brain_structures_generic.usdz](vision_pro_stroke_kit/exports/usdz/brain_structures_generic.usdz) | **Generic brain structures.** Simplified hemispheres, cerebellum, and brainstem. |
| 40 | [cerebral_arteries_generic.usdz](vision_pro_stroke_kit/exports/usdz/cerebral_arteries_generic.usdz) | **Generic cerebral arteries.** Simplified Circle of Willis and principal branches. |

### Pathology concepts (3)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 41 | [ischemic_lvo_clot.usdz](vision_pro_stroke_kit/exports/usdz/ischemic_lvo_clot.usdz) | **Ischemic large-vessel-occlusion clot.** Conceptual intraluminal obstruction marker. |
| 42 | [ich_hematoma.usdz](vision_pro_stroke_kit/exports/usdz/ich_hematoma.usdz) | **Intracerebral haemorrhage collection.** Conceptual escaped-blood volume; not a measured haematoma. |
| 43 | [edema_swelling.usdz](vision_pro_stroke_kit/exports/usdz/edema_swelling.usdz) | **Conceptual oedema and swelling.** Simplified pressure/swelling state inside the skull. |

### Procedure-room context (5)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 44 | [patient_supine_generic.usdz](vision_pro_stroke_kit/exports/usdz/patient_supine_generic.usdz) | **Generic supine patient.** Neutral silhouette and drape without identifying features. |
| 45 | [angiography_operating_table.usdz](vision_pro_stroke_kit/exports/usdz/angiography_operating_table.usdz) | **Angiography/operating table.** Simplified reusable procedure-room table. |
| 46 | [vital_sign_monitor.usdz](vision_pro_stroke_kit/exports/usdz/vital_sign_monitor.usdz) | **Vital-sign monitor.** Stylised procedure monitor without quantitative patient data. |
| 47 | [iv_pole_and_bag.usdz](vision_pro_stroke_kit/exports/usdz/iv_pole_and_bag.usdz) | **IV pole and bag.** Generic room-context prop. |
| 48 | [clinical_team_generic.usdz](vision_pro_stroke_kit/exports/usdz/clinical_team_generic.usdz) | **Generic clinical team.** Two neutral staff silhouettes for scale and role context. |

### Mechanical-thrombectomy sequence (7)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 49 | [angiography_c_arm.usdz](vision_pro_stroke_kit/exports/usdz/angiography_c_arm.usdz) | **Angiography C-arm.** Simplified imaging gantry for room orientation. |
| 50 | [arterial_access_site.usdz](vision_pro_stroke_kit/exports/usdz/arterial_access_site.usdz) | **Arterial access site.** Conceptual introducer sheath and guidewire entering an artery. |
| 51 | [catheter_body_to_brain_route.usdz](vision_pro_stroke_kit/exports/usdz/catheter_body_to_brain_route.usdz) | **Body-to-brain catheter route.** Conceptual intravascular path for explaining access sequence. |
| 52 | [guidewire_microcatheter_set.usdz](vision_pro_stroke_kit/exports/usdz/guidewire_microcatheter_set.usdz) | **Guidewire and microcatheter set.** Separated components suitable for simple transform animation. |
| 53 | [stent_retriever.usdz](vision_pro_stroke_kit/exports/usdz/stent_retriever.usdz) | **Prototype stent retriever.** Stylised retrieval cage with captured-clot cue. |
| 54 | [aspiration_catheter.usdz](vision_pro_stroke_kit/exports/usdz/aspiration_catheter.usdz) | **Prototype aspiration catheter.** Simplified alternative treatment-path concept. |
| 55 | [angiography_contrast_flow.usdz](vision_pro_stroke_kit/exports/usdz/angiography_contrast_flow.usdz) | **Angiography contrast-flow overlay.** Conceptual before/after vessel-filling comparison. |

### Open-cranial treatment concepts (6)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 56 | [scalp_incision_flap.usdz](vision_pro_stroke_kit/exports/usdz/scalp_incision_flap.usdz) | **Scalp incision/flap concept.** Non-graphic layered reveal. Do not combine with a thrombectomy-only narrative. |
| 57 | [craniotomy_bone_flap.usdz](vision_pro_stroke_kit/exports/usdz/craniotomy_bone_flap.usdz) | **Craniotomy bone flap.** Removable teaching object for an open-cranial pathway. |
| 58 | [cranial_drill_generic.usdz](vision_pro_stroke_kit/exports/usdz/cranial_drill_generic.usdz) | **Generic cranial drill.** Stylised tool requiring procedure-specific specialist review. |
| 59 | [suction_and_forceps.usdz](vision_pro_stroke_kit/exports/usdz/suction_and_forceps.usdz) | **Suction and forceps.** Separated open-surgery instrument concepts. |
| 60 | [scalp_closure_sutures.usdz](vision_pro_stroke_kit/exports/usdz/scalp_closure_sutures.usdz) | **Scalp closure and sutures.** Non-graphic closed-incision state. |
| 61 | [dural_patch.usdz](vision_pro_stroke_kit/exports/usdz/dural_patch.usdz) | **Dural patch concept.** Configurable dural-expansion teaching object. |

### Haemorrhage-care concepts (2)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 62 | [minimally_invasive_evacuator_port.usdz](vision_pro_stroke_kit/exports/usdz/minimally_invasive_evacuator_port.usdz) | **Minimally invasive evacuator port.** Conceptual trajectory/evacuation port requiring specialist review. |
| 63 | [optional_evd_system.usdz](vision_pro_stroke_kit/exports/usdz/optional_evd_system.usdz) | **Optional external ventricular drain system.** Conceptual catheter and drainage chamber; not a default step. |

### Recovery and sequencing (2)

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 64 | [postoperative_head_dressing.usdz](vision_pro_stroke_kit/exports/usdz/postoperative_head_dressing.usdz) | **Postoperative head dressing.** Generic bandage/dressing recovery state. |
| 65 | [spatial_step_markers.usdz](vision_pro_stroke_kit/exports/usdz/spatial_step_markers.usdz) | **Spatial step markers.** Eight numbered markers and arrows in one wide entity for guided sequencing. |

## Intracranial detail v3 assets (43 release packages)

The complete [v3 one-by-one catalog](../../docs/assets/INTRACRANIAL_ASSET_CATALOG_V3.md) records every relationship, source/scale contract, geometry summary, transitive exclusion, and both non-published hold records. The tables below are the release runtime index.

### HRA neural detail (15)

These static generic-atlas layers share the established project brain frame. Preserve semantic children and use cutaways/visibility variants; do not stack overlapping opaque hierarchy levels or call them patient anatomy.

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 66 | [frontal_cortex_parcellation_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/frontal_cortex_parcellation_v3.usdz) | **Frontal cortical parcellation.** Named bilateral HRA frontal cortical gyri and lobules retained as separate semantic children in the established brain frame. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 67 | [parietal_cortex_parcellation_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/parietal_cortex_parcellation_v3.usdz) | **Parietal cortical parcellation.** Named bilateral HRA parietal gyri and lobules, including pre/postcentral and association regions, retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 68 | [temporal_cortex_parcellation_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/temporal_cortex_parcellation_v3.usdz) | **Temporal cortical parcellation.** Named bilateral HRA temporal gyri, poles, auditory planes, and temporal fusiform cortex retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 69 | [occipital_cortex_parcellation_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/occipital_cortex_parcellation_v3.usdz) | **Occipital cortical parcellation.** Named bilateral HRA occipital gyri, poles, cuneus, lingual, and occipital fusiform regions retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 70 | [insular_opercular_cortex_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/insular_opercular_cortex_v3.usdz) | **Insular and opercular cortex.** Named bilateral HRA short and long insular gyri, limen, agranular insula, and frontal operculum retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 71 | [cingulate_parahippocampal_cortex_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cingulate_parahippocampal_cortex_v3.usdz) | **Cingulate and parahippocampal cortex.** Named bilateral HRA cingulate, parahippocampal, perirhinal, piriform, and related medial cortical regions retained as semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 72 | [cerebellar_substructures_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cerebellar_substructures_v3.usdz) | **Cerebellar substructures.** Bilateral HRA lateral hemispheres, paravermis, vermis, deep nuclei, and cerebellar peduncles retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 73 | [brainstem_substructures_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/brainstem_substructures_v3.usdz) | **Brainstem substructures.** Bilateral HRA midbrain, pontine, medullary, collicular, peduncular, olivary, and red-nucleus structures retained as semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 74 | [basal_ganglia_deep_nuclei_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/basal_ganglia_deep_nuclei_v3.usdz) | **Basal ganglia and adjacent deep nuclei.** Named HRA caudate segments, putamen, pallidal segments, accumbens, subthalamic and substantia nigra regions, claustrum, and zona incerta. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 75 | [thalamic_hypothalamic_nuclei_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/thalamic_hypothalamic_nuclei_v3.usdz) | **Thalamic and hypothalamic nuclei.** Detailed HRA thalamic nuclei, hypothalamic regions, geniculate and habenular nuclei, mammillary region, and pineal body without overlapping broad parent volumes. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 76 | [hippocampal_amygdala_limbic_nuclei_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/hippocampal_amygdala_limbic_nuclei_v3.usdz) | **Hippocampal, amygdala, and limbic nuclei.** Named HRA hippocampal head/body/tail, source-backed amygdala nuclei, basal forebrain, bed nucleus, and septal nuclei retained as children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 77 | [ventricular_spaces_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/ventricular_spaces_v3.usdz) | **Ventricular spaces and connecting channels.** Source HRA lateral-ventricle segments, third and fourth ventricles, cerebral aqueduct, and central canal. These are atlas space surfaces, not a fluid simulation or measured CSF volume. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 78 | [major_white_matter_regions_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/major_white_matter_regions_v3.usdz) | **Major forebrain and hindbrain white-matter regions.** Bilateral HRA broad forebrain and hindbrain white-matter source volumes, kept separate from detailed tract assets because the source hierarchy overlaps them. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 79 | [commissural_sensory_pathways_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/commissural_sensory_pathways_v3.usdz) | **Major commissural and sensory pathways.** Source HRA corpus callosum, fornix, anterior commissure, mammillothalamic, optic, and olfactory structures retained as separate semantic children. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |
| 80 | [neural_detail_registered_review_assembly_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/neural_detail_registered_review_assembly_v3.usdz) | **Registered neural-detail unilateral reveal assembly.** An opaque registered review assembly with the right cortical parcels and broad white-matter parent volumes omitted to reveal bilateral deep source structures. Generic, non-patient-specific atlas anatomy; not validated for diagnosis, treatment planning, navigation, or clinical decision-making. Static generic atlas anatomy; specialist review required. |

### Cranial support detail (16 release-eligible)

The release-safe cranial manifest contains 15 independent layers plus the cranial-nerve review assembly. Attribution and ShareAlike obligations apply. The assembly replaces its nine nerve-group components while active.

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 81 | [cranial_nerve_olfactory_i_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_olfactory_i_bilateral_v3.usdz) | **Cranial nerve I — bilateral olfactory nerves.** Bilateral source-named olfactory nerve geometry registered to the shared cranial frame. Static generic atlas anatomy; specialist review required. |
| 82 | [cranial_nerve_optic_ii_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_optic_ii_bilateral_v3.usdz) | **Cranial nerve II — bilateral optic nerves.** Bilateral source-named optic nerve geometry; eyeballs are intentionally excluded to avoid duplicating the existing eye asset. Static generic atlas anatomy; specialist review required. |
| 83 | [cranial_nerves_ocular_motor_iii_iv_vi_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerves_ocular_motor_iii_iv_vi_v3.usdz) | **Cranial nerves III, IV and VI — ocular motor group.** Bilateral oculomotor, trochlear and abducens nerves as six separately named child meshes. Static generic atlas anatomy; specialist review required. |
| 84 | [cranial_nerve_trigeminal_v_expanded_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_trigeminal_v_expanded_v3.usdz) | **Cranial nerve V — expanded trigeminal pathways.** Source-named bilateral trigeminal roots and major ophthalmic, maxillary and mandibular divisions for spatial orientation. Static generic atlas anatomy; specialist review required. |
| 85 | [cranial_nerve_facial_vii_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_facial_vii_bilateral_v3.usdz) | **Cranial nerve VII — bilateral facial nerves.** Bilateral facial nerves plus the separately named chorda tympani branches. Static generic atlas anatomy; specialist review required. |
| 86 | [cranial_nerve_vestibulocochlear_viii_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_vestibulocochlear_viii_v3.usdz) | **Cranial nerve VIII — vestibulocochlear group.** Bilateral VIII trunks and source-available vestibular/cochlear subdivisions; the atlas includes one unlatered cochlear mesh and one left-labelled curve. Static generic atlas anatomy; specialist review required. |
| 87 | [cranial_nerves_glossopharyngeal_ix_vagus_x_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerves_glossopharyngeal_ix_vagus_x_v3.usdz) | **Cranial nerves IX and X — lower cranial pathways.** Bilateral glossopharyngeal and vagus paths retained at their atlas-provided extents into the neck. Static generic atlas anatomy; specialist review required. |
| 88 | [cranial_nerve_accessory_xi_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_accessory_xi_bilateral_v3.usdz) | **Cranial nerve XI — bilateral accessory nerves.** Bilateral accessory nerve paths retained through the atlas-provided neck extent. Static generic atlas anatomy; specialist review required. |
| 89 | [cranial_nerve_hypoglossal_xii_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerve_hypoglossal_xii_bilateral_v3.usdz) | **Cranial nerve XII — bilateral hypoglossal nerves.** Bilateral hypoglossal nerve paths with exact source identities preserved. Static generic atlas anatomy; specialist review required. |
| 90 | [extraocular_muscles_orbital_support_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/extraocular_muscles_orbital_support_v3.usdz) | **Extraocular muscles and orbital support.** Bilateral extraocular muscles, levator palpebrae, common tendinous rings and trochleae without duplicating the existing eyeball asset. Static generic atlas anatomy; specialist review required. |
| 91 | [pituitary_adenohypophysis_neurohypophysis_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/pituitary_adenohypophysis_neurohypophysis_v3.usdz) | **Pituitary gland — anterior and posterior lobes.** Two exact source meshes separating the adenohypophysis and neurohypophysis in the registered cranial frame. Static generic atlas anatomy; specialist review required. |
| 92 | [nasal_cavity_paranasal_spaces_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/nasal_cavity_paranasal_spaces_v3.usdz) | **Nasal cavity and available paranasal spaces.** Nasal mucosa/septal context, bilateral inferior conchae, ethmoid air-cell groups, and the separately available frontal and sphenoid sinus spaces. Static generic atlas anatomy; specialist review required. |
| 93 | [pharyngeal_upper_airway_context_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/pharyngeal_upper_airway_context_v3.usdz) | **Pharyngeal and upper-airway context.** Source-defined nasopharynx, oropharynx, laryngopharynx, soft palate and epiglottis for swallowing and airway orientation. Static generic atlas anatomy; specialist review required. |
| 94 | [muscles_of_mastication_bilateral_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/muscles_of_mastication_bilateral_v3.usdz) | **Bilateral muscles of mastication.** Bilateral temporalis, superficial/deep masseter and medial/lateral pterygoid components retained separately. Static generic atlas anatomy; specialist review required. |
| 95 | [head_neck_orientation_muscles_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/head_neck_orientation_muscles_v3.usdz) | **Major head and neck orientation muscles.** Selected bilateral head/neck muscles that establish facial, submandibular and cervical spatial orientation without attempting a complete myology atlas. Static generic atlas anatomy; specialist review required. |
| 96 | [cranial_nerves_complete_assembly_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_nerves_complete_assembly_v3.usdz) | **Cranial nerves I–XII review assembly.** Review assembly combining all source-supported I–XII cranial nerve group assets while retaining every semantic child. Static generic atlas anatomy; specialist review required. |

### Scale-separated conceptual micro detail (12)

Every package below is magnified, non-histologic, non-quantitative, non-patient-specific, and not registered to the head. A persistent “magnified conceptual view — not to anatomical scale” warning is mandatory. The teaching-set assembly replaces all eleven individual vignettes while active.

| # | Runtime file | Description and runtime note |
|---:|---|---|
| 97 | [blood_brain_barrier_neurovascular_unit_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/blood_brain_barrier_neurovascular_unit_conceptual_v3.usdz) | **Blood-brain barrier and neurovascular-unit teaching model.** Opened capillary with endothelial layer, tight-junction seams, basement membrane, pericyte, astrocyte endfeet, and magnified RBC context. Use only in the separate micro teaching stage. |
| 98 | [capillary_endothelium_tight_junctions_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/capillary_endothelium_tight_junctions_conceptual_v3.usdz) | **Capillary endothelium and tight-junction close-up.** Flattened endothelial-cell sheet with nuclei, basement membrane, conceptual tight-junction seams, and pericyte context. Use only in the separate micro teaching stage. |
| 99 | [formed_blood_elements_magnified_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/formed_blood_elements_magnified_v3.usdz) | **Magnified formed blood elements.** Scale-separated red blood cells, a generic leukocyte cue, and platelet forms with illustrative granules. Use only in the separate micro teaching stage. |
| 100 | [platelet_fibrin_thrombus_microstructure_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/platelet_fibrin_thrombus_microstructure_conceptual_v3.usdz) | **Conceptual platelet-fibrin thrombus microstructure.** Opened vessel context with entrapped RBCs, platelet-rich cues, fibrin strands, and a textured clot-volume reference. Use only in the separate micro teaching stage. |
| 101 | [multipolar_neuron_detailed_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/multipolar_neuron_detailed_conceptual_v3.usdz) | **Detailed multipolar-neuron teaching model.** Generic soma, nucleus, dendrites, enlarged spine cues, axon, and terminal branches. Use only in the separate micro teaching stage. |
| 102 | [astrocyte_capillary_endfeet_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/astrocyte_capillary_endfeet_conceptual_v3.usdz) | **Astrocyte and capillary-endfeet teaching model.** Branching astrocyte morphology with enlarged endfeet approaching an opaque capillary context. Use only in the separate micro teaching stage. |
| 103 | [oligodendrocyte_myelinated_axons_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/oligodendrocyte_myelinated_axons_conceptual_v3.usdz) | **Oligodendrocyte and myelinated-axon teaching model.** Generic oligodendrocyte with processes connected to several simplified myelin internodes. Use only in the separate micro teaching stage. |
| 104 | [myelinated_axon_node_of_ranvier_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/myelinated_axon_node_of_ranvier_conceptual_v3.usdz) | **Myelinated axon and node-of-Ranvier close-up.** Continuous axon core with separated myelin internodes, surface-ring cues, and enlarged channel-location markers. Use only in the separate micro teaching stage. |
| 105 | [chemical_synapse_closeup_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/chemical_synapse_closeup_conceptual_v3.usdz) | **Chemical-synapse teaching close-up.** Presynaptic axon terminal, enlarged vesicles, cleft particles, postsynaptic dendrite, and generic receptor-location cues. Use only in the separate micro teaching stage. |
| 106 | [choroid_plexus_csf_interface_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/choroid_plexus_csf_interface_conceptual_v3.usdz) | **Choroid-plexus and CSF-interface teaching model.** Simplified capillary folds with epithelial-cell cues and non-quantitative CSF direction markers. Use only in the separate micro teaching stage. |
| 107 | [ischemic_tissue_zones_conceptual_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/ischemic_tissue_zones_conceptual_v3.usdz) | **Conceptual ischemic tissue-zone teaching model.** Opaque layered surrounding, at-risk, and core teaching regions with non-quantitative microvessel context. Use only in the separate micro teaching stage. |
| 108 | [intracranial_micro_teaching_set_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/intracranial_micro_teaching_set_v3.usdz) | **Intracranial microanatomy teaching-set review assembly.** Review-only gallery of all eleven scale-separated microanatomy vignettes; use individual packages at runtime. Use only in the separate micro teaching stage. |

## Representative surgical-tool v3 assets (26 release packages)

These original, unbranded packages are recognition props for two mutually
exclusive educational branches. They are **representative, not exhaustive**:
they do not define a complete tray, required order, access route, device system,
sterile setup, or appropriate procedure for a patient. Stage labels mean only
where a clinician-reviewed lesson may introduce a category. All geometry is
static, with optional qualitative kinematic pickup/rotation; there is no force,
depth, trajectory, pressure, flow, energy, device sizing, compatibility,
navigation, tissue interaction, or training model.

The tool release-number column occupies entries 109–134 in the 145-file
publishing index. The same packages are full-build records 111–136 in
[`MASTER.md`](../../MASTER.md), which retains held records 92 and 98 in the
build sequence.

### Endovascular support tools (12)

These packages belong only under the endovascular branch and the applicable
`EVT-*` stage root. Route, technique, contrast/flush, anesthesia, aspiration,
suite-control, and access-hemostasis choices remain conditional. Review
assemblies replace their components and must never be co-loaded with them.

| Release # | Runtime file | Description and stage/use rule |
|---:|---|---|
| 109 | [vascular_access_needle_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/vascular_access_needle_educational_v3.usdz) | **Generic vascular-access needle concept.** Optional `EVT-02_ARTERIAL_ACCESS` recognition prop. It does not select femoral, radial, or another route and encodes no gauge, angle, depth, or puncture technique. |
| 110 | [vascular_access_wire_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/vascular_access_wire_educational_v3.usdz) | **Generic vascular-access wire concept.** Optional `EVT-02` transition cue, separate from the intracranial v2 guidewire inspection model. No coating, diameter, length, motion, or vessel-interaction meaning. |
| 111 | [introducer_sheath_dilator_set_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/introducer_sheath_dilator_set_educational_v3.usdz) | **Generic introducer sheath and dilator set.** Optional `EVT-02` access-support view. Dimensions, taper, valve, sidearm, insertion depth, compatibility, and sequence are illustrative. |
| 112 | [guide_catheter_hemostatic_valve_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/guide_catheter_hemostatic_valve_educational_v3.usdz) | **Generic guide catheter and rotating hemostatic valve.** Optional `EVT-03_GUIDE_ACCESS`/`EVT-05_DISTAL_DELIVERY` proximal-support category. It is not a navigation path, named catheter curve, valve setting, or connector specification. |
| 113 | [aspiration_pump_canister_tubing_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/aspiration_pump_canister_tubing_educational_v3.usdz) | **Generic aspiration pump, canister, and tubing.** Show only for clinician-selected `EVT-06B_CONTACT_ASPIRATION` or `EVT-06C_COMBINED`. No vacuum, pressure, duration, aspirate volume, alarm, connection, or efficacy is encoded. |
| 114 | [contrast_manifold_syringe_flush_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/contrast_manifold_syringe_flush_educational_v3.usdz) | **Generic contrast manifold, syringe, and flush system.** Conditional `EVT-04_BASELINE_ANGIOGRAPHY`/`EVT-07_VERIFICATION` support. It contains no fluid identity, dose, route, stopcock position, pressure, timing, renal/allergy decision, or protocol. |
| 115 | [torque_device_y_connector_accessories_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/torque_device_y_connector_accessories_educational_v3.usdz) | **Generic torque device, Y-connector, and accessories.** Optional `EVT-03`/`EVT-05` accessory-recognition view. No torque magnitude, seal setting, connection order, wire manipulation, or compatibility claim. |
| 116 | [puncture_site_hemostasis_options_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/puncture_site_hemostasis_options_educational_v3.usdz) | **Generic puncture-site hemostasis options.** `EVT-08_WITHDRAWAL_HEMOSTASIS` alternatives/adjuncts, not a simultaneous setup. Route, method, pressure, deployment, timing, monitoring, and aftercare remain clinician/local-protocol decisions. |
| 117 | [sterile_endovascular_instrument_tray_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/sterile_endovascular_instrument_tray_educational_v3.usdz) | **Generic sterile endovascular instrument tray.** Optional `EVT-01_SUITE_SETUP` visual anchor. It is deliberately incomplete and does not establish counts, packaging, medications, sterility assurance, sharps handling, or an institutional checklist. |
| 118 | [angiography_suite_controls_educational_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/angiography_suite_controls_educational_v3.usdz) | **Generic angiography-suite controls.** External equipment context for `EVT-01`, `EVT-04`, or `EVT-07`. Button/pedal mapping, radiation, table motion, injector operation, emergency functions, and operator workflow are absent. |
| 119 | [vascular_access_setup_review_assembly_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/vascular_access_setup_review_assembly_v3.usdz) | **Vascular-access review assembly.** Review-table replacement for the needle, access wire, sheath/dilator, and hemostasis-option packages. It is non-registered, non-sterile, non-chronological, and transitively excludes all four components. |
| 120 | [endovascular_tools_workflow_review_assembly_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/endovascular_tools_workflow_review_assembly_v3.usdz) | **Endovascular support-tool workflow review assembly.** Non-chronological gallery replacing all ten components and the nested access assembly. It is not a procedure-room setup, required device list, sequence, or patient plan. |

### Open-cranial tools (14)

Every package below is `open_neurosurgery_only`, prohibited from ordinary EVT,
and hidden until
`clinician_selected_hemorrhage_or_decompression_only` is confirmed. Open
evacuation, minimally invasive evacuation, decompression, closure, and optional
CSF access are conditional branches rather than one inevitable sequence.

| Release # | Runtime file | Description and stage/use rule |
|---:|---|---|
| 121 | [surface_marking_ruler_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/surface_marking_ruler_set_open_neurosurgery_v3.usdz) | **Generic surface marker and flexible ruler set.** `OPEN-01_POSITION_PREP` orientation context only. Markings are non-calibrated and define no incision, coordinate, measurement, or plan. |
| 122 | [scalpel_dissector_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/scalpel_dissector_set_open_neurosurgery_v3.usdz) | **Generic scalpel and blunt dissector set.** Non-graphic `OPEN-02_SCALP_EXPOSURE` recognition prop. It encodes no blade choice, incision, tissue plane, depth, force, or technique. |
| 123 | [scalp_retractor_hemostat_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/scalp_retractor_hemostat_set_open_neurosurgery_v3.usdz) | **Generic scalp retractor and hemostat set.** Optional `OPEN-02` exposure/hemostasis category. Do not animate tissue contact or infer retraction force, clamp pressure, duration, or efficacy. |
| 124 | [perforator_craniotome_system_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/perforator_craniotome_system_open_neurosurgery_v3.usdz) | **Generic perforator and craniotome system concepts.** `OPEN-03_BONE_ACCESS` detail replacing/supplementing the overlapping prototype drill view. No speed, torque, trajectory, cutting, heat, protective-stop, or safety behavior. |
| 125 | [bone_flap_fixation_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/bone_flap_fixation_set_open_neurosurgery_v3.usdz) | **Generic bone-flap fixation plates and screws.** `OPEN-07A_CRANIOTOMY_CLOSURE` only when the reviewed branch replaces the flap. Prohibited for decompressive-craniectomy leave-off; no implant material, dimensions, compatibility, placement, or torque. |
| 126 | [dural_scissors_hooks_forceps_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/dural_scissors_hooks_forceps_set_open_neurosurgery_v3.usdz) | **Generic dural scissors, hook, and forceps set.** `OPEN-04_DURAL_ACCESS` recognition view. It does not define an opening pattern, corridor, clearance, trajectory, or technique. |
| 127 | [bipolar_forceps_irrigation_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/bipolar_forceps_irrigation_set_open_neurosurgery_v3.usdz) | **Generic bipolar forceps and irrigation set.** Optional `OPEN-05A_OPEN_EVACUATION`/`OPEN-06_HEMOSTASIS_INSPECTION` context. No electrical/thermal energy, fluid identity/rate, temperature, sealing, or efficacy. |
| 128 | [suction_microdissector_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/suction_microdissector_set_open_neurosurgery_v3.usdz) | **Generic suction and microdissector set.** Optional `OPEN-05A`/`OPEN-06` view that replaces the overlapping prototype `suction_and_forceps` close-up. No pressure, flow, tissue removal, manipulation, bleeding, or completion metric. |
| 129 | [brain_spatula_retractor_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/brain_spatula_retractor_set_open_neurosurgery_v3.usdz) | **Generic brain spatula and retractor set.** Conditional `OPEN-05A` recognition only. Placement, corridor, tissue contact, width choice, pressure, duration, deformation, and safety are deliberately absent. |
| 130 | [microscope_microinstrument_tray_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/microscope_microinstrument_tray_open_neurosurgery_v3.usdz) | **Generic microscope-compatible microinstrument tray.** Optional detached `OPEN-04`/`OPEN-05A` comparison layout. It is not a microscope model, complete tray, sterile configuration, optical specification, or operative setup. |
| 131 | [dural_closure_suture_patch_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/dural_closure_suture_patch_set_open_neurosurgery_v3.usdz) | **Generic dural closure needle, suture, and patch set.** Branch-appropriate `OPEN-07A`/`OPEN-07B` material-category explanation. It encodes no suture/patch selection, closure pattern, tension, watertightness, compatibility, or result. |
| 132 | [conditional_csf_access_instrument_set_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/conditional_csf_access_instrument_set_open_neurosurgery_v3.usdz) | **Conditional generic CSF-access instrument set.** Hidden by default; available only at `OPEN-EVD_OPTIONAL` after a separate specialist gate, replacing the detailed view of `optional_evd_system`. No target, trajectory, depth, placement, drainage height, pressure, waveform, or management instruction. |
| 133 | [cranial_access_tools_review_assembly_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/cranial_access_tools_review_assembly_open_neurosurgery_v3.usdz) | **Cranial-access tools review assembly.** Review-table replacement for the five surface/exposure/bone-access component sets. Transitive exclusions are mandatory; layout is not a sterile tray, patient registration, or procedure sequence. |
| 134 | [intradural_closure_tools_review_assembly_open_neurosurgery_v3.usdz](vision_pro_stroke_kit_v2/exports/usdz/intradural_closure_tools_review_assembly_open_neurosurgery_v3.usdz) | **Intradural and closure tools review assembly.** Review-table replacement for six dural/microsurgical/protection/tray/closure sets. It intentionally excludes conditional CSF access and encodes no required order or operative arrangement. |

## Adaptive visual-comfort asset (1 release package)

This package is a reduced-graphic orientation alternative for a viewer who
explicitly requests less detail. It is generic educational media, not an
anxiety treatment or diagnostic output. The muted pastel palette is a design
hypothesis that requires representative-user and human-factors testing.

| Release # | Runtime file | Description and runtime rule |
|---:|---|---|
| 135 | [brain_orientation_calm_educational_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/brain_orientation_calm_educational_v1.usdz) | **Comfort-oriented generic brain orientation.** External bilateral cortex, cerebellum, and brainstem with matte high-roughness materials and no vessels, blood, clot, lesion, incision, deep structures, instruments, or dense labels. It derives from `brain_anatomy_realistic_v2`, replaces rather than overlays the detailed brain while active, and must keep Restore Original and full clinician-approved information available. |

The host application owns selection. Use an explicit self-reported preference
or a governed facilitator choice; never derive a clinical anxiety label from
pupil, gaze, or body movement. The
[adaptive endpoint](../../Services/AdaptiveAssetService/README.md) returns
transparent, reversible presentation recipes and reports this package only as
a display-blocked review candidate for the `overview` tier until an external
governed release approves the exact asset version.

Release records:

- [Asset notes](../../docs/assets/source-notes/ADAPTIVE_VISUALS_ASSET_NOTES_V1.md)
- [Source provenance and CC BY change notice](../../docs/assets/research/ADAPTIVE_VISUALS_SOURCE_PROVENANCE_V1.md)
- [Technical and visual validation](../../docs/assets/validation/ADAPTIVE_VISUALS_VALIDATION_V1.md)
- [Endpoint research and safety contract](../../docs/adaptive-visuals/RESEARCH_AND_SAFETY.md)

## Optional spatial-care environment assets (10 release packages)

These original, self-contained packages provide the warm consultation-room
composition visible in the interface target board. They contain no anatomy,
people, hands, text, case data, controls, lights, cameras, or clinical objects.
They are **disabled by default**: use system passthrough on Vision Pro and the
selected Simulator environment during simulator work. Load this module only for
an explicitly selected fully immersive developer demo or governed design
review. The blank feature-wall centre is reserved for app-native content.

All nine independent components share `experience_floor_origin`. Load either
selected components or the complete assembly—never both.

| Release # | Runtime file | Description and runtime rule |
|---:|---|---|
| 136 | [calm_consultation_room_shell_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/calm_consultation_room_shell_v1.usdz) | **Warm consultation-room architectural shell.** Open-front 7.2 × 6.2 m room with oak floor, warm plaster boundaries, baseboards, framed side window, and open-centre ceiling perimeter. It is a visual scale scaffold, not verified physical clearance. |
| 137 | [curved_feature_wall_architecture_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/curved_feature_wall_architecture_v1.usdz) | **Curved hero feature wall.** Rounded central backdrop, walnut acoustic rhythm, low ledge, and abstract non-text identity backer. Keep its centre blank for SwiftUI/RealityKit attachments. |
| 138 | [modular_lounge_seating_set_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/modular_lounge_seating_set_v1.usdz) | **Modular lounge seating.** Two softened sofa compositions for the rear family/waiting zones. They are virtual composition cues—not physical seating to sit on, lean against, or collide with. |
| 139 | [consultation_armchair_pair_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/consultation_armchair_pair_v1.usdz) | **Family/presenter armchair pair.** Teal and sand chairs framing the central anatomy zone. They encode no identity, permission, role state, or tracked seat position. |
| 140 | [round_spatial_display_dais_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/round_spatial_display_dais_v1.usdz) | **Round spatial-display dais and rug.** Central plinth, restrained teal ring, and orientation points under the hero anchor. The marks are aesthetic—not calibration, measurement, collision, or safe-space indicators. |
| 141 | [low_table_side_table_set_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/low_table_side_table_set_v1.usdz) | **Low coffee and side-table set.** Rounded noninteractive room furniture used only for balance and scale. It contains no records, controls, or clinical supplies. |
| 142 | [clinical_credenza_storage_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/clinical_credenza_storage_v1.usdz) | **Closed consultation-room credenza.** Generic walnut storage and privacy-neutral decor with no equipment, medication, document, or manufacturer meaning. |
| 143 | [calm_botanical_planter_set_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/calm_botanical_planter_set_v1.usdz) | **Botanical planter set.** Three modeled planters with stems, branches, and 42 leaves. Plants are visual landmarks and make no calming, therapeutic, or anxiety-reduction claim. |
| 144 | [ambient_lighting_fixture_set_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/ambient_lighting_fixture_set_v1.usdz) | **Ambient fixture geometry.** Two floor lamps, ceiling rings, and wall sconces. Meshes are non-emissive; the host app owns IBL, RealityKit lights, exposure, and device profiling. |
| 145 | [spatial_care_consultation_environment_assembly_v1.usdz](vision_pro_stroke_kit_v2/exports/usdz/spatial_care_consultation_environment_assembly_v1.usdz) | **Registered full-room assembly.** Review/demo convenience package containing all nine components at the shared floor origin. It transitively excludes every component and is not the default patient environment. |

The module manifest also supplies suggested anchors for landing, case carousel,
hero head, guidance/evidence attachments, topic rail, magnified vignette, and
comfort controls. These are authoring starting points, not comfort or safety
guarantees. See the [environment notes](vision_pro_stroke_kit_v2/SPATIAL_CARE_ENVIRONMENT_ASSET_NOTES_V1.md),
[provenance](vision_pro_stroke_kit_v2/SPATIAL_CARE_ENVIRONMENT_SOURCE_PROVENANCE_V1.md),
and [validation](vision_pro_stroke_kit_v2/validation/SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md).

### Full-build records excluded from release (2)

| Build-record ID | Status | Publishing-tree rule |
|---|---|---|
| `middle_inner_ear_bilateral_v3` | `HOLD_FOR_INNER_EAR_LICENSE_REVIEW` | Binary and runtime-manifest record omitted pending source/licence clearance or verified replacement. |
| `cranial_support_registered_assembly_v3` | `HOLD_FOR_INNER_EAR_LICENSE_REVIEW` | Binary and runtime-manifest record omitted because the assembly contains the held ear geometry. |

Preview renders that visibly contain either held package are omitted as well.

### Known tool-catalog gaps

The 26 tool packages intentionally do not complete every stage. The current
release has no dedicated access-ultrasound model, diagnostic or balloon-guide
catheter variant, radiation-shielding set, neurosurgical head holder, manual
rongeur/periosteal-elevator set, operating microscope/illumination model,
generator console, patties/hemostatic-material set, external surgical
suction/irrigation console, skin-stapler/navigation-pointer concept, or complete
external EVD leveling/drainage system. Reuse the existing generic context where
appropriate or omit the concept; never infer that an absent prop is clinically
unnecessary. See the
[stage audit](../../docs/assets/research/SURGICAL_TOOL_STAGE_AUDIT_V3.md) for the
full gap and duplication analysis.

## Manifests

- [Prototype-v1 manifest](vision_pro_stroke_kit/asset_manifest.json)
- [Core realistic-v2 manifest](vision_pro_stroke_kit_v2/asset_manifest_v2.json)
- [Head-detail-v2 manifest](vision_pro_stroke_kit_v2/asset_manifest_head_details_v2.json)
- [Cranial-vascular-v2 manifest](vision_pro_stroke_kit_v2/asset_manifest_cranial_vascular_v2.json)
- [Blood-flow-v2 manifest](vision_pro_stroke_kit_v2/asset_manifest_bloodflow_v2.json)
- [Thrombectomy-device-v2 manifest](vision_pro_stroke_kit_v2/asset_manifest_devices_v2.json)
- [Neural-detail-v3 manifest](vision_pro_stroke_kit_v2/asset_manifest_neural_detail_v3.json)
- [Release-safe cranial-detail-v3 manifest](vision_pro_stroke_kit_v2/asset_manifest_cranial_detail_v3.json)
- [Intracranial-micro-v3 manifest](vision_pro_stroke_kit_v2/asset_manifest_intracranial_micro_v3.json)
- [Endovascular-support-tools-v3 manifest](vision_pro_stroke_kit_v2/asset_manifest_endovascular_tools_v3.json)
- [Open-cranial-tools-v3 manifest](vision_pro_stroke_kit_v2/asset_manifest_open_cranial_tools_v3.json)
- [Adaptive-visuals-v1 manifest](vision_pro_stroke_kit_v2/asset_manifest_adaptive_visuals_v1.json)
- [Spatial-care-environment-v1 manifest](vision_pro_stroke_kit_v2/asset_manifest_spatial_care_environment_v1.json)

Manifest `usdz` paths are relative to the corresponding kit directory. Keep
the package layout intact or rewrite paths intentionally in the app's catalog
loader. The retained `usdc` fields describe upstream working/interchange
outputs; those duplicate working files are intentionally not committed in this
runtime-only asset pull request. Load the packaged `usdz` path.

## RealityKit loading guidance

Copy selected assets into the app bundle or an `.rkassets` package, resolve the
file URL from the matching manifest record, and load it asynchronously:

```swift
import RealityKit

let entity = try await Entity(contentsOf: assetURL)
entity.name = manifestRecord.id
```

Route `adaptive_visuals_v1` only to a detached
`ExperiencePlacementRoot/AdaptivePresentationRoot`. Fail closed while either
the endpoint or release record says `display_authorized: false`. After an
external governed review approves the exact package and presentation policy,
the calm orientation asset may temporarily replace—but never overlay or
co-load with—the detailed source brain. Restore the source before medical
detail is shown. Runtime material/visibility edits remain sidecars owned by the
application; do not bake them destructively into the atlas USDZ.

Route `spatial_care_environment_v1` only to
`ExperiencePlacementRoot/OptionalEnvironmentRoot`. Prefer no module asset in
ordinary mixed/passthrough or Simulator-scene presentation. In the gated
synthetic fully immersive mode, load the assembly or selected components at
the shared floor origin; generate only deliberate coarse static collisions and
never treat virtual walls, floors, furniture, rug, or dais as verified real
space. All interface panels and runtime lighting remain app-owned.

Do not apply another axis correction: the exported USD stages already use Y-up
and metres. Center inspection views using visual bounds. Load combined hero
assemblies lazily, and use the separate opaque layers for reveal/toggle flows.
Filter or reject any future record whose `license_review_status` starts with
`HOLD_`; the current release-safe cranial manifest omits both held records.

Route every `endovascular_tools_v3` record only to the gated endovascular stage
specified by the tool-stage audit. Route every `open_cranial_tools_v3` record
only to `OpenCranialRoot` after the explicit clinician-selected
hemorrhage/decompression gate; fail closed in ordinary EVT. Treat
`stage_tags`, narrative adjacency, and review-gallery layout as descriptive
education metadata rather than operating instructions or a required sequence.
Recursively enforce each assembly's component/exclusion list before loading.

Never center, fit, or register a `microscopic_conceptual_separate` package
inside `HeadRegisteredRoot`. Open it in a separate teaching stage and keep the
magnification, conceptual/nonquantitative, and non-patient-specific warnings
visible for the entire time the asset is shown.

The blood-flow animation is a baked illustrative transform animation. Discover
its imported resource through `availableAnimations`, play it explicitly, and
offer a replay action. It is not a fluid solver, CFD output, perfusion estimate,
or patient measurement.

## Patient-use boundary

These assets must not be used for diagnosis, triage, treatment selection,
surgical planning, navigation, device sizing, haemodynamic calculation, or
outcome prediction. A specialist must review the selected anatomy, colours,
scale, labels, procedure sequence, and patient-facing language before use.
