# Stroke VisionOS

An Apple Vision Pro learning experience for exploring how an ischemic stroke can interrupt blood flow, inspecting the affected vessel in 3D, and comparing conceptual response paths in spatial context.

> [!IMPORTANT]
> This repository now contains a validated runtime asset catalog, but it does
> not yet contain the planned Xcode application scaffold. The experience below
> remains product direction unless a specific capability is present and
> independently verified in the repository.

## Product promise

Stroke VisionOS should make a difficult biological process understandable through a direct spatial loop:

1. Choose a learning module.
2. Place and inspect a 3D anatomical model.
3. Zoom into a vessel and open a cutaway view.
4. Observe a clot and the resulting restriction in blood flow.
5. Follow the mechanism from obstruction to stroke risk.
6. Explore a conceptual intervention and restored-flow state.
7. Zoom out or reset to regain anatomical context.
8. Compare Plan A and Plan B, then generate a learning summary.

```mermaid
flowchart LR
    A["1. Module gallery"] --> B["2. Place and inspect 3D anatomy"]
    B --> C["3. Zoom into vessel cutaway"]
    C --> D["4. Observe clot and restricted flow"]
    D --> E["5. Understand the stroke mechanism"]
    E --> F["6. Explore a conceptual intervention"]
    F --> G["7. Zoom out or reset"]
    G --> H["8. Compare plans and create summary"]
```

The experience should feel like an interactive spatial lesson, not a static anatomy viewer or a conventional dashboard.

## Safety and evidence boundary

This is an educational prototype. It is not a medical device and must not:

- diagnose, triage, or predict a real person's condition;
- recommend treatment, medication, dosage, or a clinical procedure;
- ingest patient records, scans, identifiers, or other protected health information;
- present simplified visuals or simulation values as clinically exact;
- claim device, simulator, build, scientific, or user-test proof that has not actually been completed.

Educational simplifications must be labelled in the interface and documentation. Scientific or clinical statements should be traceable to reputable sources before release.

## MVP scope

The first coherent vertical slice should include:

- a compact module gallery;
- one placeable and rotatable 3D vessel or neurovascular scene;
- zoom, orbit, translation, and a reliable Reset/Home action;
- a reversible cutaway or “unzip” view of the vessel;
- readable clot, restricted-flow, and restored-flow states;
- a short guided sequence connecting the visual change to the learning objective;
- a simple Plan A / Plan B comparison using educational language;
- a local learning summary or report with no patient data.

Not part of the first slice: accounts, cloud sync, clinical decision support, patient-specific simulation, collaboration backends, or production analytics.

## Current 3D asset catalog

The repository includes **145 uniquely named, manifest-backed USDZ runtime
assets**:

- 65 original packages: 36 higher-detail v2 assets and 29 clearly labelled
  low-poly prototype-v1 assets;
- 43 release-eligible v3 detail packages: 15 HRA neural-detail assets, 16
  non-held cranial-support assets, and 12 scale-separated conceptual
  microanatomy teaching assets;
- 26 release-eligible v3 surgical-tool packages: 12 endovascular support-tool
  packages and 14 open-cranial tool packages;
- one comfort-oriented, reduced-graphic HRA brain derivative for adaptive
  patient/family orientation;
- ten original spatial-care environment packages: nine independently loadable
  room components plus one registered review assembly;
- 147 total build records: the detailed source build produced 82 additional
  packages, but
  `middle_inner_ear_bilateral_v3` and
  `cranial_support_registered_assembly_v3` are on an inner-ear licence hold,
  and their binaries are deliberately absent from this publishing tree.

In this inventory, “release-eligible” means present in the non-held publishing
set—not clinically approved or hospital-ready.

The higher-detail catalog covers brain/skull anatomy, head layers, cranial
vasculature, cerebral blood-flow teaching views, and generic thrombectomy
devices, plus cortical parcellations, deep nuclei, white-matter regions,
cranial nerves, orbital/airway/muscle context, blood-brain-barrier teaching,
blood elements, thrombus microstructure, neurons, glia, myelin, synapse, CSF
interface, and conceptual ischemic-tissue zones. It also includes representative,
unbranded tool-recognition sets for gated endovascular and open-cranial lesson
branches. The tool sets are not exhaustive trays, clinical sequences,
instructions, device specifications, or training simulators.

