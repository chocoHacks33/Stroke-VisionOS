# Visual Detail Variants v1

This pack is a deterministic, machine-readable presentation contract for the 150 release USDZ assets. It defines three explicit visual-detail selections per asset—450 virtual variants in total—without copying, decimating, rewriting, or replacing source geometry.

The pack is an authoring and integration resource. `patient_display_authorized` is `false` throughout. Nothing here grants clinical validity, patient-display approval, device-operation guidance, a treatment recommendation, or permission to infer a viewer state.

## Contents

| File | Purpose |
| --- | --- |
| `visual_detail_variant_catalog_v1.json` | Ordered 150-asset catalog and all 450 virtual variant bindings. |
| `VISUAL_DETAIL_ASSET_CATEGORIES.txt` | Exhaustive, mutually exclusive 14-category asset-ID map plus all 17 assembly-domain overrides. |
| `visual_detail_category_policy_v1.json` | Category-specific preservation, simplification, and prohibition rules. |
| `visual_detail_category_policy_schema_v1.json` | JSON Schema for the policy document. |
| `visual_detail_selector_v1.js` | Browser/global and CommonJS selector requiring an explicit tier on every selection. |
| `build_visual_detail_variants_v1.py` | Deterministic builder for generated JSON, text map, and manifest. |
| `validate_visual_detail_variants_v1.py` | Source-integrity, taxonomy, tier, selector, safety, and manifest validator. |
| `asset_manifest_visual_detail_variants_v1.json` | Self-excluding byte/SHA-256 manifest for the eight resources above. |

The manifest excludes itself because embedding its own digest would be recursive. This pack contains no runtime geometry.

## Tier contract

Tier selection is always explicit; there is no default and no automatic viewer-state logic.

- `minimal`: the smallest reviewed, complete explanation. It may replace authored geometry with a native label, a reviewed silhouette/meaning-equivalent proxy, or no optional geometry when the policy permits. It remains a reversible presentation sidecar.
- `reduced80`: a semantic-density target of exactly `0.8`. This means approximately 80% of approved explanatory information, not 80% of polygons, draw calls, opacity, scale, medical severity, or source bytes. It remains a reversible presentation sidecar.
- `full`: binds the exact observed release USDZ path, byte count, and SHA-256, with no source or presentation mutation.

All tiers preserve the selected learning objective, material medical facts, warnings, laterality, registration, pathway, closure branch, and either the recognizable silhouette or a separately reviewed meaning-equivalent proxy. Lower tiers never change the source USDZ bytes; the host applies opaque visibility, label, motion, or component-selection sidecars and can restore `full` immediately.

Every category/tier policy has a structured `presentation_parameters` recipe. Numeric values are normalized to `0.0...1.0` and increase monotonically from `minimal` through `reduced80` to `full`:

- `semantic_density_target`
- `texture_resolution_scale`
- `secondary_detail_visibility_ratio`
- `label_density_ratio`
- `saturation_multiplier`
- `specular_multiplier`
- `motion_mode` and `motion_speed_multiplier`
- `particle_or_flow_mode` and `particle_or_flow_count_ratio`

These are presentation targets, not permission to mutate USDZ geometry. In particular, `BLOOD_FLOW_TEACHING/minimal` uses sparse static direction markers with no continuous cell animation; `BLOOD_FLOW_TEACHING/reduced80` uses reduced cell/flow density and slower motion; `full` remains source-authored. Categories without a relevant particle/flow layer use `none` for lower tiers.

## Exhaustive taxonomy

