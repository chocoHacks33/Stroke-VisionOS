# Asset provenance and transformation record

## Scope

The committed release catalog contains 150 unique, manifest-backed runtime USDZ
packages: the baseline 65 (36 higher-detail v2 and 29 prototype-v1), 43
non-held v3 detail packages, 26 v3 surgical-tool packages, and one adaptive
visual derivative, plus ten original optional consultation-environment
packages and five Page 2 surgical-state packages. The complete source build
produced 71 v3 packages plus the adaptive derivative, environment module, and
Page 2 module, for 152 unique build records, but the two inner-ear-containing
packages are on a licence hold and are deliberately absent from this publishing
tree. The unmanifested `stroke_kit_asset_gallery.usdz` review composite remains
excluded because it duplicates prototype geometry.

No raw scans, patient records, identifiers, private source archives, Blender
working files, or vendor GLBs are included in this pull request.

## Coordinate and export conventions

- Runtime unit: metres (`metersPerUnit = 1`).
- USD up axis: Y.
- Delivery format: USDZ containing USD-compatible geometry and PBR materials.
- Blender source orientation was converted and verified during USD export; the
  runtime packages must not receive an additional minus-90-degree correction.
- Combined assemblies are review conveniences. Prefer separately toggleable
  opaque layers in the patient-facing experience.

## NIH 3D / Human Reference Atlas sources

### Brain

- Work: HRA Brain, Male, NIH 3D `3DPX-020960`, version `1.01`.
- Source: <https://3d.nih.gov/entries/20960?version=1.01>
- Changes: semantic selection, recentering, region joining, practical runtime
  reduction, smoothing, UV preparation, project PBR materials, and USD export.

### Skull and eyes

- Work: Visible Human Male Skull and Eyes, NIH 3D `3DPX-020591`, version
  `1.03`.
- Source: <https://3d.nih.gov/entries/20591?version=1.03>
- Changes: scale normalization to metres, recentering, reorientation, baked
  transforms, practical runtime reduction, and USD export while preserving
  semantic separation.

### Skin

- Work: Skin, Male, NIH 3D `3DPX-021016`, version `2`.
- Source: <https://3d.nih.gov/entries/21016?version=2>
- Changes: head/upper-neck crop, capped crop boundary, registration in the HRA
  brain frame, UVs, runtime geometry, cutaway variant, and project PBR maps.

Exact source hashes and notices are retained under [`sources/nih3d`](sources/nih3d).

## Z-Anatomy / BodyParts3D sources

- Z-Anatomy source: <https://github.com/Z-Anatomy/Models-of-human-anatomy>
- BodyParts3D source: <https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html>
- Changes: selected named arterial, meningeal, venous, sinus, jugular, and neck
  access structures; reduced curve/mesh complexity; converted curves where
  needed; registered to the generic brain frame; applied project materials;
  and exported independently toggleable USDZ layers.
- Bony frontal and sphenoid air sinuses were explicitly excluded from the
  cranial-vascular selection.

## Neural-detail v3

The 15 neural packages select 275 source-semantic meshes from NIH 3D / HRA
*Brain, Male* `3DPX-020960` v1.01 under CC BY 4.0. Eight overlapping broad or
alternate parent meshes were deliberately omitted in favour of detailed
children. No missing neural structure was invented. The exact semantic
allocation, source hash, transformation, and attribution are recorded in
[NEURAL_DETAIL_PROVENANCE_V3.md](research/NEURAL_DETAIL_PROVENANCE_V3.md) and
[hra_neural_detail_semantic_audit_v3.json](research/hra_neural_detail_semantic_audit_v3.json).

## Cranial-detail v3

The release-safe cranial set contains 15 independent Z-Anatomy / BodyParts3D
layers and one cranial-nerve review assembly selected from exact source object
names. Source curves were tessellated within recorded limits; missing anatomy
was not mirrored, bridged, or inferred. The full build's ear asset and complete
support assembly are not published because of the recorded inner-ear licence
hold. See
[CRANIAL_DETAIL_SOURCE_PROVENANCE_V3.md](research/CRANIAL_DETAIL_SOURCE_PROVENANCE_V3.md)
and [cranial_detail_source_qc_v3.json](research/cranial_detail_source_qc_v3.json).

## Original procedural and generated work