The adaptive derivative is a presentation alternative, not an extra anatomy
layer. In its lowest-detail profile it replaces the detailed brain view; it
must not be co-loaded over the source anatomy or used to hide
clinician-approved facts.

The environment module is also a presentation option, not clinical content.
On Vision Pro the default remains system passthrough; in Simulator the default
remains the selected Simulator environment. The synthetic consultation room is
disabled by default and may be loaded only for an explicitly selected
fully-immersive developer demo or governed design review.

The complete one-by-one catalog, paths, descriptions, runtime notes, manifests,
and loading guidance are in
[`RealityKitContent/Assets/README.md`](RealityKitContent/Assets/README.md).
The canonical scene hierarchy, asset relationships, pathway state machine,
interaction physics, and Houdini/RealityKit handoff are defined in
[`MASTER.md`](MASTER.md).
Licensing and provenance are recorded under [`docs/assets`](docs/assets).
The 45 v3 build records—including the two non-published hold records—are
cataloged one by one in
[`INTRACRANIAL_ASSET_CATALOG_V3.md`](docs/assets/INTRACRANIAL_ASSET_CATALOG_V3.md).

![Layered generic head cutaway](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/08_layered_head_cutaway_v2.png)

![Registered cranial vascular context](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/17_cranial_vascular_brain_context.png)

![Registered neural-detail review](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/neural_detail_v3/36_registered_neural_review_assembly_v3.png)

![Blood-brain barrier conceptual teaching model](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/intracranial_micro_v3/40_blood_brain_barrier_neurovascular_unit_v3.png)

![Endovascular support-tool review gallery](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/endovascular_tools_v3/12_endovascular_tools_workflow_review_assembly_v3.png)

![Open-cranial access-tool review gallery](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/open_cranial_tools_v3/01_cranial_access_tools_review_assembly_v3.png)

![Comfort-oriented generic brain orientation](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/adaptive_visuals_v1/01_brain_orientation_calm_educational_v1.png)

![Optional spatial-care consultation environment](RealityKitContent/Assets/vision_pro_stroke_kit_v2/previews/spatial_care_environment_v1/10_spatial_care_consultation_environment_assembly_v1.png)

These models are generic educational material—not patient-specific anatomy,
histology, quantitative flow simulation, or clinical decision support. The
micro-detail packages must always appear in a separate magnified teaching stage
with persistent “not to anatomical scale,” conceptual/nonquantitative, and
non-patient-specific warnings.

Endovascular tools may appear only under the selected `EVT-*` educational
stage, with access route, imaging/flush, aspiration, hemostasis, and other
categories treated as conditional options. Open-cranial tools are
`open_neurosurgery_only`, prohibited from ordinary EVT, and require the explicit
`clinician_selected_hemorrhage_or_decompression_only` gate. Every tool is
static or qualitatively kinematic: no force, depth, trajectory, pressure,
energy, device sizing, compatibility, navigation, tissue interaction, or
training meaning is encoded.

## Spatial-care interface resource pack

The supplied four-state interface reference is represented by a deliberately
split implementation contract:

- **USDZ** supplies the existing reviewed anatomy and the ten optional room
  packages;
- **SwiftUI/RealityKit attachments** must supply glass panels, text, role
  choices, case cards, topic rails, evidence cards, progress, warnings,
  leader lines, magnifier frames, and reversible controls;
- **visionOS** supplies passthrough, the configured Simulator environment,
  hand presence, gaze privacy, natural input, hover, and system boundaries;
- **InterfaceMedia** supplies four clearly fictional demo portraits, a
  code-native wordmark, scene presets, UI tokens, SF Symbols mappings,
  review-blocked evidence placeholders, and an intentionally incomplete
  annotation-anchor review scaffold.

The supporting target board below translates the concept into a
right-M1-compatible, non-graphic four-state flow. It is an ImageGen design
reference—not a runtime screenshot, anatomical source, Simulator proof, or
clinical evidence.

![Spatial-care interface target storyboard](RealityKitContent/InterfaceMedia/spatial_care_interface_v1/previews/spatial_care_interface_storyboard_v1.png)

The current detailed clot and blood-flow packages depict a conceptual
**right-M1** scenario. Interface copy must say right M1; it must not reuse the
source concept's left-MCA wording. A future left-sided lesson requires
separately source-backed, registered, clinically reviewed left pathology and
flow assets—never a mirrored model.

