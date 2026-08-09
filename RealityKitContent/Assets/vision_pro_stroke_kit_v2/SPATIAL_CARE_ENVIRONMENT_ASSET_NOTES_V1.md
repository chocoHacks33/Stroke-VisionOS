# Spatial care environment asset notes v1

## Purpose and default-environment rule

`spatial_care_environment_v1` is an optional synthetic consultation-room set
for a fully immersive developer demo or governed design review. It translates
the user-supplied reference's warm, quiet waiting-room mood into original,
unbranded geometry without copying its text, portraits, hands, interface panels,
or anatomy.

This module is **not the default environment**. On Apple Vision Pro, prefer
system passthrough. In Apple Vision Pro Simulator, prefer the configured
Simulator scene. Ordinary windows, volumes, or mixed/passthrough experiences
must not load this synthetic room merely to imitate the reference screenshot.
The app may offer it only through an explicit fully immersive developer/demo or
review mode.

The feature wall is intentionally blank. All headings, case cards, buttons,
labels, topic rails, evidence panels, comfort controls, portraits, and other
interface content belong in app-native SwiftUI/RealityKit attachments. Existing
manifest-backed anatomy is loaded separately at the provided anchor slots.

Every package remains `patient_display_authorized=false`. The visual mood is a
design hypothesis, not an anxiety treatment or evidence of clinical benefit.

## Exact inventory

The module contains **nine independent environment components plus one registered
assembly**. Independent components are already authored in the same room frame
and load at the same `experience_floor_origin`. The assembly duplicates every
component and therefore excludes all nine independent packages.

| # | Asset | Triangles | What it represents and where it belongs |
|---:|---|---:|---|
| 1 | `calm_consultation_room_shell_v1` | 7,708 | Open-front 7.2 × 6.2 m room shell: oak floor, warm plaster walls, baseboards, side window, and open-centre ceiling perimeter. It establishes scale and the optional immersive boundary. Never treat its furniture-scale floor as proof of real-world clearance. |
| 2 | `curved_feature_wall_architecture_v1` | 7,600 | Rounded central hero backdrop, walnut slat rhythm, ledge, and non-text identity backer on the rear wall. Its centre remains empty so the app can place a welcome brain, head model, case carousel, and labels without baked content. |
| 3 | `modular_lounge_seating_set_v1` | 12,600 | Two softened, upholstered sofas placed toward the rear-left and rear-right waiting zones. The teal/sand cushions echo the reference palette. They are spatial composition and scale cues, not usable physical seating. |
| 4 | `consultation_armchair_pair_v1` | 7,640 | Teal family chair and sand presenter chair framing the central display from the foreground. They visually support role selection and guided consultation but encode no user identity, permission, or interaction. |
| 5 | `round_spatial_display_dais_v1` | 7,148 | Greige circular rug, low dark plinth, teal ring, and three orientation points centred at runtime Z = −0.48 m. Existing brain/head packages attach above this stage. The markers are visual only and are not tracked calibration points. |
| 6 | `low_table_side_table_set_v1` | 5,216 | Rounded coffee table plus two pedestal side tables. They balance the room and provide scale cues but contain no controls, documents, clinical objects, or interactive surfaces. |
| 7 | `clinical_credenza_storage_v1` | 3,556 | Closed walnut storage with dark top, brass pulls, ceramic vase, and stone object against the rear-right wall. It is privacy-neutral decor; no supplies, records, medication, or device claims are encoded. |
| 8 | `calm_botanical_planter_set_v1` | 29,640 | Three planters with modeled stems, branches, and 42 individually oriented leaves. They soften corners and create landmarks. They make no therapeutic or anxiety-reduction claim. |
| 9 | `ambient_lighting_fixture_set_v1` | 7,800 | Two floor lamps, double ceiling ring, and two wall sconces. These are non-emissive fixture meshes only. RealityKit owns IBL and runtime lights. |
| 10 | `spatial_care_consultation_environment_assembly_v1` | 88,908 | Complete open-front room containing all nine registered components. Use for authoring review or the simplest explicit synthetic demo. Never co-load it with any component above. |

