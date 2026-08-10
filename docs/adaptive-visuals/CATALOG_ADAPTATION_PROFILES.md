# Catalog-wide adaptation profiles

## Purpose

[`catalog_adaptation_profiles.json`](../../Services/AdaptiveAssetService/adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.json)
provides one conservative presentation profile for every released asset. It is
an application-routing contract for non-destructive visibility, material, and
motion changes. It is not an anxiety score, clinical classification, patient
display approval, or instruction to alter medical facts.

The profile is intentionally separate from the HTTP service implementation. A
client may intersect an endpoint recipe with the per-asset allowlist, but it
must never treat an action absent from the profile as implicitly safe.

## Coverage

- 135 profiles for 135 unique release-manifest asset IDs.
- 135 exact package-revision-bound selector records covering a RealityKit
  topology of 7,243 entities, 3,472 model entities, and 24 authored animation
  resources.
- 12 source manifests recorded with a deterministic aggregate SHA-256.
- Zero held IDs. `middle_inner_ear_bilateral_v3` and
  `cranial_support_registered_assembly_v3` are explicitly excluded.
- 16 review/combined assemblies with component and transitive never-co-load
  rules.
- 19 profile-allowlisted brain/neuroanatomy sources that may name the calm
  brain only as an externally reviewed orientation interstitial. The candidate
  is not content-equivalent and is never automatically displayed.
- Every profile has `patient_display_authorized: false`; the current release
  manifests all retain a required specialist or clinical review status.

## Profile fields

Each `profiles[]` record contains:

| Field | Meaning |
|---|---|
| `asset_id`, `title`, `module`, `source_manifest` | Stable catalog identity and source record |
| `content_categories` | Broad content routing such as neuroanatomy, vascular anatomy, environment, device, tool, pathology, micro-teaching, or review assembly |
| `graphic_content_tags` | Observable content flags such as blood, clot, haemorrhage, incision, cutaway, internal anatomy, catheter, instrument, flow cue, or microscopic detail |
| `presentation_intensity` | A conservative authoring heuristic: `minimal`, `low`, `moderate`, or `high`; never a person-level anxiety or distress measurement |
| `allowed_actions` | Closed allowlists for visibility, material, and motion changes |
| `replacement_rules` | Aggregate/component exclusions, semantic overlap exclusions, and optional orientation-candidate routing |
| `clinical_safeguards` | Required review status and fail-closed non-diagnostic, non-patient-specific, material-fact, and display-authorization boundaries |

Content categories and graphic-content tags are closed vocabularies in the
JSON Schema, and the generator rejects unknown values. The controlled action
vocabulary is embedded at the top of the JSON. Material actions are bounded,
display-blocked developer-preview transforms such as tint, saturation,
roughness, specular response, and emission; they carry no patient-display
authorization. Motion actions only remove or reduce authored motion; they never
authorize a new procedural animation. Semantic child hiding requires an exact,
package-revision-bound selector map. That map makes selector identity exact,
but its semantic classification still requires external clinical and
human-factors review. Profiles containing primary pathology do not allow
whole-asset hiding; the runtime map also protects primary semantic groups from
automatic hiding and protects mapped labels and primary-pathology materials
from automatic material changes.

## Runtime use

A safe client should:

1. Validate all release manifests and this profile's manifest-set digest.
2. Fail closed if the selected asset has no exact profile.
3. Obtain an explicit `self_report_preference` or governed facilitator choice;
   never derive a clinical state from gaze, pupil, hand, joint, or movement
   signals.
4. Intersect requested recipe actions with the profile's three allowlists and
   the exact package-SHA-bound selector map.
5. Apply only the returned visibility, material, and authored-animation
   operations as a reversible RealityKit sidecar. Use discrete visibility with
   no runtime alpha, preserve source geometry because no runtime LOD variant is
   available, and leave annotations, pacing, label priority, and controls to
   the app.
6. Enforce every `never_co_load_with_asset_ids` entry before scene composition.
7. Treat any orientation candidate as display-blocked unless the exact asset
   version has an external specialist and human-factors approval record.
8. Keep Show More/Less, Pause, Exit, and Restore Original available.

The source USDZ remains untouched and the runtime state must be restorable in
one action. Those technical safeguards do not prove that medical meaning is
preserved; the exact visual result requires external clinical and human-factors
review before patient display.

`presentation_intensity` describes the asset, not the viewer. It must not be
mapped to a diagnosis, severity label, treatment, or claim that a palette or
detail tier reduces anxiety. Human-factors and representative-user testing
remain mandatory before a patient-facing pilot.

## Replacement model

`role` is one of:

- `standalone` — no catalog aggregate relationship;
- `component` — belongs to at least one aggregate and must not be co-loaded
  with that aggregate;
- `aggregate` — replaces its listed components while active and never augments
  them; or
- `orientation_candidate` — a generic, non-equivalent orientation asset that
  remains display-blocked in the current release.

The file also records semantic exclusions that are not literal containment,
including broad-versus-detailed white-matter views, duplicate ventricular
representations, and documented legacy/detail overlaps for access, drill,
suction, and optional CSF-access views. A directed `replaces_asset_ids` entry
means only that the named overlap must be hidden while the replacement is
active; it does not claim clinical superiority, clinical equivalence, or
permission to use the asset in patient mode. The generator expands aggregate
membership transitively so a nested review assembly cannot bypass a component
exclusion.

## Rebuild and verify

From `Services/AdaptiveAssetService`:

```bash
python3 profiles/build_catalog_adaptation_profiles.py
python3 profiles/build_catalog_adaptation_profiles.py --check
python3 -m json.tool adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.json >/dev/null
python3 -m json.tool adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.schema.json >/dev/null
```

The builder fails if the catalog is not exactly 135 unique assets across 12
manifests, if a held ID appears, if an aggregate references an unknown asset,
if a profile grants patient display or anxiety inference, if material facts may
be removed, or if an action falls outside the controlled vocabulary. `--check`
also fails when a manifest changes without regenerating the profile.

Builder scripts remain in `profiles/`; packaged runtime JSON lives under
`adaptive_asset_service/runtime_profiles/` so an installed wheel uses the same
profile, schema, RealityKit topology, and binding files as the repository.

The machine-readable structure is documented by
[`catalog_adaptation_profiles.schema.json`](../../Services/AdaptiveAssetService/adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.schema.json).
