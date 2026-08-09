# Spatial care environment source provenance v1

## Provenance outcome

All geometry and materials in `spatial_care_environment_v1` are original,
project-authored procedural Blender work. The module uses no FAB asset, stock
model, downloaded mesh, external texture, photograph, portrait, product design,
ImageGen output, or third-party material library.

The user-supplied four-panel concept image was used only as a high-level mood and
composition reference: warm neutral architecture, curved central backdrop,
seating around a clear hero zone, restrained teal accents, wood rhythm, plants,
and layered fixture forms. No pixels, text, people, hands, portraits, interface
panels, anatomy, or identifiable design geometry were copied into the module.

## Authoring record

| Field | Value |
|---|---|
| Module | `spatial_care_environment_v1` |
| Generator | `source/build_spatial_care_environment_v1.py` |
| Editable source | `blender/spatial_care_environment_v1.blend` |
| Authoring application | Blender 5.2.0 LTS |
| Geometry method | Project-authored Python primitives, applied bevels, curves converted to mesh, and registered collection duplication |
| Materials | Project-authored Principled BSDF materials exported through USD Preview Surface compatibility |
| External texture dependencies | None |
| External mesh dependencies | None |
| Generated portraits or people | None |
| Patient data / PHI | None |
| Product or manufacturer representation | None |
| Runtime units / axis | metres / Y-up |
| Runtime Camera or Light prims | None |

## Original geometry construction

The generator builds nine independent registered collections:

1. Room shell from beveled slabs, walls, trims, window frame/glass, and open
   ceiling perimeter.
2. Feature wall from rounded panels, walnut slats, ledge, and abstract non-text
   identity shapes.
3. Lounge sofas from individual softened frame, seat, back, arm, and cushion
   meshes.
4. Consultation chairs from individual softened seat/back/arm and plinth meshes.
5. Spatial-display stage from cylinders and torus rings.
6. Coffee and side tables from rounded slabs, cylinders, and support meshes.
7. Credenza from cabinet, front, hardware, leg, and non-medical decor meshes.
8. Plants from ceramic cylinders, project-authored curve stems/branches, and
   transformed smooth leaf meshes.
9. Fixture geometry from cylinders, cone shades, torus rings, and sconce forms.

The registered assembly duplicates those nine collections at their exact common
room coordinates. It is a convenience package, not a new design source, and
must not be co-loaded with its components.

## Material construction

The material palette is procedural and self-contained:

- warm mineral plaster;
- light warm plaster;
- smoked oak floor;
- walnut and walnut shadow gaps;
- stone and sand high-roughness fabric;
- muted teal high-roughness fabric;
- greige rug and dark bound edge;
- matte dark metal;
- brushed aged brass;
- warm and charcoal ceramic;
- two botanical greens and a stem material;
- restrained frosted-glass preview surface; and
- opal and teal fixture/accent surfaces.

No material carries a therapeutic claim. “Calm” and “comfort” are design intent,
not clinical evidence or an anxiety diagnosis.

## Export construction

Each independent collection and the assembly are exported twice from Blender:

- editable/evidence stage: `exports/usdc/<asset-id>.usdc`;
- runtime package: `exports/usdz/<asset-id>.usdz`.

Export settings include:

- metres and Y-up conversion;
- root prim `/Asset`;
- mesh triangulation;
- normals and UV coordinates;
- portable preview-surface materials;
- custom properties under `userProperties`;
- cameras and lights excluded;
- animation excluded; and
- relative paths, with no external asset dependency.

The preview camera, preview floor, and three Blender Area lights are authoring
helpers only. They are excluded from runtime stages. Lighting-fixture packages
contain meshes but no emissive or runtime Light prim.

## Content and privacy exclusions

The source and runtime packages intentionally exclude:

- people, hands, avatars, or body scans;
- patient portraits or fictional portraits;
- names, medical records, case histories, or PHI;
- text, buttons, case cards, evidence panels, or topic rails;
- brain, head, vascular, blood, clot, pathology, or surgical geometry;
- medical devices, medication, supplies, or manufacturer-specific objects;
- dynamic physics, navigation, or treatment logic; and
- biometric, gaze, pupil, movement, or anxiety inference.

All interface content remains app-native. Existing reviewed anatomy assets are
composed separately and keep their own licence, provenance, clinical, scale, and
display restrictions.

## Build reproducibility

From the source-kit root:

```bash
/Applications/Blender.app/Contents/MacOS/Blender \
  --background \
  --python source/build_spatial_care_environment_v1.py

python3 source/validate_spatial_care_environment_v1.py
```

The first command regenerates the Blender master, all ten USDC/USDZ packages,
all ten 1600 × 1200 previews, and the manifest. The second command regenerates
strict package and RealityKit validation evidence.

Any geometry, material, export, filename, or package change invalidates recorded
byte counts, SHA-256 values, RealityKit observations, and validation evidence.
Rebuild and rerun all checks rather than editing hashes manually.

## Distribution and review status

Because this module is wholly project-authored and has no external asset
dependency, there is no third-party asset attribution or ShareAlike/NonCommercial
hold for this module. This statement does not change the licences of other
anatomy/tool modules with which it may be composed.

Technical and provenance cleanliness do not establish clinical readiness. The
module remains `patient_display_authorized=false` until the whole application
passes human-factors, accessibility, privacy, simulator, physical-device,
clinician, and institutional review.