All four case portraits and case records are synthetic fictional demo content.
They contain no patient record, clinical timeline, treatment recommendation,
eligibility decision, or predicted outcome. Keep the badge “Fictional
educational scenario — not a patient record” visible, and keep evidence cards
hidden in patient/family mode until the exact claim, current source, locale,
accessible copy, expiry policy, and review record are approved together.

The machine-readable pack is in
[`RealityKitContent/InterfaceMedia/spatial_care_interface_v1`](RealityKitContent/InterfaceMedia/spatial_care_interface_v1),
its [one-by-one interface resource catalog](RealityKitContent/InterfaceMedia/spatial_care_interface_v1/README.md)
explains all 14 supporting files, and its integration, ownership, state,
exclusion, physics, and Houdini rules are defined in
[`MASTER.md`](MASTER.md).

## Adaptive visual-comfort endpoint

[`Services/AdaptiveAssetService`](Services/AdaptiveAssetService) provides a
small local HTTP service for changing the presentation of a catalogued source asset
without rewriting its USDZ. `POST /v1/visual-adaptations` returns an immediate,
reversible RealityKit sidecar recipe for layer visibility, material intensity,
motion, labels, and pacing. It may also report a display-blocked orientation
candidate for later governed review. A compatibility alias is
available at `/v1/adaptations`.

```mermaid
flowchart LR
    A["Viewer chooses detail and motion"] --> B["POST /v1/visual-adaptations"]
    B --> C{"Edit or generate?"}
    C -->|"Edit — immediate"| D["Apply reversible RealityKit recipe"]
    C -->|"Generate — asynchronous"| E["Create abstract USDA review draft"]
    D --> F["Show active mode and Restore Original"]
    E --> G["Clinician review required before display"]
```

The service deliberately does **not** infer or diagnose anxiety. It rejects
pupil, gaze, joint-movement, biometric, and anxiety-score fields. Production
selection comes from `self_report_preference` or a governed
`clinician_override`; `simulated_demo` may make a seeded random choice only for
clearly labelled demos. The evidence and privacy contract is in
[`RESEARCH_AND_SAFETY.md`](docs/adaptive-visuals/RESEARCH_AND_SAFETY.md).

Run the dependency-free development service:

```bash
cd Services/AdaptiveAssetService
python3 -m adaptive_asset_service --port 8765
python3 -m unittest discover -s tests -v
```

The fast path is intended for on-the-spot use and preserves the source model.
In a local 250-request loopback check, the HTTP edit path measured 0.455 ms
median and 0.813 ms p95; this is development-machine evidence, not a Vision Pro
or production-network latency guarantee. Generated drafts are deterministic,
abstract, non-anatomical review artifacts and remain display-blocked until an
external authenticated clinical-review workflow approves them.
The reproducible checks and remaining gates are recorded in
[`ADAPTIVE_ENDPOINT_VALIDATION.md`](docs/adaptive-visuals/ADAPTIVE_ENDPOINT_VALIDATION.md).

## Intended Apple stack

The implementation direction is native visionOS:

- **SwiftUI** for windows, navigation, controls, and report surfaces;
- **RealityKit** for spatial anatomy, animation, materials, particles, and interactions;
- **Reality Composer Pro** where authored scene composition is useful;
- **XCTest or Swift Testing** for deterministic logic and state transitions;
- **Apple Vision Pro Simulator** for automated/local build evidence, followed by separate physical-device and human usability checks.

Exact deployment target, Xcode version, project name, scheme, and package choices must be recorded after the initial Xcode scaffold is merged. Do not guess them in code or documentation.

## Repository layout and planned app scaffold

The adaptive service and asset/docs trees below exist now. A future Xcode app
scaffolding pull request may refine the planned `StrokeVisionOS/` and `Tests/`
directories while keeping feature ownership obvious:

```text
Stroke-VisionOS/
├── README.md
├── StrokeVisionOS/                 # App source after project creation
│   ├── App/                        # App entry point and navigation
│   ├── Experience/                 # Shared spatial state and lesson flow
│   ├── Features/
│   │   ├── ModuleGallery/
│   │   ├── VesselExplorer/
│   │   ├── StrokeSimulation/
│   │   ├── PlanComparison/
│   │   └── LearningReport/
│   ├── Models/                     # Domain and lesson-state models
│   ├── Components/                 # Reusable SwiftUI/RealityKit pieces
│   └── Resources/                  # App-owned resources
├── RealityKitContent/
│   ├── Assets/                     # 145 manifest-backed USDZ packages
│   └── InterfaceMedia/             # Fictional/demo UI media and scene config
├── Services/
│   └── AdaptiveAssetService/       # Local visual-preference recipe endpoint
├── Tests/                          # Unit, contract, and UI tests
└── docs/                           # Decisions, evidence, sources, and asset records
```

