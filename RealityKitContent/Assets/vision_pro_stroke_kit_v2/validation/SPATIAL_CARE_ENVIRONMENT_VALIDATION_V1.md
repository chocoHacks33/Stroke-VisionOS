# Spatial care environment validation v1

Validation date: 2026-08-09

## Outcome

**10/10 packages pass; 0 fail.**
Module contract checks: **PASS**.

| Asset | Triangles / budget | USDZ bytes | RK models | RK materials | RK dimensions X × Y × Z (m) | Result |
|---|---:|---:|---:|---:|---|---|
| `calm_consultation_room_shell_v1` | 7,708 / 32,000 | 138,335 | 41 | 41 | 7.200 × 3.250 × 6.200 | PASS |
| `curved_feature_wall_architecture_v1` | 7,600 / 22,000 | 247,829 | 23 | 23 | 5.835 × 2.680 × 0.435 | PASS |
| `modular_lounge_seating_set_v1` | 12,600 / 28,000 | 405,314 | 18 | 18 | 6.401 × 1.120 × 1.246 | PASS |
| `consultation_armchair_pair_v1` | 7,640 / 16,000 | 156,466 | 10 | 10 | 4.475 × 1.150 × 1.054 | PASS |
| `round_spatial_display_dais_v1` | 7,148 / 11,000 | 305,423 | 7 | 7 | 2.360 × 0.106 × 2.360 | PASS |
| `low_table_side_table_set_v1` | 5,216 / 13,000 | 142,884 | 8 | 8 | 6.160 × 0.542 × 2.700 | PASS |
| `clinical_credenza_storage_v1` | 3,556 / 13,000 | 128,963 | 12 | 12 | 1.830 × 1.150 × 0.495 | PASS |
| `calm_botanical_planter_set_v1` | 29,640 / 36,000 | 860,946 | 93 | 93 | 6.917 × 1.926 × 4.966 | PASS |
| `ambient_lighting_fixture_set_v1` | 7,800 / 30,000 | 265,375 | 14 | 14 | 6.460 × 2.946 × 4.015 | PASS |
| `spatial_care_consultation_environment_assembly_v1` | 88,908 / 185,000 | 2,618,451 | 226 | 226 | 7.200 × 3.250 × 6.200 | PASS |

Every package passed `/usr/bin/usdchecker --arkit --strict`, contains one embedded
USD stage, declares `metersPerUnit = 1` and `upAxis = "Y"`, matches its exact
manifest byte count and SHA-256 digest, stays below its triangle budget, has no
external asset dependency, and loads through RealityKit with finite positive
bounds and at least one model/material. Runtime bounds match the manifest's
Blender-X/Y/Z to RealityKit-X/Y/Z axis mapping. All ten previews are 1600 × 1200.

No exported stage contains a Camera or Light prim. No authored prim name matches
the prohibited portrait, patient-record, person/hand, anatomy, pathology, blood,
or baked-interface tokens checked by the validator. This is a structural check,
not a privacy, accessibility, clinical, human-factors, or visual-design approval.

## Required environment boundary

The manifest keeps system passthrough on device—or the configured Apple Vision
Pro Simulator scene—as the default environment. The synthetic room is disabled
by default and gated to an explicitly selected fully immersive developer demo or
governed review. Ordinary windows, volumes, and mixed/passthrough presentation
must not load it simply to reproduce the visual reference.

The feature-wall centre is intentionally blank. The host app supplies all text,
case cards, comfort controls, evidence panels, topic rails, portraits, and other
interface content as app-native SwiftUI/RealityKit attachments. Existing reviewed
anatomy packages are loaded separately at named anchor slots.

## Assembly and runtime rules

- Load either the full assembly or selected independent components, never both.
- All nine independent components share the same floor-origin registration.
- Fixture packages are non-emissive geometry; the app owns runtime illumination.
- Virtual furniture is not physical furniture and must not invite sitting,
  leaning, or walking into unverified real-world space.
- Generate only deliberately selected coarse static collisions. No dynamic
  rigid-body, fabric, lighting, or interaction physics is authored.
- The observed desktop RealityKit decode times are not Vision Pro frame-rate,
  memory, thermal, comfort, or device-performance guarantees.

## Remaining gates

Before any patient-facing build, perform app-level composition in a real Xcode
visionOS target, simulator screenshots, physical-device tests, frame-time and
memory profiling, system-boundary and passthrough checks, seated/standing reach
testing, Reduce Motion and VoiceOver review, readable-contrast testing, privacy
review, human-factors evaluation, clinician review of the complete experience,
and institutional governance approval. `patient_display_authorized` remains
`false` for every package and for the module.
