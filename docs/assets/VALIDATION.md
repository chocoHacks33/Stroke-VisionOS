# Asset validation record

Validated on 2026-08-08, 2026-08-09, and 2026-08-10 in macOS using Apple's USD tools and
RealityKit. Module reports retain their exact validation dates.

## Catalog integrity

- 150 release runtime USDZ packages: 65 baseline plus 43 non-held v3 detail
  packages, 26 v3 surgical-tool packages, one adaptive visual derivative, and
  ten optional environment packages plus five Page 2 surgical-state packages.
- 150 unique release-manifest IDs, basenames, and paths. All 69 v3 records, the
  adaptive derivative, and all ten environment records carry
  verified byte counts and SHA-256 values; the original package validation
  retains its payload-integrity evidence.
- Fourteen manifests: five v2, one prototype-v1, five v3 module manifests, one
  adaptive-visual manifest, one spatial-care-environment manifest, and one
  Page 2 surgical-state manifest.
- No missing manifest-backed packages.
- `stroke_kit_asset_gallery.usdz` intentionally excluded.
- Runtime payload: 298,669,039 bytes (284.83 MiB).
- Largest package: 32,482,833 bytes; no selected file exceeds 50 MiB.
- The original 65 repository packages passed
  `/usr/bin/usdchecker --arkit --strict`: 65 pass, 0 fail.
- Fresh strict validation of the 43 exact v3 publishing copies:
  `/usr/bin/usdchecker --arkit --strict`: 43 pass, 0 fail.
- Fresh strict validation of the 26 exact tool-v3 publishing copies:
  `/usr/bin/usdchecker --arkit --strict`: 26 pass, 0 fail.
- Strict validation of the adaptive visual derivative:
  `/usr/bin/usdchecker --arkit --strict`: 1 pass, 0 fail.
- Strict validation of the optional environment module:
  `/usr/bin/usdchecker --arkit --strict`: 10 pass, 0 fail.
- Strict validation of the Page 2 surgical-state module:
  `/usr/bin/usdchecker --arkit --strict`: 5 pass, 0 fail.

## v2 technical gate

- `/usr/bin/usdchecker --arkit --strict`: 36 pass, 0 fail.
- RealityKit `Entity.load(contentsOf:)`: 36 pass, 0 fail.
- Nonzero RealityKit `ModelComponent` instances: 664.
- `cerebral_bloodflow_animation_v2.usdz`: 26 entities and 24 animation
  resources; authored duration four seconds.

## Prototype gate

- Repository-copy `/usr/bin/usdchecker --arkit --strict`: 29 pass, 0 fail.
- RealityKit load probe: 29 pass, 0 fail.
- Prototype packages remain clearly labelled as low-poly teaching assets.

## v3 detail gates

- Neural detail: 15/15 strict USD PASS and 15/15 RealityKit load PASS with
  nonzero renderable content.
- Cranial detail source build: 18/18 strict USD PASS and 18/18 RealityKit load
  PASS. The release tree includes only the 16 non-held packages; the ear package
  and ear-containing complete assembly are omitted.
- Intracranial micro detail: 12/12 strict USD PASS, 12/12 RealityKit load PASS,
  and dedicated preview coverage PASS for 12/12.
- Technical and preview success is not clinical validation. Micro-detail
  patient-facing interpretation remains HOLD pending persistent
  magnification/conceptual warnings and specialist review.
- Detailed evidence is retained in
  [NEURAL_DETAIL_ASSET_VALIDATION_V3.md](validation/NEURAL_DETAIL_ASSET_VALIDATION_V3.md),
  [CRANIAL_DETAIL_ASSET_VALIDATION_V3.md](validation/CRANIAL_DETAIL_ASSET_VALIDATION_V3.md),
  and
  [INTRACRANIAL_MICRO_ASSET_VALIDATION_V3.md](validation/INTRACRANIAL_MICRO_ASSET_VALIDATION_V3.md).

## v3 surgical-tool gates

- Endovascular support tools: 12/12 strict USD PASS and 12/12 RealityKit load
  PASS with nonzero renderable content; 12/12 packages have dedicated preview
  coverage.
- Open-cranial tools: 14/14 strict USD PASS and 14/14 RealityKit load PASS with
  nonzero renderable content; eight reviewed previews cover both assemblies and
  the principal independent categories, including the isolated conditional
  CSF-access set.
- All 26 source-to-publishing USDZ copies match their manifest byte counts and
  SHA-256 hashes. The two manifests contain unique IDs and paths with no overlap
  against the previous 110 build records.
- Technical success does not validate completeness, sterility, compatibility,
  operative sequence, clinical appropriateness, patient comprehension, device
  performance, training, or hospital readiness. All package behavior remains
  static or qualitatively kinematic.
