# Asset licences

This repository does not currently apply one blanket licence to every asset.
Use each runtime package under the terms recorded below and retain the adjacent
source, attribution, and modification records when redistributing it.

## Original project assets

Eighty-one of the 135 release-catalog USDZ packages are original project work:
43 baseline packages, 12 conceptual micro-detail packages, and 26 surgical-tool
packages. No
repository-wide licence has yet been selected for those files, so public access
to the repository must not be interpreted as an additional licence grant.

The generated material maps and preview images are supporting project artwork.
They are generic educational visuals, not patient data, histology, diagnostic
evidence, or clinically validated tissue measurements.

### Surgical-tool v3 project work

All 12 `endovascular_tools_v3` packages and all 14
`open_cranial_tools_v3` packages are original, unbranded project geometry and
materials. Their generators use no third-party mesh, CAD, product scan,
catalogue image, texture, HDRI, logo, packaging, or ImageGen output. Category
references in the audit/provenance documents are evidence for terminology only;
they are not licences for copied product geometry and confer no medical-device
clearance or clinical validity.

The tool USDZs, previews, manifests, and project-authored documentation remain
subject to the repository's unresolved licence decision. Preserve the source
and modification records in
[PROVENANCE.md](PROVENANCE.md), and do not imply a trademark, manufacturer
association, freedom-to-operate determination, or permission beyond the rights
actually granted by the project owner.

## NIH 3D and Human Reference Atlas derivatives — CC BY 4.0

The baseline 11 packages below, all 15 neural-detail-v3 packages, and the
adaptive visual derivative include geometry derived from NIH 3D / Human
Reference Atlas sources under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/):

- `brain_anatomy_realistic_v2.usdz`
- `brain_deep_structures_v2.usdz`
- `brain_ventricles_v2.usdz`
- `skull_semantic_realistic_v2.usdz`
- `thrombectomy_registered_hero_v2.usdz`
- `external_head_scalp_realistic_v2.usdz`
- `external_head_scalp_cutaway_v2.usdz`
- `eyes_context_realistic_v2.usdz`
- `dura_mater_conceptual_v2.usdz`
- `dura_mater_cutaway_conceptual_v2.usdz`
- `layered_head_cutaway_registered_v2.usdz`
- `brain_orientation_calm_educational_v1.usdz`

The 15 neural-detail packages are listed individually in the
[v3 catalog](INTRACRANIAL_ASSET_CATALOG_V3.md#neural-detail--14-hra-packages-plus-one-assembly)
and in the
[neural manifest](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_neural_detail_v3.json).
Their detailed acquisition, source hash, and modification record is retained in
[NEURAL_DETAIL_PROVENANCE_V3.md](research/NEURAL_DETAIL_PROVENANCE_V3.md).

The adaptive package uses selected external orientation structures from HRA
*Brain, Male* v1.01. They were recentered, joined by anatomical region,
decimated, smoothed, and recolored with matte pastel materials; deep anatomy,
vasculature, pathology, blood, and cut surfaces were deliberately omitted. Its
required attribution and change notice are in
[ADAPTIVE_VISUALS_SOURCE_PROVENANCE_V1.md](research/ADAPTIVE_VISUALS_SOURCE_PROVENANCE_V1.md).

Required creator, title, version, source URL, hashes, and modification notices
are retained under [`sources/nih3d`](sources/nih3d) and in
[`source-notes/V2_ATTRIBUTION.md`](source-notes/V2_ATTRIBUTION.md).

## Z-Anatomy and BodyParts3D derivatives — ShareAlike

The following 13 baseline packages and the 16 non-held cranial-detail-v3
packages include material derived through Z-Anatomy and BodyParts3D and must
retain the applicable attribution and ShareAlike terms:

- `cerebral_arteries_realistic_v2.usdz`
- `thrombectomy_registered_hero_v2.usdz`
- `falx_cerebri_atlas_v2.usdz`
- `tentorium_cerebelli_atlas_v2.usdz`
- `meningeal_partitions_atlas_v2.usdz`
- `layered_head_cutaway_registered_v2.usdz`
- `dural_venous_sinuses_realistic_v2.usdz`
- `internal_jugular_veins_realistic_v2.usdz`
- `dural_sinuses_jugulars_realistic_v2.usdz`
- `head_neck_veins_supplemental_v2.usdz`
- `head_neck_veins_expanded_realistic_v2.usdz`
- `neck_access_arteries_realistic_v2.usdz`
- `cranial_vascular_registered_assembly_v2.usdz`

The 16 published cranial packages are listed in the
[release-safe cranial manifest](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_cranial_detail_v3.json).
Retain the University of Dundee CAHID cranial-nerve CC BY 4.0 attribution
pending a definitive per-object source review, as recorded in
[CRANIAL_DETAIL_SOURCE_PROVENANCE_V3.md](research/CRANIAL_DETAIL_SOURCE_PROVENANCE_V3.md).

Required attributions:

- “Z-Anatomy — The libre 3D atlas of anatomy” —
  [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- “BodyParts3D — The Database Center for Life Science” —
  [CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/)

The preserved source notice is under
[`sources/z_anatomy`](sources/z_anatomy). The two mixed packages,
`thrombectomy_registered_hero_v2.usdz` and
`layered_head_cutaway_registered_v2.usdz`, contain both NIH CC BY and
Z-Anatomy/BodyParts3D ShareAlike material.

## Inner-ear licence hold

The source build also produced `middle_inner_ear_bilateral_v3` and
`cranial_support_registered_assembly_v3`, which contains that ear geometry.
Both are `HOLD_FOR_INNER_EAR_LICENSE_REVIEW` because the local atlas
documentation cites an adapted University of Dundee inner-ear work under
CC BY-NC-SA 4.0 without a sufficient per-object provenance ledger. Their
binaries and runtime-manifest records are deliberately absent from this
publishing tree. Do not distribute or restore them for hospital, commercial,
or runtime use until provenance and licence compatibility are cleared or the
geometry is replaced with a verified source.

## Preview and composite rule

Preview images and combined assemblies inherit the relevant terms of the assets
they depict or contain. A combined package is not a relicensing mechanism.