| Primary category | Assets | Simplification focus |
| --- | ---: | --- |
| `ANATOMY_CNS_MACRO` | 18 | Major CNS silhouette, selected structure, laterality, and atlas/generic status. |
| `ANATOMY_HEAD_NECK_SUPPORT` | 25 | Head, skull, meninges, nerves, support anatomy, and registered relationships. |
| `ANATOMY_VASCULAR` | 6 | Vessel class, route, direction, laterality, and conceptual color disclosure. |
| `PATHOLOGY_MACRO` | 6 | Non-graphic registered focus while retaining pathology type and uncertainty. |
| `BLOOD_FLOW_TEACHING` | 7 | Qualitative flow direction/state with no CFD or quantitative claim. |
| `MICRO_CONCEPTUAL` | 11 | Representative microscopic mechanism in a separate, explicitly magnified vignette. |
| `TOOLS_ENDOVASCULAR` | 19 | Detached category-level EVT tools with pathway and non-training warnings. |
| `TOOLS_OPEN_CRANIAL` | 16 | Detached category-level open tools with conditional pathway gates. |
| `OPEN_CRANIAL_ANATOMY_STATE` | 7 | Non-graphic, branch-correct access/closure state; forbidden in ordinary EVT. |
| `CLINICAL_CONTEXT` | 7 | Only essential generic context; no identity, readings, or operational cues. |
| `SPATIAL_ENVIRONMENT` | 9 | Optional room components; system passthrough/Simulator remains the baseline. |
| `GUIDANCE` | 1 | Current-step navigation with accessible native-control fallback. |
| `ADAPTIVE_PRESENTATION` | 1 | Replacement-only reviewed orientation presentation, never a stacked overlay. |
| `COMPOSITE_ASSEMBLY` | 17 | Unload assembly and choose domain-governed leaf components recursively. |

Total: 150 assets. Every release ID appears exactly once. Composite assemblies also receive an explicit domain override so their leaf assets follow anatomy, vessel, flow, microscopic, tool, environment, or mixed registered-head rules instead of a generic assembly rule.

## Browser use

Load the catalog, construct the selector, and pass the tier explicitly for every choice:

```html
<script src="visual_detail_selector_v1.js"></script>
<script>
fetch("visual_detail_variant_catalog_v1.json")
  .then(function (response) { return response.json(); })
  .then(function (catalog) {
    var selector = VisualDetailSelectorV1.createSelector(catalog);
    var binding = selector.select("brain_anatomy_realistic_v2", "reduced80");
    var recipe = binding.presentation_parameters;
    // The host resolves binding.source_usdz and applies the reviewed sidecar policy.
  });
</script>
```

`select(assetId, tier)` and `selectMany(assetIds, tier)` reject a missing or unknown tier. Each returned selection contains the resolved category/domain `presentation_parameters` and any assembly-domain recipe. The selector does not choose a tier, examine people, or authorize display. Those responsibilities remain outside this resource pack and must use an approved explicit control and review workflow.

## Runtime integration rules

1. Treat `source_usdz`, `source_usdz_bytes`, and `source_usdz_sha256` as an integrity triplet. Refuse a mismatched source rather than silently substituting it.
2. Keep source entities immutable. Implement `minimal` and `reduced80` as reversible host-side visibility, attachment, material-parameter, motion, or component-selection state.
3. Prefer opaque swaps and focused isolation over stacked transparency. Never convert reduced detail into hidden clinical facts.
4. Preserve persistent conceptual, nonquantitative, non-patient-specific, magnification, uncertainty, pathway, and scale disclosures in native RealityKit attachments or an equivalent accessible layer.
5. Never combine ordinary EVT with `TOOLS_OPEN_CRANIAL` or `OPEN_CRANIAL_ANATOMY_STATE`. Gate open surgery and EVD content independently and preserve craniotomy-replace versus craniectomy-leave-off closure logic.
6. Keep microscopic vignettes detached from the registered head and visibly marked as conceptual and magnified. Do not scale-match them to anatomy.
7. For `COMPOSITE_ASSEMBLY`, unload the complete assembly before loading selected leaf components. Do not co-load assembly and components or partially decimate an assembly in place.
8. Keep patient display blocked until every selected asset, sidecar recipe, attachment, pathway combination, accessibility mode, and performance profile has separate clinical, human-factors, legal, privacy, and platform review.

## Build and validation

Run from the repository root:

```sh
python3 RealityKitContent/InterfaceMedia/visual_detail_variants_v1/build_visual_detail_variants_v1.py
python3 RealityKitContent/InterfaceMedia/visual_detail_variants_v1/validate_visual_detail_variants_v1.py
```

The builder reads the 14 release manifests in a fixed order, observes every source USDZ byte count and SHA-256, fails on duplicate/unmapped IDs, writes the generated resources deterministically, and finally hashes the eight non-manifest pack resources. The validator independently checks all source bindings, 14 category counts, 17 assembly overrides, 150 assets, three variants per asset, 450 unique variants, exact `0.8` semantics, selector constraints, private-path absence, patient-display gates, and every manifested byte/SHA-256 pair.

Re-running the builder against unchanged sources and unchanged pack source files must produce byte-identical generated outputs and a byte-identical self-excluding manifest.
