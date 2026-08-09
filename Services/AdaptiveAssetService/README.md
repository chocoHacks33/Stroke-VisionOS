# Adaptive Asset Service

A local HTTP service that turns a catalog asset plus an explicit presentation preference into a reversible RealityKit sidecar recipe. The fast path edits presentation at runtime; it does not destructively rewrite the USDZ.

The service deliberately does **not** estimate anxiety. It accepts no pupil, eye-tracking, movement, or other biometric data. `simulated_demo` randomly chooses a detail preference for demos and labels that choice as simulated and non-diagnostic.

## Run

Python 3.9 or newer is sufficient and there are no runtime dependencies.

```bash
cd Services/AdaptiveAssetService
python3 -m adaptive_asset_service --port 8765
```

Defaults:

- binds to `127.0.0.1` only;
- indexes the repository's `RealityKitContent/Assets/**/asset_manifest*.json` files read-only;
- loads the frozen visual-detail catalog and category policy and fails startup if
  their authorized revisions, source-package bytes, or SHA-256 bindings do not
  match;
- writes generated review drafts under the operating system's temporary directory;
- emits structured JSON logs containing request ID, route, status, and duration—not request bodies, asset IDs, preferences, or seeds.

Check readiness:

```bash
curl --fail http://127.0.0.1:8765/healthz
```

## Deterministic visual-detail variants

The isolated visual-detail API exposes exactly three explicit presentation
tiers for each catalogued asset. It does not infer anxiety, inspect sensors, or
randomly select a tier, and it does not change the existing four
`detail_preference` values used by `/v1/visual-adaptations`.

List all three variants, in `minimal`, `reduced80`, `full` order:

```bash
curl --fail-with-body \
  http://127.0.0.1:8765/v1/detail-variants/head_skin_generic
```

Resolve one tier against the exact USDZ revision:

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d @examples/detail_variant_request.json \
  http://127.0.0.1:8765/v1/detail-variants
```

`POST /v1/detail-variants` accepts exactly these three fields:

| Field | Required | Values / behavior |
|---|---:|---|
| `asset_id` | yes | Exact manifest ID; paths and traversal are rejected |
| `detail_tier` | yes | Exactly `minimal`, `reduced80`, or `full` |
| `expected_package_sha256` | yes | Lowercase 64-character SHA-256 copied from the current GET response |

`minimal` is the category policy's smallest complete explanatory
presentation. `reduced80` targets 80% of approved semantic information—not
80% of polygons. `full` binds the exact observed source package as the
presentation. Lower tiers are virtual, reversible recipes; none of the three
mutates the USDZ.

Both endpoints return path-free source metadata, including the exact package
byte count and SHA-256, plus the frozen catalog and category-policy revisions.
Every recipe contains the category-resolved `presentation_parameters`. If the
POST digest is stale, the server returns HTTP `409` and leaves the caller's
current state unchanged; fetch the variants again before retrying. Unknown
fields—including pupil, gaze, movement, biometric, anxiety, or other sensor
fields—are rejected rather than used as selectors.

The returned `application_contract` is intentionally strict:

- `runtime_scope` is `developer_preview_only`;
- `developer_runtime_application_authorized` is `false`;
- `renderer_mapping_status` is `pending_exact_renderer_mapping`; and
- `patient_display_authorized` is always `false`.

The endpoint resolves data only. A client must not apply the recipe until an
exact renderer/entity mapping has been implemented and separately reviewed,
and it must not show these variants to a patient while the display flag is
false.

## Fast edit request

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d @examples/edit_request.json \
  http://127.0.0.1:8765/v1/visual-adaptations
```

The response contains a `recipe` with:

- semantic layer visibility and LOD policy;
- material tint, saturation, roughness, and source-legend preservation;
- primary/secondary/blood-particle opacity;
- animation speed, autoplay, looping, and static-frame policy;
- annotation density and progressive-disclosure controls;
- pacing, confirmation pauses, warnings, and a safe generic fallback;
- an adaptation badge, changed-property disclosure, and one-action restoration of the original source.

Semantic layer selection is best-effort. If an asset does not expose the requested semantic layer groups, the client must use `recommended_fallback`; it must never hide content silently.

`status: completed` means only that the recipe was computed. The edit response
separately reports `application_contract.patient_display_authorized`. It is
always `false` in this prototype; developer preview remains a separate flag.
An external governed release must approve the exact source asset/version,
semantic entity mapping, and adaptive policy/profile together. Source-manifest
approval alone is not sufficient to approve a material or visibility edit.