- Detailed evidence is retained in
  [ENDOVASCULAR_TOOLS_VALIDATION_V3.md](validation/ENDOVASCULAR_TOOLS_VALIDATION_V3.md)
  and
  [OPEN_CRANIAL_TOOLS_ASSET_VALIDATION_V3.md](validation/OPEN_CRANIAL_TOOLS_ASSET_VALIDATION_V3.md).
- The separate
  [combined independent QA](validation/SURGICAL_TOOLS_COMBINED_INDEPENDENT_QA_V3.md)
  passed its technical, visual, manifest, package-integrity, duplicate-geometry,
  and workflow-contract gate for 26/26 packages and inspected all 20 final
  previews. It explicitly leaves the clinical-validity gate unpassed and
  outside the technical audit.

## Adaptive visual and endpoint gates

- `brain_orientation_calm_educational_v1`: 1/1 strict USD PASS and 1/1
  RealityKit load PASS with four non-empty model/material regions and finite
  positive bounds.
- Manifest byte count and SHA-256 match the published USDZ; the package is
  metre-scale, Y-up, self-contained, and contains no camera, light, or named
  graphic-content prim.
- The 1600 × 1200 preview passed visual inspection for framing, silhouette,
  tonal separation, and absence of blood, lesion, incision, or instrument
  content.
- The adaptive service passes 35/35 dependency-free unit tests, OpenAPI JSON
  parsing, Python compilation, full-catalog lookup, biometric-field rejection,
  traversal rejection, privacy-safe logs, reversible edit recipes, and
  display-blocked procedural generation. The three-tier GET/POST routes also
  pass frozen catalog/policy binding, exact source revision, stale-SHA 409,
  catalog-reload drift, same-size mid-hash mutation, duplicate-JSON-key,
  non-finite-number, path-free response, and malformed-framing tests.
- The new orientation model remains
  `REQUIRES_SPECIALIST_AND_HUMAN_FACTORS_REVIEW`. The endpoint exposes it only
  as `display_authorized: false`; neither a technical package pass nor an API
  response authorizes patient display.
- Detailed evidence is retained in
  [ADAPTIVE_VISUALS_VALIDATION_V1.md](validation/ADAPTIVE_VISUALS_VALIDATION_V1.md)
  and
  [ADAPTIVE_ENDPOINT_VALIDATION.md](../adaptive-visuals/ADAPTIVE_ENDPOINT_VALIDATION.md).

## Three-tier visual-detail catalog gates

- The deterministic pack covers 150/150 release assets across all 14 USDZ
  manifests, with exactly one primary category per asset and all 17 composite
  assembly-domain overrides.
- It emits exactly 450 unique virtual IDs: 150 each for `minimal`,
  `reduced80`, and `full`. All 150 full bindings match the observed source
  package byte count and SHA-256; all 300 lower tiers preserve the source and
  prohibit geometry mutation.
- The 14 categories × 3 tiers provide 42 complete structured parameter blocks.
  All normalized numeric series are bounded and monotonic; every `reduced80`
  semantic target is exactly `0.8`.
- The blood/flow rule is explicit: minimal uses sparse static markers with zero
  motion; reduced80 uses fewer flow/cell cues at slower speed; full remains
  source-authored. No tier claims CFD or quantitative physiology.
- Builder determinism, catalog/source integrity, Draft 2020-12 policy-schema
  evaluation, JavaScript selector behavior, missing/unknown-tier rejection,
  eight-resource manifest integrity, private-path absence, and the false
  patient-display/geometry-mutation gates all pass.
- The pack contains no additional USDZ geometry. Detailed evidence and the
  exhaustive asset-by-asset text map are in
  [`visual_detail_variants_v1`](../../RealityKitContent/InterfaceMedia/visual_detail_variants_v1/README.md).

## Spatial-care environment gates

- Ten packages: nine registered independent room components plus one complete
  registered assembly.
- `/usr/bin/usdchecker --arkit --strict`: 10/10 PASS.
- RealityKit `Entity.load(contentsOf:)`: 10/10 PASS with nonzero models,
  materials, and finite positive bounds.
- Exact manifest byte/SHA-256 checks, metre/Y-up/default-prim checks, package
  isolation, triangle budgets, and 10/10 1600 × 1200 preview coverage: PASS.
- No package contains a Camera or Light prim, external reference, patient/hand,
  anatomy/pathology, baked interface, or PHI-named prim.
- Assembly: 88,908 triangles and 2,618,451 bytes; all ten packages total
  5,269,986 bytes. The assembly replaces all nine components.
- System passthrough/Simulator scene remains the default, the synthetic room is
  disabled by default, and every record remains
  `patient_display_authorized=false`.
- Detailed evidence is retained in
  [SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/validation/SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md).

