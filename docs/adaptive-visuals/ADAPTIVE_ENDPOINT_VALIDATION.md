# Adaptive visual endpoint validation

Validation date: 2026-08-09

## Outcome

Service/API 0.2.0 passes its local functional, privacy, catalog, and
artifact-safety checks. This is engineering evidence only; it is not clinical,
human-factors, regulatory, production-security, or physical Vision Pro
validation.

## Automated checks

From `Services/AdaptiveAssetService`:

```bash
python3 -m unittest discover -s tests -v
python3 -m json.tool openapi.json >/dev/null
python3 -m compileall -q adaptive_asset_service
```

Result: **41/41 tests passed**, the OpenAPI document parsed, and the Python
3.9-compatible package compiled. Coverage includes:

- packaged control-panel HTML, CSS, and JavaScript delivery with strict
  same-origin security headers and an exact static-route allowlist;
- path-free public catalog browsing with source-content revision binding;
- 135/135 catalog adaptation profiles and package-SHA-bound RealityKit selector
  records, loaded from packaged `adaptive_asset_service/runtime_profiles/`
  resources;
- topology and selector tamper rejection across 7,243 entities, 3,472 model
  entities, and 24 authored animation resources;
- canonical and compatibility endpoint routing;
- full request type and enum validation;
- rejection of pupil, gaze, joint-motion, biometric, and anxiety-score fields;
- path/traversal rejection and duplicate manifest-ID failure;
- rejection and connection closure for ambiguous, chunked, oversized, or
  body-bearing request framing before unconsumed bytes can become another
  request;
- private `0700` artifact directories and `0600` artifact files;
- unique request IDs across reused HTTP/1.1 connections and generic
  address-free connection-error logs;
- deterministic labelled demo simulation;
- explicit patient/family preference sources;
- Reduce Motion and static overrides;
- family authorization and privacy gates;
- transparent, reversible edit recipes and exact visibility/material/animation
  operation plans;
- protection of mapped labels, primary pathology materials, and every primary
  semantic group from automatic hiding;
- allowlisted logs that omit request bodies, asset IDs, preferences, seeds, and
  client addresses;
- asynchronous deterministic procedural drafts with no external USD reference;
- `display_authorized: false` response, artifact metadata/envelopes, and HTTP
  headers; and
- no patient-display approval endpoint.

An isolated PEP 517 wheel build produced
`stroke_vision_adaptive_asset_service-0.2.0-py3-none-any.whl`. A clean virtual
environment installed that wheel, found all four packaged runtime-profile JSON
resources, loaded the real 135-asset catalog, and initialized all 135 profiles
and 135 exact binding records. This specifically guards against a source-tree
test passing while an installed console script is missing its topology data.

## Full-catalog smoke test

The service indexed **135 assets across 12 manifests** from
`RealityKitContent/Assets`. Live loopback requests verified:

- `/healthz` reports `diagnostic_inference: false`;
- `/` serves the local developer preview and `GET /v1/catalog` returns all 135
  sorted public records without local or manifest paths, each with a profile and
  entity-map summary;
- `/healthz` reports 135 profiled and 135 entity-mapped assets;
- an edit request returns a source-preserving recipe and an exact
  package-revision-bound child-index application plan;
- the plan emits executable visibility, bounded developer-preview material, and
  authored-animation operations only; opacity uses discrete visibility with no
  alpha operation, runtime LOD is unavailable, and annotations, pacing, label
  priority, and controls remain app-owned;
- mapped labels and primary pathology receive no automatic material changes;
  primary semantic groups receive no automatic visibility changes;
- source USDZ bytes remain untouched and the plan requires a pre-edit state
  snapshot plus one-action restoration;
- `medical_content_preservation_status` remains
  `requires_external_clinical_and_human_factors_review` rather than asserting
  clinical preservation;
- edit completion remains separate from patient-display authorization; the
  prototype always returns `patient_display_authorized: false`, because a
  future governed release must approve the exact source, entity mapping, and
  adaptive policy/profile together;
- `simulated_demo` returns `simulated: true`, `non_diagnostic: true`, and uses no
  biometric input;
- a family request requires patient participation/authorization and privacy
  confirmation;
- overview exposes `brain_orientation_calm_educational_v1` only for the 19
  profile-allowlisted brain/neuroanatomy sources and only as an
  `orientation_asset_candidate` with its manifest review status,
  `display_authorized: false`, and the specialist/human-factors review gate;
- a generation request returns HTTP 202 and a deterministic abstract USDA
  review draft; and
- the generated USDA passes `usdchecker`, contains no external asset reference,
  and embeds the review-draft role, `displayAuthorized=false`, and review gate;
  its JSON companion embeds `display_authorized=false` and the same gate around
  the nested recipe.

The packaged browser control panel was also exercised against the live default
service. Catalog loading, overview/static selection, exact-plan generation, the
four-operation mapping summary, blocked orientation candidate, and false
patient-display gate rendered correctly; no browser console warning or error
was observed. This was visual developer QA, not a medical-asset render or a
substitute for Vision Pro testing.

## Native RealityKit developer-preview validation

The reference
[`RealityKitAdaptivePlanApplier.swift`](../../Services/AdaptiveAssetService/clients/RealityKitAdaptivePlanApplier.swift)
and its real-package
[`ValidateRealityKitAdaptivePlan.swift`](../../Services/AdaptiveAssetService/tools/ValidateRealityKitAdaptivePlan.swift)
harness were frozen for this validation at these SHA-256 revisions:

- executor: `a57a53f7c15ecc343ba25e3f13152e89659d1fd36f551be5f82d20c98823dbe2`;
- harness: `7c71b270039038fd3c930eba805d9ebffb8595b0917b56a8f15c92dfb17bc3a3`.