The thrombus, generic procedure devices, artery cutaway, lumen cues,
biconcave-cell teaching models, microcirculation vignette, direction markers,
and four-second transform animation are original project constructions.

The source texture folder includes project-created base-color maps and derived
OpenGL normal/roughness maps. The ImageGen prompt summaries and hashes are in
[`source-notes/IMAGEGEN_HEAD_DETAIL_MATERIALS.md`](source-notes/IMAGEGEN_HEAD_DETAIL_MATERIALS.md).

The 12 micro-detail-v3 packages are original procedural teaching geometry.
Three project-owned ImageGen base-colour references support appearance only;
they are not microscopy, histology, anatomy, pathology, or clinical evidence.
The exact prompts, refinement record, output paths, and hashes are retained in
[`source-notes/IMAGEGEN_INTRACRANIAL_MICRO_V3.md`](source-notes/IMAGEGEN_INTRACRANIAL_MICRO_V3.md).

## Surgical-tool v3

The 12 endovascular-support packages and 14 open-cranial packages are original,
unbranded procedural project work. No third-party mesh, CAD, product scan,
online model, catalogue image, texture, logo, trademark, packaging, or ImageGen
output is used. Generic category references were consulted only to audit broad
terminology and conditional stage context; no product dimensions, controls,
connector standards, proprietary geometry, instructions, or performance data
were copied.

The endovascular module contains ten independent category packages and two
review assemblies. It supports conditional educational associations spanning
suite setup, vascular access, guide support, angiography, distal delivery,
aspiration-based variants, and access-site hemostasis. The open module contains
twelve independent packages and two review assemblies, is
`open_neurosurgery_only`, and requires the
`clinician_selected_hemorrhage_or_decompression_only` gate. The review
assemblies duplicate their component geometry and must replace, never augment,
those components.

Canonical release records:

- [Endovascular asset notes](source-notes/ENDOVASCULAR_TOOLS_ASSET_NOTES_V3.md)
- [Endovascular provenance](research/ENDOVASCULAR_TOOLS_PROVENANCE_V3.md)
- [Open-cranial asset notes](source-notes/OPEN_CRANIAL_TOOLS_ASSET_NOTES_V3.md)
- [Open-cranial provenance](research/OPEN_CRANIAL_TOOLS_SOURCE_PROVENANCE_V3.md)
- [Stage, duplication, gap, and handoff audit](research/SURGICAL_TOOL_STAGE_AUDIT_V3.md)

These are representative recognition props, not exhaustive trays, marketed
devices, operative sequences, sterile configurations, planning/navigation data,
or training simulators. Mesh dimensions are display bounds, not product
measurements; all allowed behavior is static or qualitatively kinematic.

## Adaptive visual-comfort derivative v1

`brain_orientation_calm_educational_v1` selects external orientation structures
from HRA *Brain, Male* `3DPX-020960` v1.01 under CC BY 4.0. The source was
recentered, joined into four display regions, reduced for runtime use, smoothed,
and assigned project-authored matte pastel materials. Vessels, blood, pathology,
incisions, cut surfaces, deep anatomy, instruments, and dense labels were not
included. No marketplace mesh, vendor CAD, patient data, or generated anatomy
was introduced.

The palette and reduced visual density are a comfort-oriented design hypothesis,
not evidence of anxiety reduction. The asset performs no behavioural inference
and may be selected only through a visible, reversible host-application policy.
See
[ADAPTIVE_VISUALS_SOURCE_PROVENANCE_V1.md](research/ADAPTIVE_VISUALS_SOURCE_PROVENANCE_V1.md)
and
[ADAPTIVE_VISUALS_ASSET_NOTES_V1.md](source-notes/ADAPTIVE_VISUALS_ASSET_NOTES_V1.md).

## Spatial-care consultation environment v1

The nine independent room components and one registered assembly are wholly
project-authored procedural Blender geometry and materials. No third-party
mesh, texture, stock asset, portrait, manufacturer design, patient information,
or ImageGen output is embedded in these USDZ packages. The user-supplied image
was used only as a high-level mood/composition reference; its pixels, text,
people, hands, interface panels, portraits, and anatomy were not copied.

