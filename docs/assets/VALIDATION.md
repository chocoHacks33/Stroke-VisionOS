# Asset validation record

Validated on 2026-08-08 and 2026-08-09 in macOS using Apple's USD tools and
RealityKit. Module reports retain their exact validation dates.

## Catalog integrity

- 135 release runtime USDZ packages: 65 original plus 43 non-held v3 detail
  packages, 26 v3 surgical-tool packages, and one adaptive visual derivative.
- 135 unique release-manifest IDs, basenames, and paths. All 69 v3 records and
  the adaptive derivative carry
  verified byte counts and SHA-256 values; the original package validation
  retains its payload-integrity evidence.
- Twelve manifests: five v2, one prototype-v1, five v3 module manifests, and
  one adaptive-visual manifest.
- No missing manifest-backed packages.
- `stroke_kit_asset_gallery.usdz` intentionally excluded.
- Runtime payload: 275,619,913 bytes (262.85 MiB).
- Largest package: 32,482,833 bytes; no selected file exceeds 50 MiB.
- The original 65 repository packages passed
  `/usr/bin/usdchecker --arkit --strict`: 65 pass, 0 fail.
- Fresh strict validation of the 43 exact v3 publishing copies:
  `/usr/bin/usdchecker --arkit --strict`: 43 pass, 0 fail.
- Fresh strict validation of the 26 exact tool-v3 publishing copies:
  `/usr/bin/usdchecker --arkit --strict`: 26 pass, 0 fail.
- Strict validation of the adaptive visual derivative:
  `/usr/bin/usdchecker --arkit --strict`: 1 pass, 0 fail.

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
- Service/API 0.2.0 passes 41/41 dependency-free unit tests, OpenAPI JSON
  parsing, Python 3.9 compilation, full-catalog lookup and content binding,
  packaged control-panel/security-header checks, path-free catalog browsing,
  biometric-field rejection, traversal rejection, privacy-safe logs,
  reversible edit plans, and display-blocked procedural generation.
- All 135 released assets have a fail-closed adaptation profile and an exact
  package-SHA-bound RealityKit child-index selector record. The captured
  topology covers 7,243 entities, 3,472 model entities, and 24 authored
  animation resources. Selector identity passed technical validation; semantic
  classification still requires external clinical and human-factors review.
- Executable plans contain visibility, bounded developer-preview material, and
  authored-animation operations only. They use discrete visibility without
  runtime alpha, expose no runtime LOD variant, leave annotations/pacing/controls
  app-owned, protect mapped labels and primary-pathology materials, keep the
  source untouched/restorable, and explicitly leave medical-content
  preservation subject to external review.
- The new orientation model remains
  `REQUIRES_SPECIALIST_AND_HUMAN_FACTORS_REVIEW`. The endpoint exposes it only
  for the 19 allowlisted neuro source assets and only as
  `display_authorized: false`; neither a technical package pass nor an API
  response authorizes patient display. Generated USDA and JSON review artifacts
  also embed the false display flag and review gate.
- Detailed evidence is retained in
  [ADAPTIVE_VISUALS_VALIDATION_V1.md](validation/ADAPTIVE_VISUALS_VALIDATION_V1.md)
  and
  [ADAPTIVE_ENDPOINT_VALIDATION.md](../adaptive-visuals/ADAPTIVE_ENDPOINT_VALIDATION.md).

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

That simulator evidence predates the 26 tool packages. The tools have
package-level USD and RealityKit validation, but the complete 135-package
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
- Inner-ear source/licence clearance or replacement before either held build
  package can enter a release tree.
