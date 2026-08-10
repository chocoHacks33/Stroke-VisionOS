# Adaptive Asset Service

A dependency-free local HTTP service (service/API 0.2.0) that turns a
catalogued asset plus an explicit presentation preference into a reversible
RealityKit sidecar contract. The source USDZ is never rewritten.

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
- loads 135 catalog adaptation profiles and exact package-revision-bound
  RealityKit selector records by default;
- writes generated review drafts under the operating system's temporary directory;
- emits structured JSON logs containing request ID, route, status, and duration—not request bodies, asset IDs, preferences, or seeds.

The packaged profile, schema, RealityKit topology, and binding JSON files live
in `adaptive_asset_service/runtime_profiles/`. Deterministic builder scripts
remain in `profiles/`; installed wheels include the runtime JSON, not the
builders.

Check readiness:

```bash
curl --fail http://127.0.0.1:8765/healthz
```

## Local developer control panel

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/) after starting the
service. The dependency-free control panel is served from the Python package
and provides:

- search across all manifest-backed assets through the path-free
  `GET /v1/catalog` view;
- explicit audience, preference-source, detail-tier, motion, and edit/generate
  controls;
- a clearly labelled abstract presentation sketch driven by the returned
  recipe, not a substitute USDZ renderer;
- requested visibility, opacity, label-density, motion, authorization, and
  orientation-candidate inspection, alongside the executable-plan boundary;
- formatted request/response JSON and a copyable cURL handoff; and
- polling plus review-only downloads for generated USDA drafts.

The panel cannot approve patient display, upload sensor data, mutate a source
package, or apply a recipe to RealityKit. It keeps the service response as the
policy source of truth and displays the false authorization gate prominently.
Its architecture and future visionOS handoff are documented in
[DEVELOPER_PREVIEW_HANDOFF.md](DEVELOPER_PREVIEW_HANDOFF.md).

## Fast edit request

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d @examples/edit_request.json \
  http://127.0.0.1:8765/v1/visual-adaptations
```

The response separates policy from executable work:

- `recipe` records the requested detail tier, semantic groups, bounded
  developer-preview material values, motion preference, opacity request, LOD
  bias, annotations, pacing, controls, warnings, and fallback;
- `catalog_adaptation_profile` provides the selected asset's closed action
  allowlists, graphic-content tags, replacement exclusions, and fail-closed
  review state; and
- `application_plan` contains only exact visibility, material, and authored
  animation operations for the loaded package revision.

The default selector set covers all 135 released assets and is derived from a
RealityKit load of 7,243 entities: 3,472 carry models and 24 authored animation
resources are present. Each operation starts at the entity returned by
`Entity.load(contentsOf:)` and follows an exact child-index path. The plan is
rejected if the loaded USDZ SHA-256 does not match. Entity names and debug paths
are diagnostics, not selectors.

Exact selector identity does not make the semantic grouping clinically
validated. The classification is deterministic presentation routing and still
requires external clinical and human-factors review. Mapped labels and primary
pathology are protected from automatic material changes, and primary semantic
groups are protected from automatic visibility changes. An absent requested
group is reported as not applicable; a present but blocked request marks the
plan unresolved and requires the documented fallback.

The current executor has deliberate limits:

- opacity is handled through exact discrete visibility only; it emits no alpha
  operations and otherwise preserves source opacity;
- no runtime LOD variant is available, so source geometry is preserved;
- annotation density, pacing, label priority, and comfort controls are owned by
  the visionOS app; authored geometry labels are not automatically hidden; and
- material changes are bounded, display-blocked developer-preview transforms
  and carry no patient-display authorization.

The source package and source materials remain untouched on disk. The app must
snapshot runtime state before the first edit and provide one-action restoration.
The contract does not assert that medical meaning has been preserved; that
requires external clinical and human-factors review of the exact build.

`status: completed` means only that the recipe was computed. The edit response
separately reports `application_contract.patient_display_authorized`. It is
always `false` in this prototype; developer preview remains a separate flag.
An external governed release must approve the exact source asset/version,
semantic entity mapping, and adaptive policy/profile together. Source-manifest
approval alone is not sufficient to approve a material or visibility edit.

For `overview`, the response may report
`brain_orientation_calm_educational_v1` only when the selected source is one of
the 19 profile-allowlisted brain/neuroanatomy assets. The candidate is marked
`display_authorized: false` because its manifest still requires specialist and
human-factors review. The service does not recommend, resolve, or automatically
display it. If a future governed release approves the exact asset version and
policy, use it only as an orientation replacement: never co-load it over the
medical source, keep the source available, and restore the source before showing
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

`GET /v1/catalog` supports the local developer panel. It returns stable asset
IDs, titles, modules, descriptions, review statuses, package basenames, byte
counts, content hashes, integrity status, path-free adaptation-profile summaries,
and entity-mapping summaries. It does not expose the catalog root, manifest
path, or relative package path.

## Generation contract

```bash
curl --fail-with-body \
  -H 'Content-Type: application/json' \
  -d @examples/generate_request.json \
  http://127.0.0.1:8765/v1/visual-adaptations
