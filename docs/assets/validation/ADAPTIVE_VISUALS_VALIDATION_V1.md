# Adaptive visuals validation v1

Validation date: 2026-08-09

## Outcome

**1/1 package passes; 0 fails.**

| Asset | Triangles | USDZ bytes | RK models | RK materials | RK dimensions X × Y × Z (m) | Result |
|---|---:|---:|---:|---:|---:|---|
| `brain_orientation_calm_educational_v1` | 111,798 | 5,243,068 | 4 | 4 | 0.135973 × 0.145702 × 0.166934 | PASS |

The package passed `/usr/bin/usdchecker --arkit --strict`, contains one embedded
USD stage, declares `metersPerUnit = 1` and `upAxis = "Y"`, matches the exact
manifest byte counts and SHA-256 values, and loads through RealityKit with four
non-empty model/material regions and finite positive visual bounds. The exported
stage contains no cameras or lights. No authored prim name contains a prohibited
graphic-content token (vessel, blood, clot, lesion, haemorrhage, incision, or cut
surface). The 1600 × 1200 preview was visually inspected for framing, tonal
separation, silhouette readability, and absence of graphic procedural content.

Observed RealityKit desktop decode time: **285.4 ms**.
This observation is not a Vision Pro latency, frame-rate, memory, thermal, or
interaction guarantee.

## Integrity

```text
ad938c5737f8e2aae552277360ea4826cef6b066e3f4cbbfb81112281143e2d8  brain_orientation_calm_educational_v1.usdc
698016952f59068cb91cd6fb04fc50dbccec8c4c1495091e8e624bf21ec9efa6  brain_orientation_calm_educational_v1.usdz
```

## Scope

The technical pass does not validate anatomical completeness, clinical content,
informed-consent sufficiency, anxiety sensing, anxiety reduction, accessibility,
or patient comprehension. Muted pastel colour and reduced visual density are a
comfort-oriented design hypothesis and require specialist, privacy, accessibility,
human-factors, and representative-user review. The display mode must be disclosed,
reversible, and preserve optional access to all clinician-approved facts.