For `overview`, the response also reports the catalogued
`brain_orientation_calm_educational_v1` as an
`orientation_asset_candidate` when available. It is deliberately marked
`display_authorized: false` because its manifest still requires specialist and
human-factors review. The service does not recommend or automatically display
it. If an external governed release later approves the exact asset version, use
it only as an orientation replacement: never co-load it over the medical
source, keep the source available, and restore the source before showing
medical detail. The calm asset never names itself as a candidate.

## Request contract

`POST /v1/visual-adaptations` (canonical) and `POST /v1/adaptations` (compatibility alias) accept:

| Field | Required | Values / behavior |
|---|---:|---|
| `asset_id` | yes | Exact ID from a checked manifest; path characters and traversal are rejected |
| `audience` | yes | `patient` or `family` |
| `mode` | yes | `auto`, `edit`, or `generate`; `auto` resolves to the fast edit path |
| `adaptation_source` | yes | `simulated_demo`, `self_report_preference`, or `clinician_override` |
| `detail_preference` | conditional | `overview`, `simplified`, `standard`, or `clinical_detail`; required except when a demo choice should be simulated |
| `motion_preference` | no | `system_default` (default), `reduced`, or `static` |
| `simulation_seed` | no | Integer `0...2^63-1`, accepted only for reproducible `simulated_demo` requests |

Unknown fields are rejected. In particular, `pupil_dilation`, `eye_tracking`, `joint_movement`, `anxiety_score`, and similar biometric/diagnostic fields produce `biometric_input_not_accepted`.

`family` recipes require confirmation of patient participation or authorization and privacy choices. They explicitly prohibit showing family members more detail than the patient authorized.

## Generation contract

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d @examples/generate_request.json \
  http://127.0.0.1:8765/v1/visual-adaptations
```

Generation returns HTTP `202` with a job contract. The service asynchronously creates:

- an original, abstract, low-intensity USDA orientation scene made from standard USD primitives; and
- the exact JSON presentation recipe used for the draft.

This is a deterministic procedural template, not an anatomy generator and not a claimed AI-model call. Poll `GET /v1/jobs/{job_id}` until the status is `awaiting_clinician_review`. Draft downloads carry:

```text
X-Display-Authorized: false
X-Clinical-Review-Required: true
```

The service intentionally has no self-approval endpoint. A properly
authenticated clinical-review workflow and a future governed release must issue
a separate exact-version approval record before an app can display a draft;
this prototype never changes the false display flag. The source medical asset
remains available and unchanged.

The procedural USDA is a review draft and is distinct from the catalogued
calm-orientation candidate. Both are explicitly display-blocked in the response;
the endpoint cannot confer patient-display approval on either artifact.

## RealityKit application boundary

The endpoint returns data; the visionOS app remains responsible for mapping semantic layer groups to known entity names and applying material overrides on the main actor. A safe client should:

1. reject the recipe for patient display when `patient_display_authorized` is
   false;
2. show that an adaptation is active;
3. show which properties changed;
4. keep Show Less, Show More, Pause, Exit/Return, and Restore Original visible;
5. fall back when semantic groups cannot be matched; and
6. prevent clinician-gated candidates and drafts from display until an external
   approval record exists.

The recipes are for patient/family education only. They are not for diagnosis, treatment selection, surgical planning, navigation, quantitative haemodynamics, or standalone informed consent.

## Test

```bash
cd Services/AdaptiveAssetService
python3 -m unittest discover -s tests -v
python3 -m json.tool openapi.json >/dev/null
```

The test suite covers catalog integrity, traversal rejection, request-framing
desynchronization, private artifact permissions, per-request correlation IDs,
validation, exact three-tier coverage, stale-package conflicts, frozen
catalog/policy bindings, seeded demo reproducibility, all motion overrides,
family privacy, biometric-field rejection, safe logging, asynchronous
procedural drafts, and clinical-review headers.

The complete machine-readable contract is in [openapi.json](openapi.json).

## Deployment notes

- This service has no authentication. Keep it on loopback for development or place it behind the project's approved authenticated gateway.
- `clinician_override` is a policy label, not proof of clinician identity; the authenticated gateway/review system must verify the actor.
- Terminate TLS and enforce authorization at that gateway before any network deployment.
- Do not send names, medical record numbers, sensor streams, or free text; the API schema has no fields for them.
- Runtime output belongs in an ephemeral or encrypted application container, not Git.
- The service accepts one bounded `Content-Length` and rejects
  `Transfer-Encoding`, duplicate lengths, and bodies on GET. Rejected framed
  requests close the connection rather than reusing unread bytes.
- Artifact roots and job directories are verified private (`0700`); generated
  scene and recipe files are written `0600`.
- Rate limits, audit retention, review identity, consent/authorization records, and deletion policy belong to the deployment layer.