```

Generation returns HTTP `202` with a job contract. The service asynchronously creates:

- an original, abstract, low-intensity USDA orientation scene made from standard
  USD primitives; and
- a JSON review envelope containing the exact presentation recipe.

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
calm-orientation candidate. The USDA embeds `artifactRole`,
`displayAuthorized=false`, and `reviewGate` as custom metadata. The JSON embeds
the equivalent `artifact_role`, `display_authorized=false`, and `review_gate`
around the nested `recipe`. The transport headers and job response repeat the
same block. The endpoint cannot confer patient-display approval on either
artifact.

## RealityKit application boundary

The HTTP endpoint computes exact child-index operations but does not mutate a
RealityKit scene. A developer-preview reference executor is provided in
[`clients/RealityKitAdaptivePlanApplier.swift`](clients/RealityKitAdaptivePlanApplier.swift),
with a real-package host harness in
[`tools/ValidateRealityKitAdaptivePlan.swift`](tools/ValidateRealityKitAdaptivePlan.swift).
See [`clients/README.md`](clients/README.md) for its compile, type-check, and
integration contract. Its frozen SHA-256 is
`a57a53f7c15ecc343ba25e3f13152e89659d1fd36f551be5f82d20c98823dbe2`.
The reference source is not integrated into a visionOS app and cannot authorize
patient display.

The reference client deliberately makes the integration context part of
authorization:

1. `RealityKitAdaptivePlanSession.load(contentsOf:)` hashes the USDZ before and
   after the RealityKit load and binds the loaded root to that byte count and
   SHA-256. A caller cannot substitute a separately loaded root.
2. `AdaptiveLocalPlanAuthorization` verifies the response against the exact
   bindings and catalog profiles bundled as code-signed app resources, then
   validates the complete recorded topology and canonical operation set.
3. `apply` requires `.developerPreview`, the app's expected audience/detail/
   motion state, a declared animation baseline, the exact fallback presentation
   state, and readiness of required disclosure, controls, warning, and
   progressive-disclosure UI.
4. Family mode requires both patient participation or authorization and the
   privacy gate. `.patientEducation` is rejected while display authorization is
   false; a rejected context transition first clears any active adaptation.
5. Operations traverse only `child_index_path` from the bound root and run on
   the main actor. Names and debug paths are never runtime selectors. Opacity
   remains discrete visibility and source geometry remains unchanged because no
   runtime LOD variant exists.
6. The app must present the returned fallback whenever it is required. A
   present semantic request blocked by the profile is not silently ignored;
   groups absent from the package remain not applicable.
7. For app-owned animation state, provide an
   `AdaptiveAnimationStateManaging` baseline that captures/suspends playback and
   recreates it at restoration. The session also exposes Pause/Resume and
   restores its visibility/material snapshots while stopping its own playback
   controllers.
8. Keep the active-adaptation disclosure, changed properties, Show Less, Show
   More, Pause, Exit/Return, and Restore Original available. Prevent gated
   candidates or drafts from display until an external exact-version approval
   record exists.

The selector map is technically exact for the captured package topology, but
its semantic classification and every patient-facing visual change remain
subject to external clinical and human-factors review.

The recipes are for patient/family education only. They are not for diagnosis, treatment selection, surgical planning, navigation, quantitative haemodynamics, or standalone informed consent.

## Test

```bash
cd Services/AdaptiveAssetService
python3 -m unittest discover -s tests -v
python3 -m json.tool openapi.json >/dev/null
```

The current suite passes **41/41** tests. It covers catalog integrity,
135/135 profile and topology-bound selector coverage, selector tamper and
revision rejection, primary-pathology/label protection, executable operation
contracts, static-UI allowlisting and security
headers, path-free catalog browsing, traversal rejection, request-framing
desynchronization, private artifact permissions, per-request correlation IDs,
validation, seeded demo reproducibility, all motion overrides, family privacy,
biometric-field rejection, safe logging, asynchronous procedural drafts, and
embedded/transport clinical-review gates.

Separately, the frozen native reference passed strict macOS, visionOS-device,
and visionOS-simulator type-checks plus an optimized macOS build. Canonical
overview/static load, hash, topology authorization, application, and restoration
passed for **135/135 real USDZ packages**, including 30 fallback cases. That run
applied 3,154 material entities/slots, 134 visibility operations, and 24
authored animation resources with zero unsupported slots. Static reconstruction
of all 1,620 asset/detail/motion combinations matched with zero mismatch;
targeted motion, tamper, child-reorder, context-rollback, Pause/Resume, and
app-owned animation-manager lifecycle checks also passed. This remains
developer-only engineering evidence, not app integration or patient-display
validation. Reproduction commands and the complete boundary are in
[`clients/README.md`](clients/README.md), with evidence recorded in
[`ADAPTIVE_ENDPOINT_VALIDATION.md`](../../docs/adaptive-visuals/ADAPTIVE_ENDPOINT_VALIDATION.md).

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
