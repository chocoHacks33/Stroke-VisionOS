# RealityKit adaptive-plan reference client

[`RealityKitAdaptivePlanApplier.swift`](RealityKitAdaptivePlanApplier.swift) is
the developer-preview reference executor for the service's exact RealityKit
application plan. It is paired with the macOS command-line validation harness
[`ValidateRealityKitAdaptivePlan.swift`](../tools/ValidateRealityKitAdaptivePlan.swift).
The frozen executor revision documented here has SHA-256
`a57a53f7c15ecc343ba25e3f13152e89659d1fd36f551be5f82d20c98823dbe2`.

This source is **not integrated into a visionOS application**, is not a
patient-facing renderer, and does not authorize patient display. It executes
only an explicitly declared developer-preview presentation and fails closed on
any package, topology, local-policy, response, request-context, fallback, or UI
readiness mismatch.

## Security and application contract

On the main actor, `RealityKitAdaptivePlanSession` provides these boundaries:

- `load(contentsOf:)` hashes the USDZ before and after `Entity.load`, rejects a
  package that changes during loading, and securely binds the resulting root
  entity and package byte count/SHA-256 in one session;
- `AdaptiveLocalPlanAuthorization` loads the exact binding and catalog-profile
  JSON bundled as code-signed app resources, verifies their digests against the
  endpoint response, and reconstructs the only canonical operation set allowed
  for the observed package, profile, tier, and motion preference;
- authorization checks the entire recorded model/animation topology before
  applying any operation, including entity names, child-index paths, material
  slot counts, and authored-animation counts;
- `apply` requires the explicit expected audience, detail tier, and motion
  preference; `.developerPreview` execution context; an animation baseline;
  the app's fallback state; and confirmation that the required disclosure,
  comfort controls, content warning, and progressive-disclosure UI are ready;
- family execution additionally requires both patient participation or
  authorization and the app's privacy confirmation;
- `.patientEducation` is rejected while the contract remains display-blocked.
  Because `apply` restores any active adaptation before validating a replacement
  request, a rejected patient-context transition cannot leave the old adaptive
  presentation on screen;
- every target resolves only from the session's loaded root using its exact
  `child_index_path`; entity names and debug paths are validation diagnostics,
  never runtime selectors; and
- failures after application begins roll back the captured presentation state.

After authorization, the session applies exact `isEnabled` changes, transforms
existing `PhysicallyBasedMaterial`, `SimpleMaterial`, and `UnlitMaterial` slots
while preserving source alpha, preserves unsupported material types, and
configures only the authored animation resources named by the plan. The USDZ
bytes remain unchanged.

`pauseAdaptiveAnimations()` and `resumeAdaptiveAnimations()` operate on the
playback controllers created by this session. `restoreOriginalPresentation()`
stops those controllers, restores captured visibility and materials, and calls
the app-owned animation manager when `.appManaged` supplied the baseline. Use
`.pristineLoadedRoot` only immediately after load and before the app creates any
playback. If the app already owns active or paused animation, supply an object
conforming to `AdaptiveAnimationStateManaging`; its preparation method must
capture/suspend that state and its restoration method must recreate it.

Annotations, pacing, label priority, disclosure presentation, Show More/Less,
Pause, Exit/Return, Restore Original, and any fallback card remain app-owned.
The executor does not synthesize runtime alpha or LOD variants.

## Integration outline

1. Add `RealityKitAdaptivePlanApplier.swift` to the native app target. Bundle
   `realitykit_entity_bindings.json` and
   `catalog_adaptation_profiles.json` as code-signed, read-only resources.
2. Create `AdaptiveLocalPlanAuthorization` from those bundled resource URLs.
3. Load the source through
   `RealityKitAdaptivePlanSession.load(contentsOf:)`; do not separately load a
   root and pass it into an adaptive session.
4. Decode the endpoint response with `decodeResponse(_:)`.
5. Construct `AdaptiveExpectedPresentation` from the app state that produced
   the request. For family mode, set both family gates only after the required
   participation/authorization and privacy flow succeeds.
6. Confirm and pass the explicit `.developerPreview` context, the correct
   `AdaptiveAnimationBaseline`, the displayed `AdaptiveFallbackPresentation`,
   and `AdaptivePresentationUIReadiness` state.
7. Call `apply` on the main actor, inspect `AdaptiveApplyReport`, and keep the
   false patient-display gate visible.
8. Route the app's Pause/Resume controls to the session methods. Call
   `restoreOriginalPresentation()` before changing presentation context,
   replacing/unloading the source, or exiting adaptive mode.

Do not reinterpret a name as a selector, load authorization JSON from a
mutable download location, bypass `patientDisplayAuthorized == false`, or call
the executor in `.patientEducation`. A future governed patient build needs a
separately reviewed, versioned, and authorized contract.

## Compile and type-check

From `Services/AdaptiveAssetService`:

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

The first three commands strictly type-check the same source for macOS,
visionOS device, and visionOS simulator SDKs. The final command produces the
optimized macOS validation executable; none builds or launches the app.

## Run the real-package harness

The tool takes seven positional arguments: source USDZ, endpoint response,
bindings, profiles, expected audience, expected detail tier, and expected
motion preference. From `Services/AdaptiveAssetService`, for example:

```bash
/tmp/ValidateRealityKitAdaptivePlan \
  ../../RealityKitContent/Assets/vision_pro_stroke_kit_v2/exports/usdz/brain_anatomy_realistic_v2.usdz \
  /tmp/brain-overview-static-response.json \
  adaptive_asset_service/runtime_profiles/realitykit_entity_bindings.json \
  adaptive_asset_service/runtime_profiles/catalog_adaptation_profiles.json \
  patient overview static
```

Optional flags are:

- `--fallback-presented` only when the response requires, and the app has
  actually presented, `application_plan.fallback_if_unresolved`;
- `--family-authorized --family-privacy-confirmed` together for an authorized
  family request; and
- `--patient-education` as a negative test: it is expected to fail while
  patient display remains blocked. The separate context-transition lifecycle
  probe confirms that such a rejection clears an already-active adaptation.

The harness loads and binds the real package, authorizes the response with the
local runtime resources, applies it, prints `AdaptiveApplyReport`, and restores
the presentation before exit.

## Validation evidence

The frozen executor passed strict macOS, visionOS-device, and visionOS-simulator
type-checks plus an optimized macOS build. The real-package harness then passed
canonical load/hash/topology/application/restoration for **135/135 released
USDZ packages** using overview/static requests, including **30 required-fallback
cases**.

Across that catalog run it applied **3,154 material entities and 3,154 material
slots**, **134 visibility operations**, and **24 authored animation resources**,
with **0 unsupported material slots**. Independent static reconstruction of all
**1,620 asset/detail/motion combinations** (135 assets × four detail tiers ×
three motion choices) matched the endpoint plans with zero mismatch. Targeted
real-package checks also covered static, reduced, and system-default motion.

Negative checks rejected the response/selector/material/animation/fallback/UI
tamper matrix, a reordered child topology, missing family gates, and patient
execution context. Context-transition rollback, Pause/Resume, and the
app-managed animation preparation/restoration lifecycle also passed.

This is engineering evidence for a developer-only reference executor. It does
not establish app integration, patient-display authorization, clinical or
human-factors validity, simulator launch, physical Vision Pro behavior, or
production performance.