All package paths, exact byte counts, SHA-256 values, bounds, materials, review
flags, and app anchor slots are in
`asset_manifest_spatial_care_environment_v1.json`.

## Coordinate and placement contract

- Source Blender frame: X horizontal, Y into the room, Z up.
- Runtime USD/RealityKit frame: X horizontal, Y up, −Z into the room.
- Units: metres.
- Shared anchor: `experience_floor_origin = [0, 0, 0]`.
- Suggested viewer floor position: `[0, 0, 1.75]`.
- Suggested viewer eye position: `[0, 1.55, 1.75]`.
- Suggested forward direction: `[0, 0, −1]`.
- Full runtime bounds: approximately 7.2 m wide × 3.25 m high × 6.2 m deep.

These are authoring coordinates, not a safety boundary. On device, place virtual
content relative to the user's confirmed safe space, preserve visionOS system
boundaries, retain an immediate exit path, and never encourage walking, sitting,
or leaning against virtual furniture.

## Interface and anatomy anchor slots

The following slots are suggested authoring positions. The host app should still
derive comfortable attachment orientation from the current viewer pose, enforce
readable distance and angular size, and allow repositioning.

| Slot | Runtime position X, Y, Z (m) | Intended content |
|---|---|---|
| `welcome_brain_or_calm_orientation` | 0.00, 1.38, −0.48 | Existing calm orientation brain or approved welcome model above the dais. |
| `welcome_role_choice_attachment` | 0.00, 1.02, −0.08 | App-native Family/Presenter choice; permissions remain app state. |
| `case_selection_carousel` | 0.00, 1.45, −0.55 | Privacy-reviewed app-native case cards. Never put PHI in an environment texture. |
| `hero_head_anatomy` | 0.00, 1.35, −0.48 | Existing manifest-backed head/brain/vascular composition. |
| `left_guidance_attachment` | −1.55, 1.40, −0.15 | Short app-native orientation and urgency explanation. |
| `right_evidence_attachment` | 1.60, 1.26, −0.12 | App-native evidence or clinician-reviewed explanation card. |
| `right_topic_rail` | 2.42, 1.42, −0.32 | App-native topic navigation. Keep it reachable and avoid edge crowding. |
| `magnified_inset` | 1.60, 1.58, −0.28 | One separately loaded conceptual micro vignette with required scale disclaimers. |
| `comfort_controls` | 0.00, 0.82, 0.10 | Persistent Show Less/More, Pause, Restore, and Exit controls. |

All suggested panel forward vectors are `[0, 0, 1]`, toward the authored viewer
position. Do not bake these panels into USDZ, and do not use the environment's
blank wall as a single giant texture containing user interface or patient data.

## How the room supports the four reference states

### Welcome / role choice

Use passthrough or the Simulator scene by default. For an explicitly selected
synthetic demo, load the assembly or `room shell + feature wall + display dais +
selected decor`. Place the approved orientation brain and role-choice attachment
at their slots. The environment carries no user role and must not decide family
access.

### Case selection

Keep the room static. Replace the welcome attachment with the app-native case
carousel at `case_selection_carousel`. Portraits and case details are application
data, not asset textures. Use fictional or consented data only, and enforce the
application's privacy and family-participation gates.

### Guided orientation view

Place the reviewed head/anatomy composition at `hero_head_anatomy`, with the
short guidance attachment left and contextual card right. Hand input and pointer
affordances come from visionOS/RealityKit; this module contains no hand meshes.
The dais is a display cue, not a collision or calibration target.

### Scholar / detail view

Keep the full-scale head at the hero anchor. Use `magnified_inset` for one
separately loaded conceptual microscopic package and keep its magnification and
nonquantitative disclaimers visible. Put topic navigation at `right_topic_rail`.
Do not parent microscopic packages into the head or imply patient registration.

