# Stroke Care Immersive — developer handoff

This directory contains a native SwiftUI + RealityKit visionOS developer preview that indexes the complete 150-model release, presents bounded educational scene recipes, and runs in Apple Vision Pro Simulator against a dark, full-immersion stage.

> This is generic, unapproved developer-preview content. It is not patient-specific, not authorized for patient/family display, not a surgical simulator, and not suitable for diagnosis, treatment planning, navigation, procedural training, device selection, or outcome prediction.

## What is implemented

- A Figma-inspired dark spatial interface with mint/amber accents and glass panels: landing view, Family/Presenter framing choice, fictional scenario cards, guided exploration, Calm/Guided/Scholar explanation styles, step timeline, topic rail, notes, toolbox, comfort/detail slider, and searchable asset library.
- A black full-immersion `ImmersiveSpace` with a bounded RealityKit teaching model and detached SwiftUI attachments for the disclosure, notes, toolbox, controls, and conceptual vessel vignette.
- All 150 catalogued USDZ packages staged into the app bundle with byte-count and SHA-256 verification.
- Three reversible presentation bindings for every source asset: `minimal`, `reduced80`, and `full` (450 bindings total).
- Fourteen step recipes plus detached artery-lumen and microcirculation vignettes. A recipe loads at most eight compatible assets; most load fewer.
- An explicit, user-paced state machine with Previous, Next, Pause/Resume, Replay, and Restore. There is no automatic clinical progression.
- A searchable, category-filtered 150-record library, paged eight records at a time. Open-cranial records remain visible as metadata but locked until the separate developer gate is active.
- Fail-closed resource loading: a missing required asset replaces the scene with a neutral marker; a missing optional asset produces a warning.
- Simulator build, install, launch, screenshot, gated-branch QA, resource-staging, and pure-core smoke-test scripts.

## Asset and visual-detail contract

The source of truth is:

```text
RealityKitContent/InterfaceMedia/visual_detail_variants_v1/visual_detail_variant_catalog_v1.json
```

The numbers have distinct meanings:

| Count | Meaning |
|---:|---|
| 150 | Unique source USDZ packages across 14 release manifests |
| 450 | Virtual presentation bindings: 150 assets × 3 tiers |
| 3 | `minimal`, `reduced80`, and `full` |

The 450 bindings are not 450 independent geometry files. Every tier resolves to the same catalogued USDZ path, byte count, and digest. `minimal` and `reduced80` are reversible presentation sidecars; they may reduce detached labels/notes, optional whole-role visibility, motion, flow cues, and view saturation without changing geometry or medical identity. `full` binds the exact source presentation.

The explicit 0–1 slider uses hysteresis to avoid rapid swapping:

- Enter `reduced80` at `0.40`; return to `minimal` at or below `0.28`.
- Enter `full` at `0.90`; return to `reduced80` at or below `0.82`.
- The setting is chosen by the user. The app does not infer anxiety from eyes, pupils, gaze, hands, joints, motion, voice, or any other biometric signal.

The current RealityKit executor applies the safe subset implemented by the app: whole-role/optional-layer visibility, qualitative-flow suppression, animation speed/pause, saturation, note/label density, and tier-dependent guidance. It does not mutate source meshes or hide descendant meshes. Every tier preserves each loaded asset's complete authored geometry because reviewed semantic child mappings do not yet exist.

## UI and spatial composition

The UI follows the supplied Figma/Page 2 and screenshot composition at the interaction level; it is not a pixel-for-pixel Figma export and does not reuse Figma anatomy, coordinates, clinical copy, or icons.

- Landing: Stroke Care wordmark treatment, generic brain orientation, Family/Presenter framing, and entry to scenarios or the 150-asset library.
- Scenarios: four fictional developer-preview cards for orientation, flow comparison, structural detail, and a detached vessel vignette.
- Explore: step timeline, central 3D teaching stage, detached note panel, topic rail, transport controls, Calm/Guided/Scholar framing, and explicit Comfort & Visual Detail slider.
- Library: all 150 metadata records, 14 categories, search, eight-record paging, component/assembly status, file size, and gated open-cranial entries.
- Immersive view: black full space, one fitted model root, detached glass attachments, and persistent safety disclosure.