They passed these host and SDK checks from `Services/AdaptiveAssetService`:

```bash
xcrun --sdk macosx swiftc \
  -warnings-as-errors -strict-concurrency=complete -typecheck \
  clients/RealityKitAdaptivePlanApplier.swift \
  tools/ValidateRealityKitAdaptivePlan.swift

xcrun --sdk xros swiftc \
  -target arm64-apple-xros27.0 \
  -warnings-as-errors -strict-concurrency=complete -typecheck \
  clients/RealityKitAdaptivePlanApplier.swift \
  tools/ValidateRealityKitAdaptivePlan.swift

xcrun --sdk xrsimulator swiftc \
  -target arm64-apple-xros27.0-simulator \
  -warnings-as-errors -strict-concurrency=complete -typecheck \
  clients/RealityKitAdaptivePlanApplier.swift \
  tools/ValidateRealityKitAdaptivePlan.swift

xcrun --sdk macosx swiftc -O \
  -warnings-as-errors -strict-concurrency=complete \
  clients/RealityKitAdaptivePlanApplier.swift \
  tools/ValidateRealityKitAdaptivePlan.swift \
  -o /tmp/ValidateRealityKitAdaptivePlan
```

Result: strict macOS, `arm64-apple-xros27.0`, and
`arm64-apple-xros27.0-simulator` type-checks **PASS**; optimized macOS build
**PASS**.

The harness takes source, response, local bindings, local profiles, expected
audience, expected detail, and expected motion. A reproducible real-package
invocation is:

```bash
/tmp/ValidateRealityKitAdaptivePlan \
  ../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/brain_anatomy_realistic_v2.usdz \
  /tmp/brain-overview-static-response.json \
  adaptive_asset_service/runtime_profiles/realitykit_entity_bindings.json \
  adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.json \
  patient overview static
```

Add `--fallback-presented` only for a response with
`fallback_required: true`. Family runs require both `--family-authorized` and
`--family-privacy-confirmed`. `--patient-education` is a deliberate rejection
probe while the native contract remains display-blocked.

### Full-catalog native run

Canonical overview/static responses passed load, pre/post-load package hashing,
exact local binding/profile authorization, full-topology validation,
application, and restoration for **135/135 released USDZ packages**. This
included **30 responses requiring the documented fallback**, all run with the
matching app-presented fallback declaration.

| Native full-catalog aggregate | Result |
|---|---:|
| Real USDZ packages | 135 / 135 passed |
| Material entities applied | 3,154 |
| Material slots transformed | 3,154 |
| Visibility operations applied | 134 |
| Authored animation resources configured | 24 |
| Unsupported material slots | 0 |
| Required-fallback cases | 30 / 30 passed |

Every report retained `sourceAssetUnchanged: true` and
`patientDisplayAuthorized: false`; each run invoked
`restoreOriginalPresentation()` after application.

Independent static reconstruction checked every **asset × detail tier × motion
preference** combination: 135 assets × four detail tiers × three motion choices
= **1,620 combinations**, with **zero operation-set mismatch** against the
endpoint. Targeted real-package execution additionally covered static,
reduced-motion, and system-default playback behavior.

### Fail-closed and lifecycle checks

The negative matrix rejected forged or non-canonical selectors, material and
animation values, protected pathology changes, out-of-range presentation
values, recipe/asset or local revision mismatches, fallback bypass or
substitution, missing warning/progressive-disclosure readiness, missing family
participation/privacy gates, cross-package use, and patient execution context.
A separately reordered child hierarchy was also rejected by the complete
topology check rather than re-resolved by entity name.

`apply` restores an already-active developer adaptation before validating a
replacement. The context-transition rollback probe confirmed that an attempted
patient-context change is rejected with the original presentation restored.
Failure during application also rolled back captured visibility/material state.
Pause/Resume checks passed for session-created playback controllers.

The app-managed animation probe confirmed the complete lifecycle: the
integrating manager's preparation hook captured and suspended its playback
before an adaptive animation plan, the session restored its own state and
stopped its controllers, and the manager's restoration hook recreated the
app-owned playback state. `.pristineLoadedRoot` remains valid only before the
app starts playback.

This is a developer-preview executor, not an integrated visionOS app. The
strict SDK checks, host application/restoration, and static reconstruction do
not authorize patient display and do not establish simulator launch, physical
Vision Pro, clinical, human-factors, or production performance validation. See
[`clients/README.md`](../../Services/AdaptiveAssetService/clients/README.md) for
the integration boundary.

## Runtime performance boundary

This validation records no latency claim for the final mapped response. Measure
startup, response size, median/tail latency, main-actor application cost,
memory, frame timing, and thermal behavior after the reference executor is
integrated into a native app and the deployment path is fixed. Local loopback
timing would not establish Vision Pro, Wi-Fi, gateway, authentication, or
end-to-end RealityKit performance.

## Remaining release gates

- Put any non-loopback deployment behind authenticated authorization, TLS,
  rate limiting, retention/deletion policy, and reviewed audit controls.
- Have stroke clinicians and patient-education owners approve the semantic
  classification, protected groups, bounded material changes, and exact content
  that each tier may reveal or defer.
- Complete privacy, accessibility, human-factors, health-literacy, and
  representative patient/family testing.
- Integrate the reference executor into a visionOS app and test the app-owned
  animation snapshot/restoration path alongside annotations, pacing, and
  controls.
- Revalidate the exact package-SHA child-index selectors, material overrides,
  discrete visibility, absence of runtime alpha/LOD changes, reset,
  disclosure badge, Show More/Less, Pause, Exit, and Restore Original controls
  on physical Vision Pro hardware.
- Do not display a generated draft or the calm orientation candidate until the
  exact version has the required external review record.