## Loading recipes

### Default patient or family experience

Load **none of this module**. Use system passthrough on device or the configured
Simulator scene, then load only the required app interface and reviewed anatomy.

### Explicit synthetic developer demo

Choose exactly one strategy:

1. Load `spatial_care_consultation_environment_assembly_v1`; or
2. Load selected independent components at the same floor anchor.

For progressive loading, start with room shell, feature wall, and dais. Add
seating and tables if needed for composition, then lazy-load credenza, plants,
and fixture geometry. Omit decor first under memory or frame-time pressure.

### Review and authoring

The assembly is useful for whole-room screenshot and anchor review. Independent
packages are better for profiling, incremental loading, optional decor, and
future per-component LOD work.

## Materials and lighting

The module uses portable Principled/UsdPreviewSurface-style materials with no
external image dependency: warm plaster, smoked oak, walnut, boucle-like matte
fabrics, muted teal accents, greige rug, dark metal, aged brass, ceramic,
botanical greens, frosted window glass, and opal fixture geometry.

The USDZ stages contain **no Camera or Light prim**. Preview cameras and lights
exist only during Blender rendering and are excluded from every package. The app
must author and test its own RealityKit lighting. Prefer restrained IBL and a
small number of app lights; verify exposure, material contrast, comfort, and
thermal behavior in both Simulator and physical Apple Vision Pro.

## Collision, physics, and interaction

No dynamic physics is authored. Suggested collision treatment:

- Room floor/boundaries: optional coarse static collision only in the gated
  synthetic immersive mode.
- Furniture: omit collision by default; add coarse static shapes only if a
  tested interaction needs them.
- Plants, decor, rug, dais, and fixture geometry: no collision by default.
- UI, anatomy manipulation, pointer targets, and hand input: app-owned
  RealityKit components, never inferred from environment meshes.

Do not simulate fabric, plant motion, furniture dynamics, walking constraints,
or lighting physics from these packages.

## Performance and quality

The full assembly is 88,908 triangles and approximately 2.7 MiB, below its
185,000-triangle ceiling. Each independent package also remains under its own
manifest budget. All ten packages pass strict ARKit USD validation and load
through RealityKit. These checks do not establish device frame rate, memory,
thermal stability, accessibility, or comfort.

Before patient-facing use, measure:

- asset decode and first-visible latency;
- steady-state and transition frame time;
- memory before and after unload;
- app light and shadow cost;
- comfort during seated and standing use;
- readability at tested distances;
- VoiceOver order and accessible labels for app-native controls;
- Reduce Motion behavior; and
- exit, system-boundary, and passthrough transitions.

## Recommended improvements

1. Integrate the manifest anchors into the actual visionOS app and capture
   Simulator/device screenshots before changing geometry again.
2. Add app-side progressive loading and explicit unload behavior for decor.
3. Build a measured LOD policy only if physical-device profiling identifies a
   bottleneck; do not produce unvalidated replacements pre-emptively.
4. Add coarse collision proxies in the app rather than using render meshes.
5. Tune IBL and app lights in Reality Composer Pro/RealityKit; fixture geometry
   is intentionally non-emissive.
6. Test the blank feature wall with Dynamic Type, contrast modes, VoiceOver,
   Reduce Motion, seated reach, and multiple viewer heights.
7. Provide a non-immersive window/volume fallback even when the synthetic demo
   is available.
8. Keep patient data, portrait lifecycle, and permissions in the application
   layer with institutional privacy review.
9. Repeat strict USD, RealityKit, screenshot, and device validation after any
   geometry, material, filename, or export change; hashes and topology are exact.

## Validation evidence

See:

- `validation/SPATIAL_CARE_ENVIRONMENT_VALIDATION_V1.md`
- `validation/spatial_care_environment_v1_validation.json`

Technical validation does not authorize patient display or healthcare use.