Multi-asset recipes retain the assets' authored transforms under one shared root and apply one fit transform to the whole composition. Assets are never normalized independently inside a registered recipe. UI-owned elements such as step markers, panels, and the display dais are not loaded as 3D model layers, so their bounds cannot distort model fitting.

## Pathways and gates

| Path | States | Boundary |
|---|---|---|
| Common orientation | Case selection, head orientation, stroke explanation | Generic developer-preview anatomy only |
| Endovascular (default after scenario selection) | Vascular route, occlusion focus, detached device concept, illustrative flow comparison, recovery context | Never exposes scalp, bone, dura, open-cranial anatomy, or open-cranial tools |
| Open-cranial developer preview | Confirm site, cranial-access state, protective-layer state, condition state, closure state, post-closure context | Disabled by default; requires launch flag, explicit confirmation, and in-session developer authorization |
| Detached vessel/micro views | Artery-lumen panel or one micro focus | Magnified, conceptual, explicitly not to anatomical scale |

Important composition rules enforced in `ExperienceAssetSafetyPolicy`:

- Assemblies and their component leaves are mutually exclusive, including transitive assembly-to-assembly overlap.
- No recipe exceeds eight resident assets.
- Only one pathology focus may be resident in a scene.
- The endovascular pathway rejects hemorrhage/edema and every open-cranial state/tool.
- The open pathway rejects ischemic/endovascular content.
- Micro assets remain in detached, one-focus vignettes.
- The device step is a single detached `stent_retriever_educational_v2` focus; it does not combine a magnified vessel, macro clot, and unregistered comparison layout.
- Recovery currently uses one `patient_supine_generic` focus; monitoring/team context is presented in UI, not by overlapping independently centered models.
- Legacy body-route geometry and detached tool trays remain available in the library but are not overlaid on registered head recipes.

The Family/Presenter control changes placeholder framing only. Internally this build runs with a developer content context because every catalog variant currently declares `patient_display_authorized: false`. Do not convert that UI choice into patient authorization.

## Gestures and toolbox

The implemented input path uses visionOS-owned focus and pinch behavior for SwiftUI controls. In immersive view:

- Look at a button and pinch to choose it; Simulator pointer/tap provides the corresponding fallback.
- Spatial-tapping the model's coarse interaction target hides or reveals the toolbox.
- The toolbox exposes only tools allowed for the current state: pointing/focus, notes, layer visibility, detached vessel journey, scripted device/clot-removal state previews, illustrative flow comparison, and Restore.
- Tools requiring a conceptual state change show a confirmation first.
- Open-cranial tools are unavailable in the default endovascular path and remain locked unless all developer gates pass.
- “Clot removal,” “access,” and “closure” are reversible pre-authored visibility/state changes. They are not free-form manipulation, cutting, drilling, aspiration, force, tissue, bleeding, suturing, or fixation simulations.

The app does not collect raw gaze, pupil dilation, hand-joint poses, or emotion/anxiety signals, and it does not render a custom hand mesh.

## Requirements

- Apple Silicon Mac.
- Xcode with the visionOS 27 SDK and Apple Vision Pro Simulator runtime. The scripts default to `/Applications/Xcode-beta.app/Contents/Developer`.
- Command-line tools available to the script: `zsh`, `jq`, `codesign`, `shasum`, and `xcrun`.
- The repository's complete `RealityKitContent` release. Resource staging intentionally fails if a catalogued file, byte count, or SHA-256 digest differs.

The canonical scripts target `arm64-apple-xros27.0-simulator`. They do not provision or install to a physical headset.

## Exact test, build, install, and launch commands

Run these from the repository root.

### 1. Core contract tests

```bash
Apps/StrokeImmersiveExperience/Scripts/run_core_smoke_tests.sh
```

Expected final line:

