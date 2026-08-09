# Adaptive visual endpoint validation

Validation date: 2026-08-09

## Outcome

The development endpoint passes its local functional, privacy, catalog, and
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

Result: **21/21 tests passed**, the OpenAPI document parsed, and the Python
package compiled. Coverage includes:

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
- transparent, reversible edit recipes;
- allowlisted logs that omit request bodies, asset IDs, preferences, seeds, and
  client addresses;
- asynchronous deterministic procedural drafts with no external USD reference;
- `display_authorized: false` response and artifact headers; and
- no patient-display approval endpoint.

## Full-catalog smoke test

The service indexed **135 assets across 12 manifests** from
`RealityKitContent/Assets`. Live loopback requests verified:

- `/healthz` reports `diagnostic_inference: false`;
- an edit request returns an immediate source-preserving RealityKit recipe;
- edit completion remains separate from patient-display authorization; the
  prototype always returns `patient_display_authorized: false`, because a
  future governed release must approve the exact source, entity mapping, and
  adaptive policy/profile together;
- `simulated_demo` returns `simulated: true`, `non_diagnostic: true`, and uses no
  biometric input;
- a family request requires patient participation/authorization and privacy
  confirmation;
- overview may expose `brain_orientation_calm_educational_v1` only as an
  `orientation_asset_candidate` with its manifest review status,
  `display_authorized: false`, and the specialist/human-factors review gate;
- a generation request returns HTTP 202 and a deterministic abstract USDA
  review draft; and
- the generated USDA passes `usdchecker` and contains no external asset
  reference.

## Development latency observation

A 250-request HTTP loopback sample of the edit path measured:

| Statistic | Observed latency |
|---|---:|
| Median | 0.455 ms |
| p95 | 0.813 ms |
| Maximum | 6.347 ms |

This is a single local development-machine observation. It is not a guarantee
for Vision Pro, Wi-Fi, production gateways, authentication, thermal conditions,
concurrent load, or end-to-end RealityKit material application.

## Remaining release gates

- Put any non-loopback deployment behind authenticated authorization, TLS,
  rate limiting, retention/deletion policy, and reviewed audit controls.
- Have stroke clinicians and patient-education owners approve the exact content
  that each tier may reveal or defer.
- Complete privacy, accessibility, human-factors, health-literacy, and
  representative patient/family testing.
- Validate the exact RealityKit entity mappings, material overrides, reset,
  disclosure badge, Show More/Less, Pause, Exit, and Restore Original controls
  on physical Vision Pro hardware.
- Do not display a generated draft or the calm orientation candidate until the
  exact version has the required external review record.
