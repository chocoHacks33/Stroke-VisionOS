# Developer preview handoff

## Purpose

The Adaptive Visual Lab is a local integration harness for exercising the
adaptive presentation endpoint before a native visionOS application exists. It
is intentionally a developer tool, not a patient-facing experience and not a
3D renderer. The current service/API version is 0.2.0 and supports Python 3.9+.

Run the service and open `http://127.0.0.1:8765/`. The interface, catalog API,
adaptation API, job polling, and draft downloads stay on the same loopback
origin. No external scripts, fonts, analytics, or network resources are used.

## Structure

| Surface | Responsibility |
|---|---|
| `/`, `/ui`, `/ui/` | Packaged control-panel HTML |
| `/ui/app.css` | Responsive visual system, abstract recipe sketch, and reduced-motion behavior |
| `/ui/app.js` | Form state, path-free catalog search, API requests, recipe inspection, copy helpers, and generation polling |
| `GET /v1/catalog` | Sorted path-free asset metadata, adaptation-profile summaries, entity-map summaries, and content revisions |
| `POST /v1/visual-adaptations` | Policy recipe plus exact package-revision-bound child-index application plan |
| `GET /v1/jobs/{job_id}` | Existing asynchronous draft status |
| `GET /v1/artifacts/{job_id}/{filename}` | Existing display-blocked review downloads |

Static routes use an exact allowlist rather than converting arbitrary URLs into
filesystem paths. The server applies a self-only Content Security Policy,
same-origin opener/resource policies, no-referrer policy, frame denial,
camera/microphone/location/motion-sensor denial, MIME sniffing protection, and
`Cache-Control: no-store`.

## What the visual preview means

The CSS composition is a presentation-policy sketch. It responds to the
returned tier, tint, blood/particle opacity, semantic group visibility, label
ceiling, and motion settings so a developer can inspect the recipe quickly. It
does not load the USDZ, reproduce the asset geometry, prove visual comfort, or
show what a patient would see. In particular, the displayed opacity and LOD
values are policy requests: the executable plan uses discrete visibility with
no runtime alpha operations and preserves source geometry because no runtime
LOD variant is available.

The following remain visible throughout the panel:

- developer-preview status;
- `patient_display_authorized=false`;
- the non-diagnostic, no-biometric boundary;
- review gating for the calm orientation candidate and generated drafts; and
- the requirement to preserve and restore the source.

The packaged runtime data contains one profile and one exact selector record
for each of 135 assets. The captured RealityKit topology includes 7,243
entities, 3,472 model entities, and 24 authored animation resources. Package
SHA-256 plus child-index paths make selector resolution exact for those package
revisions. Semantic grouping remains deterministic presentation routing, not
clinical or anatomical validation, and requires external review.
These JSON resources ship from `adaptive_asset_service/runtime_profiles/`;
their deterministic builders remain in `profiles/`.

## Native visionOS handoff

The developer-preview
[`RealityKitAdaptivePlanApplier.swift`](clients/RealityKitAdaptivePlanApplier.swift)
now exercises the exact-plan boundary, and
[`ValidateRealityKitAdaptivePlan.swift`](tools/ValidateRealityKitAdaptivePlan.swift)
loads real USDZ packages through that executor on macOS. These are reference
sources only: neither file is integrated into a visionOS app or authorized for
patient display. The frozen executor SHA-256 is
`a57a53f7c15ecc343ba25e3f13152e89659d1fd36f551be5f82d20c98823dbe2`.

When an actual app scaffold is added, keep the service policy contract and make
the app provide every runtime fact required by the executor:

1. Bundle `realitykit_entity_bindings.json` and
   `catalog_adaptation_profiles.json` as code-signed, read-only resources and
   create `AdaptiveLocalPlanAuthorization` from those URLs. Do not authorize
   against downloaded or mutable JSON.
2. Load the selected USDZ only through
   `RealityKitAdaptivePlanSession.load(contentsOf:)`. It hashes before and after
   `Entity.load(contentsOf:)` and binds the resulting root to the stable byte
   count/SHA-256. Reject any revision change.
3. Decode the endpoint response separately, then pass the app's explicit
   expected audience, detail tier, and motion preference. These must match the
   response; they cannot be inferred from it after the fact.