```text
ExperienceCore smoke tests passed: 150 assets, 450 variants, 14 step recipes.
```

The smoke suite verifies catalog counts and binding path/byte/digest invariants, tier monotonicity and hysteresis, recipe budgets, assembly/component exclusion, pathway separation, single-pathology and micro-vignette rules, audience/open-branch gates, detached placeholder notes, and the core tier-reconfiguration plan.

### 2. Build only

```bash
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh --build-only
```

Default output:

```text
Apps/StrokeImmersiveExperience/build/Stroke Care Immersive.app
```

The build stages all 150 USDZ files, their 14 source manifests, and three InterfaceMedia packs; verifies staged bytes and SHA-256 values; compiles for visionOS Simulator; and ad-hoc signs the bundle.

### 3. Build, boot, install, and launch

```bash
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh
```

The script prefers an already booted, available simulator whose name contains `Vision Pro` or `Stroke Care`, then falls back to the first matching available simulator. The open-cranial developer branch is off.

### 4. Build, launch, and capture a screenshot

```bash
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh \
  --screenshot /absolute/path/stroke-care-immersive.png
```

The script waits fifteen seconds after launch and captures the selected Simulator display. Set `STROKE_SCREENSHOT_DELAY_SECONDS` to override the delay for local QA.

### 5. Gated open-cranial QA

```bash
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh \
  --enable-open-preview
```

This launches with `SIMCTL_CHILD_STROKE_ENABLE_OPEN_CRANIAL_DEVELOPER_PREVIEW=1`. It only exposes the entry control; the user must still confirm the branch, and the state machine must create a valid developer authorization. This is a QA flag, not authentication or clinical approval.

### 6. Select an exact Simulator or toolchain

```bash
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh \
  --device "Apple Vision Pro"

STROKE_XCODE_DEVELOPER=/Applications/Xcode-beta.app/Contents/Developer \
STROKE_VISION_DEVICE_UDID=YOUR-SIMULATOR-UDID \
STROKE_IMMERSIVE_BUILD_ROOT=/absolute/path/to/build \
Apps/StrokeImmersiveExperience/Scripts/build_install_launch.sh
```

Environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `STROKE_XCODE_DEVELOPER` | `/Applications/Xcode-beta.app/Contents/Developer` | Xcode developer directory |
| `STROKE_VISION_DEVICE_UDID` | Auto-detected matching Simulator | Exact visionOS Simulator UDID |
| `STROKE_IMMERSIVE_BUILD_ROOT` | `Apps/StrokeImmersiveExperience/build` | App and smoke-test output directory |
| `STROKE_SCREENSHOT_DELAY_SECONDS` | `15` | Seconds to wait after launch before screenshot QA |

The Xcode project can also be opened directly:

```bash
open Apps/StrokeImmersiveExperience/StrokeImmersiveExperience.xcodeproj
```

The shared scheme keeps `STROKE_ENABLE_OPEN_CRANIAL_DEVELOPER_PREVIEW=0` by default.

## Code map

```text
Apps/StrokeImmersiveExperience/
├── Config/                         build settings for visionOS 27
├── Scripts/                        tests, resource staging, build/install/launch
├── Sources/ExperienceCore/         catalog, tiers, recipes, safety, state, notes, tools, cameras
├── Sources/StrokeImmersiveExperience/ SwiftUI and RealityKit app shell
├── Tests/ExperienceCoreTests/      executable pure-core smoke suite
├── StrokeImmersiveExperience.xcodeproj
└── Info.plist
```

Key runtime flow:

1. `ExperienceAssetCatalog` validates and indexes the 150/450 catalog.
2. `ProcedureExperienceStateMachine` selects a user-paced step and allowed actions.
3. `ExperienceSceneRecipeLibrary` chooses a bounded composition.
4. `ExperienceAssetSafetyPolicy` validates pathway, scale, pathology, and transitive exclusion rules.
5. `ExperienceAssetResidencyPlanner` can describe incremental load/unload/reconfigure changes for the next integration stage.
6. The current app loads required USDZ packages under one shared registration root and applies the selected presentation sidecars; it rebuilds that root when the active recipe changes.