## Spatial-interface resource gates

- One interface manifest plus 14 supporting resources: scene presets, four
  fictional cases, three null evidence placeholders, eight null annotation
  requests plus schema, UI tokens, SF Symbols map, wordmark, four synthetic
  portraits, supporting storyboard, and ImageGen provenance.
- Manifest byte/SHA-256 integrity: 14/14 PASS. Five image hashes/dimensions,
  JSON parsing, SVG XML parsing, metadata/private-path scan: PASS.
- Scene dependencies: 32/32 references resolved against the pre-environment
  135-asset clinical/anatomy catalog; the optional room is governed separately
  by its own manifest and environment state.
- Right-M1 laterality guard, fictional-case/zero-PHI invariants,
  display-blocked evidence, and null-by-default annotation scaffold: PASS.
- The storyboard remains supporting/non-runtime and contains generated,
  unreviewed visible wording that must not be implemented as evidence or
  patient-facing copy.
- A third-party Draft 2020-12 schema validator was unavailable; deterministic
  structural/schema-invariant checks passed, and this limitation remains an
  explicit validation gap.
- Detailed evidence is retained in
  [SPATIAL_INTERFACE_V1_VALIDATION.md](validation/SPATIAL_INTERFACE_V1_VALIDATION.md).

## Figma Page 2 surgical-state and interface gates

- Five USDZ packages: 5/5 strict ARKit USD PASS and 5/5 desktop RealityKit
  load/model/material/finite-bounds PASS; exact manifest byte/SHA-256 integrity
  PASS.
- All packages use `/Asset`, metres, and Y-up; each contains one embedded stage
  and no missing/external package reference, Camera, Light, Physics, time-sampled
  animation, glass/text/UI, or hotspot prim.
- Required named scalp, bone, and dura flap entities are present. The source
  identity is the closed pose; animation remains host-owned and non-physical.
- Five 1600 × 1200 previews exist. Module contract checks cover exact IDs/eight
  recipes, realistic-brain defaults, open-scope/gate enforcement, zero-or-one
  pathology alternatives, closure entities, source classifications, look-dev
  hashes/non-runtime use, and `patient_display_authorized=false`: PASS.
- The ten-resource `figma_page2_surgical_interface_v1` pack passes exact
  byte/SHA-256 validation, JSON parsing, pathway separation, cross-pathway
  lockout, null copy/anchor binding, zero-PHI, native-UI ownership, and
  patient-display block: 10/10 PASS.
- Step 1's frozen composition resolves `brain_anatomy_realistic_v2`, registered
  scalp, and registered cranial bone. The three registered access layers inherit
  `HeadRegisteredRoot`; legacy tools require a separately reviewed placement.
- Technical passes do not establish anatomical/procedural validity, approved
  clinical copy, patient comprehension, Simulator/physical-device integration,
  performance, comfort, accessibility, privacy, hospital readiness, or patient
  display.
- Detailed module evidence is retained in
  [FIGMA_PAGE2_SURGICAL_STATES_VALIDATION_V1.md](../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/validation/FIGMA_PAGE2_SURGICAL_STATES_VALIDATION_V1.md);
  the interface pack's own validator reports its narrower integrity result.

## Viewer integration evidence

The prior 108-asset release catalog was also exercised in the separate local
production viewer used to make these assets. Its final Apple Vision Pro
simulator build contained **108 models and 9 manifests** in both the local and
installed app bundles. Both bundles passed strict code-sign verification;
source-to-local-to-installed comparison found zero model or manifest byte
mismatches; and both held packages were absent. Loaded-content captures were
visually checked for a neural-detail assembly, the cranial-nerve assembly, and
the blood-brain-barrier micro vignette. The micro view retained its persistent
“not to anatomical scale” warning.

That simulator evidence predates the 26 tool packages. The tools and Page 2
module have package-level USD and RealityKit validation, but the complete 150-package
catalog has not yet been bundled into or visually exercised by that viewer.

That production viewer is not the repository-owned Xcode application scaffold,
which does not exist yet. The result validates package integration in the local
simulator tool; it does not establish physical Vision Pro performance,
anatomical or clinical validity, hospital readiness, or implementation of the
planned repository experience.

Detailed module reports are retained in [`validation`](validation).

## Remaining gates

- Specialist clinical and human-factors review.
- Physical Apple Vision Pro visual, interaction, comfort, and accessibility
  review.
- On-device RealityKit Trace profiling of the final assembled experience.
- Patient-facing language and sequencing approval.
- Exact Page 2 pathway/copy/anchor/attachment review, Simulator integration,
  physical-device comfort/accessibility testing, and registered-anatomy versus
  legacy-tool placement review.
- Inner-ear source/licence clearance or replacement before either held build
  package can enter a release tree.