Keep shared transform state—zoom, orbit, translation, cutaway state, and reset behavior—in one explicit experience-state owner. A Reset/Home action must restore the complete spatial view, not only one transform.

## Collaboration model

`main` is the integrated, reviewable branch. Arnav/project lead owns merges to `main`. Everyone else—including coding agents—works on a short-lived branch and opens a pull request.

### Branch names

Use one of these forms:

```text
feature/<name>-<short-scope>
fix/<name>-<short-scope>
asset/<name>-<short-scope>
docs/<name>-<short-scope>
chore/<name>-<short-scope>
```

Examples:

```text
feature/carman-vessel-cutaway
feature/mei-learning-report
asset/jo-neurovascular-model
fix/sam-reset-transform
```

Use lowercase words separated by hyphens. Do not create vague branches such as `updates`, `final`, or `new-version`.

### One-time repository bootstrap

Because the remote repository began empty, the project lead must seed `main` before teammates create branches:

```bash
git add README.md
git commit -m "docs: add project and collaboration guide"
git branch -M main
git push -u origin main
```

The lead should then merge an Xcode scaffolding pull request before feature work fans out. This prevents every teammate from independently creating a conflicting project file.

### Teammate workflow

```bash
# Clone once
git clone https://github.com/Arnie016/Stroke-VisionOS.git
cd Stroke-VisionOS

# Start every task from the latest main
git switch main
git pull --ff-only origin main
git switch -c feature/<your-name>-<short-scope>

# Work, then inspect exactly what changed
git status --short
git diff --check

# Commit and publish only your branch
git add <files-you-intend-to-commit>
git commit -m "feat: describe the user-visible change"
git push -u origin feature/<your-name>-<short-scope>
```

Open a pull request into `main`. Do not push directly to `main`, force-push a shared branch, or merge your own pull request unless the project lead explicitly asks.

### Commit style

Prefer small commits with an intent prefix:

- `feat:` user-visible capability;
- `fix:` defect correction;
- `asset:` model, texture, material, or animation work;
- `test:` verification only;
- `docs:` documentation only;
- `chore:` project configuration or maintenance.

Each commit should represent one understandable change. Avoid mixing feature work, asset replacement, broad formatting, and refactoring in the same commit.

## Workstream ownership

Before editing, claim a workstream in the team chat or GitHub issue. This is especially important for Xcode project files and Reality Composer Pro scenes, which are difficult to merge.

| Workstream | Typical ownership boundary | Example branch |
|---|---|---|
| Project scaffold | Xcode project, targets, packages, signing placeholders | `chore/arnav-project-scaffold` |
| Vessel explorer | Scene placement, transforms, cutaway, Reset/Home | `feature/carman-vessel-cutaway` |
| Flow and clot states | Deterministic lesson states, visuals, transitions | `feature/name-clot-flow-states` |
| Lesson UI | Gallery, step controls, labels, accessibility | `feature/name-guided-lesson-ui` |
| Adaptive presentation | Explicit visual preferences, reversible recipes, privacy/display gates | `codex/adaptive-visual-comfort` |
| Plans and report | Comparison surface and local learning summary | `feature/name-plan-report` |
| 3D assets | Model cleanup, scale, materials, provenance | `asset/name-neurovascular-model` |
| Verification | Unit tests, contract checks, build instructions | `test/name-experience-contract` |

If another branch owns the same scene or project file, coordinate before editing it. Prefer additive files and narrow changes over unrelated project-wide rewrites.

## 3D asset rules

- Agree on metres, origin, forward axis, pivot, and naming before importing assets.
- Prefer formats supported by the agreed RealityKit pipeline; keep editable sources separate from runtime exports.
- Record source URL or creator, licence, required attribution, modifications, scale, and export settings in `docs/assets/`.
- Configure Git LFS before committing large binary assets. Do not repeatedly replace large binaries in normal Git history.
- Do not commit assets with unclear rights, patient-derived data, secrets, API tokens, signing files, or private exports.
- Optimise geometry and textures deliberately; visual fidelity does not excuse an unusable frame rate.

