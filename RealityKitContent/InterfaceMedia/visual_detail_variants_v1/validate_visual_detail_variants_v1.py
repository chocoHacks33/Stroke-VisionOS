#!/usr/bin/env python3
"""Validate the visual-detail virtual-variant pack and all source bindings."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


sys.dont_write_bytecode = True
PACK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACK_ROOT.parents[2]
sys.path.insert(0, str(PACK_ROOT))
import build_visual_detail_variants_v1 as build  # noqa: E402


EXPECTED_TIERS = ("minimal", "reduced80", "full")
EXPECTED_CATEGORY_COUNTS = {
    "ANATOMY_CNS_MACRO": 18,
    "ANATOMY_HEAD_NECK_SUPPORT": 25,
    "ANATOMY_VASCULAR": 6,
    "PATHOLOGY_MACRO": 6,
    "BLOOD_FLOW_TEACHING": 7,
    "MICRO_CONCEPTUAL": 11,
    "TOOLS_ENDOVASCULAR": 19,
    "TOOLS_OPEN_CRANIAL": 16,
    "OPEN_CRANIAL_ANATOMY_STATE": 7,
    "CLINICAL_CONTEXT": 7,
    "SPATIAL_ENVIRONMENT": 9,
    "GUIDANCE": 1,
    "ADAPTIVE_PRESENTATION": 1,
    "COMPOSITE_ASSEMBLY": 17,
}
EXPECTED_SOURCE_MANIFESTS = (
    "RealityKitContent/Assets/vision_pro_stroke_kit/asset_manifest.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_head_details_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_cranial_vascular_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_bloodflow_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_devices_v2.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_neural_detail_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_cranial_detail_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_intracranial_micro_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_endovascular_tools_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_open_cranial_tools_v3.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_adaptive_visuals_v1.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_spatial_care_environment_v1.json",
    "RealityKitContent/Assets/vision_pro_stroke_kit_v2/asset_manifest_figma_page2_surgical_states_v1.json",
)
EXPECTED_TAXONOMY_TEXT_SHA256 = "b0c4f275237f6214a30c50b37cc1f55acd37d1bee023f015c03b578d76619ce1"
EXPECTED_PACK_FILES = {
    "README.md",
    "VISUAL_DETAIL_ASSET_CATEGORIES.txt",
    "asset_manifest_visual_detail_variants_v1.json",
    "build_visual_detail_variants_v1.py",
    "validate_visual_detail_variants_v1.py",
    "visual_detail_category_policy_schema_v1.json",
    "visual_detail_category_policy_v1.json",
    "visual_detail_selector_v1.js",
    "visual_detail_variant_catalog_v1.json",
}
PRIVATE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "file" + "://",
    "/" + "var" + "/" + "folders" + "/",
    "C:" + "\\" + "Users" + "\\",
)
SELECTOR_FORBIDDEN_WORDS = (
    "anxiety", "biometric", "emotion", "gaze", "inference", "joint", "pupil", "sensor", "stress",
)
NUMERIC_PARAMETER_KEYS = (
    "semantic_density_target",
    "texture_resolution_scale",
    "secondary_detail_visibility_ratio",
    "label_density_ratio",
    "saturation_multiplier",
    "specular_multiplier",
    "motion_speed_multiplier",
    "particle_or_flow_count_ratio",
)
PARAMETER_KEYS = set(NUMERIC_PARAMETER_KEYS) | {"motion_mode", "particle_or_flow_mode"}
MOTION_MODES = {"static", "slowed", "source_authored"}
PARTICLE_OR_FLOW_MODES = {
    "none",
    "sparse_static_direction_markers",
    "reduced_direction_markers",
    "reduced_cells_and_flow",
    "representative_static_elements",
    "reduced_representative_elements",
    "source_authored",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def validate_parameter_block(parameters: Any, label: str) -> None:
    require(isinstance(parameters, dict), f"presentation parameters are not an object: {label}")
    require(set(parameters) == PARAMETER_KEYS, f"presentation parameter keys mismatch: {label}")
    for key in NUMERIC_PARAMETER_KEYS:
        value = parameters[key]
        require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{key} is not numeric: {label}")
        require(0.0 <= value <= 1.0, f"{key} is outside 0...1: {label}")
    require(parameters["motion_mode"] in MOTION_MODES, f"invalid motion_mode: {label}")
    require(parameters["particle_or_flow_mode"] in PARTICLE_OR_FLOW_MODES, f"invalid particle_or_flow_mode: {label}")
    if parameters["motion_mode"] == "static":
        require(parameters["motion_speed_multiplier"] == 0.0, f"static motion must have zero speed: {label}")
    elif parameters["motion_mode"] == "slowed":
        require(0.0 < parameters["motion_speed_multiplier"] < 1.0, f"slowed motion speed must be between zero and one: {label}")
    else:
        require(parameters["motion_speed_multiplier"] == 1.0, f"source-authored motion speed must equal one: {label}")
    if parameters["particle_or_flow_mode"] == "none":
        require(parameters["particle_or_flow_count_ratio"] == 0.0, f"none particle mode must have zero count: {label}")
    elif parameters["particle_or_flow_mode"] == "source_authored":
        require(parameters["particle_or_flow_count_ratio"] == 1.0, f"source-authored particle count must equal one: {label}")
    else:
        require(0.0 < parameters["particle_or_flow_count_ratio"] < 1.0, f"reduced particle/flow count must be between zero and one: {label}")


def validate_source_release() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    require(tuple(build.SOURCE_MANIFESTS) == EXPECTED_SOURCE_MANIFESTS, "builder source-manifest order drifted")
    records = build.load_release_assets()
    require(len(records) == 150, f"expected 150 release assets, observed {len(records)}")

    ids = [record["asset_id"] for record in records]
    require(len(set(ids)) == 150, "release asset IDs are not unique")
    observed: dict[str, dict[str, Any]] = {}
    for release_index, record in enumerate(records):
        asset_id = record["asset_id"]
        require(record["source_manifest"] in EXPECTED_SOURCE_MANIFESTS, f"unknown source manifest for {asset_id}")
        require(record["source_manifest_index"] == EXPECTED_SOURCE_MANIFESTS.index(record["source_manifest"]), f"source manifest index mismatch for {asset_id}")
        source_relative = Path(record["source_usdz"])
        require(not source_relative.is_absolute() and ".." not in source_relative.parts, f"non-relative source path for {asset_id}")
        require(source_relative.suffix.lower() == ".usdz", f"non-USDZ source for {asset_id}")
        source_path = REPO_ROOT / source_relative
        require(source_path.is_file(), f"missing source USDZ for {asset_id}")
        require(source_path.stat().st_size == record["source_usdz_bytes"], f"source byte mismatch for {asset_id}")
        require(sha256_file(source_path) == record["source_usdz_sha256"], f"source SHA mismatch for {asset_id}")
        require(re.fullmatch(r"[0-9a-f]{64}", record["source_usdz_sha256"]) is not None, f"invalid source SHA for {asset_id}")
        observed[asset_id] = {**record, "release_index": release_index}
    return records, observed


def parse_taxonomy_text(text: str) -> tuple[dict[str, str], dict[str, str]]:
    category_for: dict[str, str] = {}
    overrides: dict[str, str] = {}
    current: str | None = None
    heading_pattern = re.compile(r"^\[([A-Z0-9_]+)\] count=(\d+)$")
    declared_counts: dict[str, int] = {}

    for line in text.splitlines():
        heading = heading_pattern.match(line)
        if heading:
            current = heading.group(1)
            declared_counts[current] = int(heading.group(2))
            continue
        if not line or "=" in line and current is None:
            continue
        if current == "ASSEMBLY_DOMAIN_OVERRIDES":
            if "=" in line:
                asset_id, domain = line.split("=", 1)
                require(asset_id not in overrides, f"duplicate assembly override for {asset_id}")
                overrides[asset_id] = domain
            continue
        if current in EXPECTED_CATEGORY_COUNTS:
            require("=" not in line, f"malformed category member line: {line}")
            require(line not in category_for, f"duplicate category membership for {line}")
            category_for[line] = current

    require(set(declared_counts) == set(EXPECTED_CATEGORY_COUNTS) | {"ASSEMBLY_DOMAIN_OVERRIDES"}, "taxonomy headings are incomplete or extra")
    for category, count in EXPECTED_CATEGORY_COUNTS.items():
        require(declared_counts[category] == count, f"declared count mismatch for {category}")
        require(sum(value == category for value in category_for.values()) == count, f"member count mismatch for {category}")
    require(declared_counts["ASSEMBLY_DOMAIN_OVERRIDES"] == 17, "assembly override declared count is not 17")
    require(len(category_for) == 150, f"taxonomy has {len(category_for)} members, expected 150")
    require(len(overrides) == 17, f"taxonomy has {len(overrides)} assembly overrides, expected 17")
    return category_for, overrides


def validate_taxonomy(release_records: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    path = PACK_ROOT / "VISUAL_DETAIL_ASSET_CATEGORIES.txt"
    text = path.read_text(encoding="utf-8")
    require(hashlib.sha256(text.encode("utf-8")).hexdigest() == EXPECTED_TAXONOMY_TEXT_SHA256, "taxonomy mapping fingerprint drifted")
    require(text == build.render_category_text(), "taxonomy text is not the deterministic builder output")
    category_for, overrides = parse_taxonomy_text(text)
    release_ids = {record["asset_id"] for record in release_records}
    require(set(category_for) == release_ids, "taxonomy does not cover all and only release IDs")
    require(set(overrides) == {asset_id for asset_id, category in category_for.items() if category == "COMPOSITE_ASSEMBLY"}, "assembly overrides do not cover all and only composite assemblies")
    require(overrides == build.ASSEMBLY_DOMAINS, "assembly-domain override mapping drifted")
    return category_for, overrides


def validate_policy() -> None:
    policy_path = PACK_ROOT / "visual_detail_category_policy_v1.json"
    schema_path = PACK_ROOT / "visual_detail_category_policy_schema_v1.json"
    policy = load_json(policy_path)
    schema = load_json(schema_path)

    require(policy_path.read_text(encoding="utf-8") == canonical_json_text(build.build_policy_document()), "policy JSON is not canonical deterministic output")
    require(schema_path.read_text(encoding="utf-8") == canonical_json_text(build.build_policy_schema()), "policy schema JSON is not canonical deterministic output")
    require(policy["patient_display_authorized"] is False, "policy must keep patient display disabled")
    require(tuple(policy["tier_order"]) == EXPECTED_TIERS, "policy tier order mismatch")
    require(policy["tier_semantics"]["reduced80"]["semantic_density_target"] == 0.8, "reduced80 policy target must equal 0.8")
    require(policy["tier_semantics"]["full"]["source_asset_unchanged"] is True, "full policy must preserve source")
    require(policy["category_count"] == 14 and len(policy["categories"]) == 14, "policy category count mismatch")
    require({entry["category_id"]: entry["asset_count"] for entry in policy["categories"]} == EXPECTED_CATEGORY_COUNTS, "policy category counts mismatch")
    require(len(policy["assembly_domain_overrides"]) == 17, "policy assembly override count mismatch")
    require(policy["presentation_parameter_contract"]["reduced80_semantic_density_target"] == 0.8, "parameter contract reduced80 target mismatch")
    require(policy["presentation_parameter_contract"]["numeric_monotonic_order"] == "minimal <= reduced80 <= full", "parameter monotonic contract mismatch")
    require(schema["properties"]["patient_display_authorized"]["const"] is False, "schema patient-display gate mismatch")
    require(schema["properties"]["tier_order"]["const"] == list(EXPECTED_TIERS), "schema tier constant mismatch")
    require(schema["properties"]["category_count"]["const"] == 14, "schema category constant mismatch")

    parameter_block_count = 0
    categories = {entry["category_id"]: entry for entry in policy["categories"]}
    for category in EXPECTED_CATEGORY_COUNTS:
        tier_blocks = categories[category]["tiers"]
        require(set(tier_blocks) == set(EXPECTED_TIERS), f"tier policy coverage mismatch for {category}")
        for tier in EXPECTED_TIERS:
            block = tier_blocks[tier]
            require(block["geometry_mutation_allowed"] is False, f"geometry mutation enabled in {category}/{tier}")
            validate_parameter_block(block["presentation_parameters"], f"policy:{category}/{tier}")
            parameter_block_count += 1
        for key in NUMERIC_PARAMETER_KEYS:
            values = [tier_blocks[tier]["presentation_parameters"][key] for tier in EXPECTED_TIERS]
            require(values[0] <= values[1] <= values[2], f"non-monotonic {key} in {category}: {values}")
        require(tier_blocks["reduced80"]["presentation_parameters"]["semantic_density_target"] == 0.8, f"reduced80 semantic density mismatch in {category}")
        full = tier_blocks["full"]["presentation_parameters"]
        require(all(full[key] == 1.0 for key in NUMERIC_PARAMETER_KEYS), f"full numeric parameters are not source-authored in {category}")
        require(full["motion_mode"] == "source_authored" and full["particle_or_flow_mode"] == "source_authored", f"full modes are not source-authored in {category}")
    require(parameter_block_count == 42, f"expected 42 category/tier parameter blocks, observed {parameter_block_count}")

    blood = categories["BLOOD_FLOW_TEACHING"]["tiers"]
    require(blood["minimal"]["presentation_parameters"]["motion_mode"] == "static", "blood-flow minimal must be static")
    require(blood["minimal"]["presentation_parameters"]["motion_speed_multiplier"] == 0.0, "blood-flow minimal speed must be zero")
    require(blood["minimal"]["presentation_parameters"]["particle_or_flow_mode"] == "sparse_static_direction_markers", "blood-flow minimal must use sparse static direction markers")
    require(blood["reduced80"]["presentation_parameters"]["motion_mode"] == "slowed", "blood-flow reduced80 must use slowed motion")
    require(blood["reduced80"]["presentation_parameters"]["particle_or_flow_mode"] == "reduced_cells_and_flow", "blood-flow reduced80 must reduce cells and flow")
    require(blood["full"]["presentation_parameters"]["motion_mode"] == "source_authored", "blood-flow full must remain source-authored")

    joined_policy = json.dumps(policy, sort_keys=True).lower()
    for phrase in ("material medical facts", "laterality", "registration", "ordinary evt", "assembly/component exclusion"):
        require(phrase in joined_policy, f"policy missing required rule: {phrase}")


def validate_catalog(
    release_records: list[dict[str, Any]],
    observed_sources: dict[str, dict[str, Any]],
    category_for: dict[str, str],
    overrides: dict[str, str],
) -> None:
    catalog_path = PACK_ROOT / "visual_detail_variant_catalog_v1.json"
    catalog = load_json(catalog_path)
    expected = build.build_catalog(release_records, build.validate_taxonomy(release_records))
    require(catalog_path.read_text(encoding="utf-8") == canonical_json_text(expected), "catalog JSON is not canonical deterministic output")

    require(catalog["patient_display_authorized"] is False, "catalog must keep patient display disabled")
    require(catalog["source_release_manifest_count"] == 14, "catalog source manifest count mismatch")
    require(catalog["source_release_asset_count"] == 150, "catalog asset count mismatch")
    require(catalog["category_count"] == 14, "catalog category count mismatch")
    require(catalog["category_counts"] == EXPECTED_CATEGORY_COUNTS, "catalog category counts mismatch")
    require(catalog["tier_count"] == 3 and tuple(catalog["tier_order"]) == EXPECTED_TIERS, "catalog tier contract mismatch")
    require(catalog["virtual_variant_count"] == 450, "catalog virtual variant count mismatch")
    require(catalog["runtime_geometry_included"] is False, "catalog must not include runtime geometry")
    require(catalog["source_geometry_mutation_allowed"] is False, "catalog must forbid source geometry mutation")
    require(len(catalog["assets"]) == 150 and len(catalog["variants"]) == 450, "catalog array counts mismatch")

    release_order = [record["asset_id"] for record in release_records]
    require([asset["asset_id"] for asset in catalog["assets"]] == release_order, "catalog asset order drifted from release-manifest order")
    asset_by_id: dict[str, dict[str, Any]] = {}
    policy = load_json(PACK_ROOT / "visual_detail_category_policy_v1.json")
    policy_by_category = {entry["category_id"]: entry for entry in policy["categories"]}
    for asset in catalog["assets"]:
        asset_id = asset["asset_id"]
        require(asset_id not in asset_by_id, f"duplicate catalog asset {asset_id}")
        asset_by_id[asset_id] = asset
        source = observed_sources[asset_id]
        for field in ("source_manifest", "source_manifest_index", "source_asset_index", "source_usdz", "source_usdz_bytes", "source_usdz_sha256"):
            require(asset[field] == source[field], f"catalog source field {field} mismatch for {asset_id}")
        require(asset["primary_category"] == category_for[asset_id], f"catalog category mismatch for {asset_id}")
        expected_kind = "assembly" if category_for[asset_id] == "COMPOSITE_ASSEMBLY" else "component"
        require(asset["composition_kind"] == expected_kind, f"composition kind mismatch for {asset_id}")
        require(asset["assembly_domain"] == overrides.get(asset_id), f"assembly domain mismatch for {asset_id}")
        expected_parameter_category = overrides.get(asset_id)
        if expected_parameter_category not in EXPECTED_CATEGORY_COUNTS:
            expected_parameter_category = category_for[asset_id]
        require(asset["parameter_policy_category"] == expected_parameter_category, f"parameter policy category mismatch for {asset_id}")
        require(asset["variant_ids"] == [f"{asset_id}::{tier}" for tier in EXPECTED_TIERS], f"variant references mismatch for {asset_id}")

    variant_by_id: dict[str, dict[str, Any]] = {}
    tiers_by_asset: dict[str, list[str]] = defaultdict(list)
    for variant in catalog["variants"]:
        variant_id = variant["variant_id"]
        require(variant_id not in variant_by_id, f"duplicate variant {variant_id}")
        variant_by_id[variant_id] = variant
        asset_id = variant["asset_id"]
        tier = variant["tier"]
        require(asset_id in observed_sources, f"variant references unknown asset {asset_id}")
        require(tier in EXPECTED_TIERS, f"unknown tier {tier}")
        require(variant_id == f"{asset_id}::{tier}", f"variant ID mismatch for {variant_id}")
        tiers_by_asset[asset_id].append(tier)
        source = observed_sources[asset_id]
        require(variant["source_usdz"] == source["source_usdz"], f"variant source path mismatch for {variant_id}")
        require(variant["source_usdz_bytes"] == source["source_usdz_bytes"], f"variant source bytes mismatch for {variant_id}")
        require(variant["source_usdz_sha256"] == source["source_usdz_sha256"], f"variant source SHA mismatch for {variant_id}")
        require(variant["category_id"] == category_for[asset_id], f"variant category mismatch for {variant_id}")
        expected_parameter_category = asset_by_id[asset_id]["parameter_policy_category"]
        require(variant["parameter_policy_category"] == expected_parameter_category, f"variant parameter policy category mismatch for {variant_id}")
        expected_parameters = policy_by_category[expected_parameter_category]["tiers"][tier]["presentation_parameters"]
        require(variant["presentation_parameters"] == expected_parameters, f"variant presentation recipe mismatch for {variant_id}")
        validate_parameter_block(variant["presentation_parameters"], f"catalog:{variant_id}")
        require(variant["patient_display_authorized"] is False, f"patient display enabled for {variant_id}")
        require(variant["preserve_silhouette_or_meaning"] is True, f"silhouette/meaning preservation disabled for {variant_id}")
        require(variant["preserve_medical_facts_and_warnings"] is True, f"fact/warning preservation disabled for {variant_id}")
        require(variant["geometry_mutation_allowed"] is False, f"geometry mutation enabled for {variant_id}")
        require(variant["source_asset_unchanged"] is True, f"source mutation implied for {variant_id}")
        if category_for[asset_id] == "COMPOSITE_ASSEMBLY":
            resolution = variant.get("assembly_resolution")
            require(isinstance(resolution, dict), f"assembly resolution missing for {variant_id}")
            require(resolution["assembly_domain"] == overrides[asset_id], f"assembly resolution domain mismatch for {variant_id}")
            expected_action = "bind_exact_source_assembly" if tier == "full" else "unload_assembly_then_select_leaf_components"
            require(resolution["action"] == expected_action, f"assembly action mismatch for {variant_id}")
            expected_leaf_resolution = "per_leaf_primary_category" if overrides[asset_id] == "MIXED_REGISTERED_HEAD" else "fixed_assembly_domain_category"
            require(resolution["leaf_parameter_resolution"] == expected_leaf_resolution, f"assembly leaf resolution mismatch for {variant_id}")
            expected_controls = policy_by_category["COMPOSITE_ASSEMBLY"]["tiers"][tier]["presentation_parameters"]
            require(resolution["assembly_control_parameters"] == expected_controls, f"assembly control recipe mismatch for {variant_id}")
            validate_parameter_block(resolution["assembly_control_parameters"], f"assembly:{variant_id}")
        else:
            require("assembly_resolution" not in variant, f"component has assembly resolution: {variant_id}")
        if tier == "full":
            require(variant["binds_exact_observed_source_as_presentation"] is True, f"full binding disabled for {variant_id}")
            require(variant["virtual_reversible_sidecar"] is False, f"full incorrectly marked as sidecar for {variant_id}")
            require("semantic_density_target" not in variant and "semantic_density" not in variant, f"full has density override for {variant_id}")
        elif tier == "reduced80":
            require(variant["binds_exact_observed_source_as_presentation"] is False, f"reduced80 incorrectly marked full for {variant_id}")
            require(variant["virtual_reversible_sidecar"] is True, f"reduced80 sidecar disabled for {variant_id}")
            target = variant.get("semantic_density_target")
            require(isinstance(target, (int, float)) and not isinstance(target, bool) and target == 0.8, f"reduced80 target mismatch for {variant_id}")
        else:
            require(variant["binds_exact_observed_source_as_presentation"] is False, f"minimal incorrectly marked full for {variant_id}")
            require(variant["virtual_reversible_sidecar"] is True, f"minimal sidecar disabled for {variant_id}")
            require(variant.get("semantic_density") == "smallest_reviewed_complete_explanation", f"minimal semantic contract mismatch for {variant_id}")

    require(len(variant_by_id) == 450, "variant IDs are not exactly 450 unique values")
    require(set(tiers_by_asset) == set(release_order), "variant asset coverage mismatch")
    for asset_id in release_order:
        require(tiers_by_asset[asset_id] == list(EXPECTED_TIERS), f"asset does not have exactly three ordered tiers: {asset_id}")
    require(Counter(variant["tier"] for variant in catalog["variants"]) == Counter({tier: 150 for tier in EXPECTED_TIERS}), "tier totals are not 150 each")


def validate_selector() -> None:
    selector = (PACK_ROOT / "visual_detail_selector_v1.js").read_text(encoding="utf-8")
    for marker in ("VisualDetailSelectorV1", "module.exports", "globalThis", "createSelector", "selectMany", "tier is required explicitly", "presentation_parameters"):
        require(marker in selector, f"selector missing UMD/API marker: {marker}")
    require('["minimal", "reduced80", "full"]' in selector, "selector tier list mismatch")
    require("function select(assetId, tier)" in selector, "selector does not require a tier argument")
    require("function selectMany(assetIds, tier)" in selector, "multi-selector does not require a tier argument")
    require(re.search(r"\btier\s*=", selector) is None, "selector contains a tier default or reassignment")
    lower = selector.lower()
    for word in SELECTOR_FORBIDDEN_WORDS:
        require(re.search(rf"\b{re.escape(word)}\b", lower) is None, f"selector contains forbidden automatic-state term: {word}")
    require("import " not in selector and "export " not in selector, "selector is not a classic browser/UMD script")


def validate_private_paths_and_file_set() -> None:
    files = {path.name for path in PACK_ROOT.iterdir() if path.is_file() and not path.name.startswith(".")}
    require(files == EXPECTED_PACK_FILES, f"pack file set mismatch; missing={sorted(EXPECTED_PACK_FILES-files)}, extra={sorted(files-EXPECTED_PACK_FILES)}")
    for path in sorted(PACK_ROOT.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        text = path.read_text(encoding="utf-8")
        for marker in PRIVATE_PATH_MARKERS:
            require(marker not in text, f"private path marker {marker!r} found in {path.name}")


def validate_manifest() -> dict[str, Any]:
    path = PACK_ROOT / "asset_manifest_visual_detail_variants_v1.json"
    manifest = load_json(path)
    require(path.read_text(encoding="utf-8") == canonical_json_text(build.build_manifest()), "pack manifest is not canonical deterministic output")
    require(manifest["manifest_self_hash_policy"] == "This manifest excludes itself because a self-hash is recursive.", "manifest self-exclusion policy mismatch")
    require(manifest["patient_display_authorized"] is False, "manifest must keep patient display disabled")
    require(manifest["asset_count"] == 150, "manifest asset count mismatch")
    require(manifest["tier_count"] == 3 and manifest["tiers"] == list(EXPECTED_TIERS), "manifest tier contract mismatch")
    require(manifest["virtual_variant_count"] == 450, "manifest variant count mismatch")
    require(manifest["reduced80_semantic_density_target"] == 0.8, "manifest reduced80 target mismatch")
    require(manifest["runtime_geometry_included"] is False, "manifest incorrectly advertises runtime geometry")
    require(manifest["resource_count"] == 8 and len(manifest["resources"]) == 8, "manifest resource count mismatch")

    expected_resources = set(EXPECTED_PACK_FILES) - {path.name}
    observed_resources = {resource["path"] for resource in manifest["resources"]}
    require(observed_resources == expected_resources, "manifest must index all and only eight non-manifest resources")
    require(path.name not in observed_resources, "manifest includes itself")
    for resource in manifest["resources"]:
        relative = Path(resource["path"])
        require(not relative.is_absolute() and len(relative.parts) == 1, f"invalid resource path {resource['path']}")
        resource_path = PACK_ROOT / relative
        require(resource_path.stat().st_size == resource["bytes"], f"manifest byte mismatch for {resource['path']}")
        require(sha256_file(resource_path) == resource["sha256"], f"manifest SHA mismatch for {resource['path']}")
        require(re.fullmatch(r"[0-9a-f]{64}", resource["sha256"]) is not None, f"invalid manifest SHA for {resource['path']}")
    return manifest


def main() -> None:
    validate_private_paths_and_file_set()
    release_records, observed_sources = validate_source_release()
    category_for, overrides = validate_taxonomy(release_records)
    validate_policy()
    validate_catalog(release_records, observed_sources, category_for, overrides)
    validate_selector()
    manifest = validate_manifest()
    print("VALIDATION PASS")
    print("release_manifests=14 release_assets=150 unique_asset_ids=150")
    print("categories=14 assembly_domain_overrides=17")
    print("tiers=3 tier_counts=minimal:150,reduced80:150,full:150 virtual_variants=450")
    print("source_usdz_integrity=150/150 full_exact_bindings=150/150 lower_virtual_sidecars=300/300")
    print("patient_display_authorized=false runtime_geometry_included=false")
    print(f"manifest_resources={manifest['resource_count']} manifest_sha256={sha256_file(PACK_ROOT / 'asset_manifest_visual_detail_variants_v1.json')}")


if __name__ == "__main__":
    main()