## Safety and non-graphic boundary

- No real patient data, imaging, identifiers, PHI, measurements, or patient-specific anatomy is accepted.
- No diagnosis, triage, treatment recommendation, outcome estimate, or clinical evidence claim is produced.
- No surgical physics, tissue deformation, cutting path, drill behavior, force, depth, trajectory, bleeding, fluid dynamics, device sizing, clot mechanics, suturing, or fixation logic is implemented.
- Flow particles are qualitative direction cues, never flow rate, pressure, perfusion, or reperfusion measurements.
- Detached vessel and micro views are conceptual and not to anatomical scale.
- Built-in explanatory notes are visibly labelled developer placeholders and remain detached because the source copy/anchor contracts are unresolved.
- A required asset or unresolved governed composition fails closed; the runtime does not substitute a medically different model.
- Reduce Motion pauses authored animation; Pause/Resume and Restore remain available throughout the lesson.

## Known limitations

1. All catalog variants are currently unauthorized for patient/family display. The current app is a developer preview even when the framing picker says Family.
2. The Figma-derived UI is an implementation interpretation, not a pixel-perfect or semantically connected Figma export.
3. Notes, evidence cards, leader-line anchors, and clinical copy are placeholders. They are not governed medical content and are not spatially attached to anatomy.
4. Camera presets are framing metadata. The current app does not execute automatic anatomical fly-throughs; the vessel experience is a detached circular vignette.
5. System gaze/pinch selects controls, and a spatial tap toggles the toolbox, but orbit, bounded zoom, drag manipulation, and richer hand-gesture commands are not yet wired to the RealityKit stage.
6. The runtime applies only part of the visual-detail sidecar. It does not yet perform material saturation/specular edits, true texture-LOD swaps, branch-level mesh culling, or controlled particle-count regeneration.
7. All 150 source packages ship in the Simulator bundle, although only the active bounded recipe loads into a scene. Bundle size and install time remain substantial, and the core residency-diff planner is not yet connected to incremental RealityKit loading.
8. Multi-asset registration relies on authored source transforms. Several independently centered clinical-context and tool models therefore remain library-only or single-focus until a governed registered assembly exists.
9. The open-cranial environment flag is a developer convenience, not a secure role/authorization system.
10. The canonical automation installs only to visionOS Simulator. Physical Vision Pro signing, entitlements, device trust, pairing, performance, and comfort testing remain outstanding.
11. There is no external web anxiety endpoint, sensor pipeline, analytics, persistence, networking, multi-user synchronization, or clinician content-management system in this app.

## Improvement priorities

1. Complete specialist governance for exact assets, copy, anchors, warnings, pathway compositions, and release revisions before changing any patient-display authorization.
2. Establish registered assemblies and explicit anchor metadata for every intended multi-asset scene; retain assembly/component exclusion tests.
3. Profile on physical Apple Vision Pro for memory, triangles, draw calls, load latency, thermal behavior, attachment legibility, motion comfort, occlusion, and hand interaction.
4. Implement a complete, reversible RealityKit sidecar executor for approved materials, labels, LODs, particles, and animations while preserving the exact source geometry and disclosures.
5. Wire comfortable orbit/zoom and opt-in detached camera journeys with system gesture APIs, Reduce Motion behavior, dwell/VoiceOver alternatives, and Simulator parity.
6. Replace placeholder notes with revisioned, governed copy and anchor bindings that fail closed when an asset revision changes.
7. Add secure role and content-release authorization; keep the open branch unreachable from ordinary EVT.
8. Add unit, UI, screenshot-regression, resource-corruption, memory-pressure, cancellation, and physical-device test coverage.
9. Add localization, Dynamic Type/VoiceOver review, Reduce Transparency treatment, contrast checks, and patient-comprehension testing only after content approval.
10. Build a signed physical-device workflow separately from the Simulator script.