The environment is optional presentation geometry. System passthrough on
Vision Pro—or the configured Simulator scene—remains the default; all packages
remain `patient_display_authorized=false`. Exact construction, exclusions, and
validation are in
[SPATIAL_CARE_ENVIRONMENT_SOURCE_PROVENANCE_V1.md](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/SPATIAL_CARE_ENVIRONMENT_SOURCE_PROVENANCE_V1.md)
and
[SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/validation/SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md).

## Spatial-interface v1 media and configuration

The non-geometry pack contains original JSON/SVG configuration, four synthetic
fictional case-card portraits, and one supporting ImageGen storyboard. The
portraits are fictional identifiers only—not real people, patient records,
identity/demographic evidence, or clinical evidence. The storyboard is a
non-runtime design target; generated visible wording inside it is explicitly
not approved implementation or evidence copy.

Built-in ImageGen was used only for the four portraits and storyboard. The
recorded prompt intent, dimensions, exact output hashes, source-reference hash,
and use restrictions are preserved in
[image_generation_provenance_v1.json](../../RealityKitContent/InterfaceMedia/spatial_care_interface_v1/image_generation_provenance_v1.json).
The pack's scene presets reference existing manifest-backed anatomy; they do
not generate, modify, or validate anatomy. Glass, cards, controls, labels,
hands, natural input, passthrough, and accessibility remain native visionOS/app
responsibilities. See
[SPATIAL_INTERFACE_V1_NOTES.md](source-notes/SPATIAL_INTERFACE_V1_NOTES.md)
and
[SPATIAL_INTERFACE_V1_VALIDATION.md](validation/SPATIAL_INTERFACE_V1_VALIDATION.md).

## Figma Page 2 surgical states v1

The new geometry module refines registered sources already in the kit:

- `scalp_access_closure_registered_conceptual_v1` derives from HRA Skin Male,
  NIH 3D `3DPX-021016` v2 (CC BY 4.0); a generic source-surface opening/flap
  was derived and the existing scalp PBR maps were preserved.
- `cranial_bone_access_closure_registered_conceptual_v1` derives from Visible
  Human Male Skull and Eyes, NIH 3D `3DPX-020591` v1.03 (CC BY 4.0); a generic
  parietal aperture/source-derived flap was created.
- `dural_access_closure_registered_conceptual_v1` derives from the existing
  project-authored conceptual HRA-registered dura; a generic opening/flap was
  derived and the existing dura PBR maps were preserved. Underlying HRA terms
  remain applicable.
- `intracerebral_hematoma_registered_conceptual_v1` and
  `cerebral_edema_registered_conceptual_v1` refine earlier project-authored
  conceptual geometry by excluding old labels/arrows/context, then rescaling,
  registering, smoothing, and recolouring it in the generic v2 brain frame.

No FAB, stock, commercial CAD, patient scan, Figma export, or unattributed
geometry is used. The built-in ImageGen linework PNG is an optional
non-anatomical look-development reference only; its exact provenance/hash is in
the manifest, it is not packed into a USDZ, and it is not used by final runtime
materials. Exact transformation and attribution records are in
[FIGMA_PAGE2_SURGICAL_STATES_SOURCE_PROVENANCE_V1.md](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/FIGMA_PAGE2_SURGICAL_STATES_SOURCE_PROVENANCE_V1.md).

## Figma Page 2 interface contract v1

The ten-resource non-geometry pack is project-authored JSON, Markdown, and
Python validation logic. The supplied Figma page and interface image informed
composition/interaction intent only. No Figma export, artwork, copied clinical
copy, anatomy, portrait, stock asset, ImageGen output, PHI, or patient record is
included. All scene bindings, anchors, clinical copy, citations, locales, and
review records fail closed pending approval. See the pack's
[provenance record](../../RealityKitContent/InterfaceMedia/figma_page2_surgical_interface_v1/figma_page2_surgical_interface_provenance_v1.json).

## Clinical meaning boundary

Every model is generic and non-patient-specific. Conceptual layers, clot size,
flow direction markers, magnified blood cells, cutaway thicknesses, colours,
and procedure-device proportions are educational abstractions. They are not
measurements, CFD results, a treatment recommendation, or evidence for a real
patient. The source audit and patient-replacement requirements are recorded in
[INTRACRANIAL_DETAIL_SOURCE_AUDIT.md](research/INTRACRANIAL_DETAIL_SOURCE_AUDIT.md).