## Pull request contract

Every pull request should answer:

1. **What changed?** Describe the user-visible behavior and list the main files.
2. **Why this scope?** Link the issue, task, or agreed workstream.
3. **How was it verified?** Include the exact command, simulator/device, and result.
4. **What remains unverified?** Call out device, hand tracking, performance, scientific review, or accessibility gates literally.
5. **What should reviewers look at?** Include screenshots or a short capture for visual/spatial work when available.

Checklist:

- [ ] Branch started from current `main`.
- [ ] Change stays inside the claimed workstream.
- [ ] `git diff --check` passes.
- [ ] The narrowest relevant tests/build were run and reported exactly.
- [ ] Reset/Home still restores every spatial transform affected by the change.
- [ ] Educational approximations and medical boundaries remain clear.
- [ ] New assets have provenance, licence, scale, and attribution records.
- [ ] No secrets, personal data, signing credentials, or generated build folders are included.
- [ ] Documentation matches the code that actually exists.

## Definition of done

A feature is done only when:

- its intended interaction works through the complete local loop;
- empty, loading, failure, and reset behavior are handled where relevant;
- labels remain readable and controls remain usable in the intended spatial context;
- deterministic state logic has a narrow test where practical;
- the app builds using the repository's documented command;
- the pull request records what was and was not tested;
- the work is reviewed and merged by the project lead.

A successful simulator build is not physical Vision Pro proof. A rendered animation is not scientific validation. A merged feature is not a clinical claim.

## Instructions for coding agents

When this repository URL is given to a coding agent, use the following contract:

```text
Read README.md completely before making changes.

1. Inspect git status, the current branch, and the actual repository contents.
2. Treat roadmap and proposed-architecture text as intent, not implemented fact.
3. Start from current main and create one short-lived branch for one bounded task.
4. Do not overwrite unrelated teammate work or broadly rewrite project files.
5. Keep the app native to visionOS unless the task explicitly changes that decision.
6. Preserve the educational/non-diagnostic boundary and never add patient data.
7. Do not add secrets, personal signing settings, paid services, or unlicensed assets.
8. Run the narrowest relevant verifier and report its exact result.
9. Do not push to main or merge. Push only the assigned branch if explicitly asked.
10. End with: changed files, verification, remaining blocker, and one next safe action.

If required context is missing and guessing would change architecture, medical meaning,
asset licensing, or another teammate's workstream, stop and ask the project lead.
```

Suggested task prompt:

```text
Work on <one bounded outcome> in https://github.com/Arnie016/Stroke-VisionOS.
Follow README.md and create <branch-name> from current main. Own only <files/workstream>.
Do not push to main or merge. Verify with <expected check>. Return changed files,
the exact verification result, the nearest blocker, and one next safe action.
```

## Build and verification status

The asset catalog has package-level USD/RealityKit validation documented in
[`docs/assets/VALIDATION.md`](docs/assets/VALIDATION.md). The adaptive service
has the Python test command documented above and in its own README. No Xcode
project or repository-owned app build command exists yet. The scaffolding pull request must
replace this section with:

- required macOS and Xcode versions;
- visionOS deployment target;
- project/workspace name and scheme;
- package or asset setup steps;
- exact simulator build command;
- exact test command;
- known physical-device and human-test gaps.

Until then, do not report `BUILD SUCCEEDED`, simulator support, device support, or completed interactions for this repository.

## Merge and conflict recovery

Before requesting review:

```bash
git fetch origin
git rebase origin/main
git diff --check origin/main...HEAD
```

If rebase conflicts touch another person's scene, Xcode project settings, or binary asset, stop and coordinate with that owner. Do not resolve a conflict by deleting their work or choosing an entire side blindly.

## Project decisions still to lock

- exact scientific learning objective and audience;
- anatomical model source and licence;
- visual language for clot, restricted flow, and restored flow;
- meaning and wording of Plan A / Plan B;
- whether the report is an on-screen recap, export, or both;
- minimum supported visionOS/Xcode versions;
- simulator performance budget and physical-device test plan;
- accessibility and reduced-motion behavior;
- repository licence.

Record accepted decisions in the repository so teammates and agents share the same source of truth. Chat messages and sketches are inputs; merged documentation and code are the canonical project record.

## Licence

No licence has been added yet. Do not assume that the code or assets may be redistributed outside the project team until the project lead adds an explicit licence.