4. Pass `.developerPreview`, never `.patientEducation`, while
   `patient_display_authorized` is false. The session restores any active
   developer adaptation before authorizing a new request, so a rejected patient
   transition clears rather than leaks the previous presentation.
5. Supply the correct animation baseline: `.pristineLoadedRoot` only before any
   app playback, or `.appManaged` with an
   `AdaptiveAnimationStateManaging` owner that captures/suspends and later
   recreates app-owned playback.
6. Present and declare the exact `fallback_if_unresolved` whenever
   `fallback_required` is true. Never silently discard a blocked semantic
   request. Treat a group absent from the package as not applicable.
7. Make the disclosure, comfort controls, required content warning, and
   progressive-disclosure UI ready before `apply`, and pass that readiness
   explicitly. Authorization fails closed if required UI is missing.
8. Let the main-actor executor traverse only `child_index_path` from its bound
   root and apply the authorized visibility, material, and authored-animation
   operations. Never select by entity name or debug path. Preserve discrete
   visibility, source alpha/geometry, mapped labels, and primary pathology.
9. Route Pause/Resume through `pauseAdaptiveAnimations()` and
   `resumeAdaptiveAnimations()`. On Exit/Return, preference replacement, or
   package unload, call `restoreOriginalPresentation()`; it restores captured
   visibility/materials, stops session-created controllers, and invokes the
   app-owned animation manager's restoration hook.
10. Keep annotations, pacing, label priority, the active-adaptation badge,
    changed properties, Show Less/More, Pause, Exit/Return, Restore Original,
    warnings, and fallback cards app-owned. Confirm patient
    participation/authorization and privacy before family mode.
11. Treat `brain_orientation_calm_educational_v1` only as a replacement
    candidate for the 19 profile-allowlisted neuro sources, never an overlay.
    Do not resolve it until the exact package and policy have a separate
    governed approval record.
12. Keep generated USDA and JSON outside the app catalog until provenance,
    specialist, accessibility, human-factors, and release gates are complete.
    The USDA embeds `displayAuthorized=false`; the JSON embeds
    `display_authorized=false`; both carry a review-draft role and the
    specialist/human-factors review gate.

The browser panel should remain available after native integration as a fast
contract-debugging surface. It should not become a shortcut around package
revision validation, external semantic review, or patient-display approval.

## Verification

From this directory:

```bash
python3 -m compileall -q adaptive_asset_service
python3 -m json.tool openapi.json >/dev/null
python3 -m unittest discover -s tests -v
osascript -l JavaScript adaptive_asset_service/static/app.js

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

/tmp/ValidateRealityKitAdaptivePlan \
  ../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/brain_anatomy_realistic_v2.usdz \
  /tmp/brain-overview-static-response.json \
  adaptive_asset_service/runtime_profiles/realitykit_entity_bindings.json \
  adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.json \
  patient overview static
```

The JavaScript command should parse the file and stop only because the
standalone JavaScript runtime has no browser `document`; a syntax error is a
failure. Runtime UI checks are also covered by the HTTP tests for HTML, CSS,
JavaScript, security headers, catalog metadata, and static-route traversal. The
current dependency-free suite passes 41/41 tests. The reference executor passes
strict macOS, `arm64-apple-xros27.0`, and
`arm64-apple-xros27.0-simulator` type-checks and an optimized macOS build. Its
135/135 real-package apply/restore run, 1,620-combination reconstruction check,
tamper and child-reorder rejection, context rollback, Pause/Resume, and
app-animation-manager lifecycle evidence are recorded in
[`ADAPTIVE_ENDPOINT_VALIDATION.md`](../../docs/adaptive-visuals/ADAPTIVE_ENDPOINT_VALIDATION.md)
and the client-specific boundary is in [`clients/README.md`](clients/README.md).
The harness arguments after its binary are source, response, local bindings,
local profiles, expected audience, expected detail, and expected motion. Add
`--fallback-presented` only when the response requires it, and add both family
flags for an authorized family request. Compilation, type-checking, and host
execution do not constitute a built or launched visionOS application.

Before a physical-device pilot, externally review the semantic classification
and separately test exact selectors, appearance, controls, accessibility,
Reduce Motion, reset behavior, and performance on Apple Vision Pro. None of the
local browser checks replace those gates.
