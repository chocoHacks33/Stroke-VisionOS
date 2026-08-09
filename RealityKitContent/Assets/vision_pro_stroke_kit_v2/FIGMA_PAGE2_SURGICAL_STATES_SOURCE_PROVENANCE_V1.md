# Figma Page 2 surgical-state source provenance v1

## Provenance summary

This module registers and refines existing licensed/project-authored sources. It
does not fabricate new clinical anatomy and does not use FAB or a downloaded
unattributed model. Source geometry remains generic and non-patient-specific.

| Runtime package | Geometry source | Licence / classification | Derivative work |
|---|---|---|---|
| `scalp_access_closure_registered_conceptual_v1` | `external_head_scalp_realistic_v2`, HRA Skin Male, NIH 3D `3DPX-021016` v2 | CC BY 4.0 | Generic circular boolean opening in the registered source; original source-surface patch retained as the movable flap without cutter caps; existing `Scalp_Skin_PBR_v2` textures preserved. |
| `cranial_bone_access_closure_registered_conceptual_v1` | `skull_semantic_realistic_v2`, Visible Human Male Skull and Eyes, NIH 3D `3DPX-020591` v1.03 | CC BY 4.0 | Generic circular aperture in the registered parietal mesh; intersected source geometry retained as the detached bone flap; warm matte presentation material. |
| `dural_access_closure_registered_conceptual_v1` | `dura_mater_conceptual_v2`, existing project-authored conceptual hull registered to HRA brain | Project-authored conceptual geometry; underlying HRA registration CC BY 4.0 | Generic circular opening; original source-surface patch retained as the movable flap without cutter caps; existing `Dura_Mater_PBR_v2` textures preserved. |
| `intracerebral_hematoma_registered_conceptual_v1` | Legacy project collection `ASSET__ich_hematoma` | Project-authored original conceptual geometry | Old context, labels, and arrows excluded; selected lobes rescaled, repositioned, smoothed, and recolored in the v2 generic brain frame. |
| `cerebral_edema_registered_conceptual_v1` | Legacy project collection `ASSET__edema_swelling` | Project-authored original conceptual geometry | Constraint ring and pressure arrows excluded; selected volume rescaled, repositioned, deterministically soft-lobulated, smoothed, and recolored in the v2 generic brain frame. |

Preserve the two NIH 3D titles, identifiers, versions, and CC BY 4.0
attributions in downstream distribution. This record does not alter upstream
licences or the licences of separately composed kit assets.

## Look-development reference

`textures/source/figma_page2_v1/holographic_linework_emission_reference_v1.png`
was generated with OpenAI built-in ImageGen as a non-anatomical presentation
look-development reference. Its SHA-256 is
`913b00955ecf9b6458b260b9dc6f2c71e04f2d10cf7767505534bb643fa7f433`.
Its provenance JSON SHA-256 is
`0512544c154a13c6cea34ff9ee890a409dcb968a1fe715168cd1687a09edf6fd`.

It was **not used in final runtime materials**, **not packed into any USDZ**, and
has no anatomical or clinical authority. The source PBR textures and restrained
project materials described above are the final runtime materials.

## Reproducible authoring record

| Field | Value |
|---|---|
| Module | `figma_page2_surgical_states_v1` |
| Generator | `source/build_figma_page2_surgical_states_v1.py` |
| Editable master | `blender/figma_page2_surgical_states_v1.blend` |
| Authoring application | Blender 5.2.0 LTS |
| Runtime packages | `exports/usdz/<asset-id>.usdz` |
| Evidence stages | `exports/usdc/<asset-id>.usdc` |
| Manifest | `asset_manifest_figma_page2_surgical_states_v1.json` |
| Runtime scale / axis | metres / Y-up |
| Runtime cameras, lights, UI, animation, physics | None |

Rebuild from the editable-kit root:

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  --python source/build_figma_page2_surgical_states_v1.py

python3 source/validate_figma_page2_surgical_states_v1.py
```

Any geometry, material, texture, transform, filename, export, or manifest change
invalidates the recorded hashes, bounds, and validation evidence. Regenerate and
revalidate rather than editing those values manually.

## Clinical and distribution status

The pathology objects are concepts, not segmentations. Source registration does
not create patient registration. Technical and provenance cleanliness do not
authorize diagnosis, planning, navigation, device sizing, training, outcome
prediction, or patient display. The entire experience still requires specialist,
human-factors, accessibility, privacy, representative-user, Simulator,
physical-device, and institutional review.
